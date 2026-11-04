import asyncio
import builtins
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import httpx

from octotools.models.executor import Executor
from octotools.models.initializer import Initializer
from octotools.tools.parallel_search.tool import (
    MCP_URL,
    USER_AGENT,
    Parallel_Search_Tool,
)


class ParallelSearchTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.calls = []
        self.result = {
            "content": [
                {
                    "type": "text",
                    "text": "Python documentation: https://docs.python.org/3/",
                }
            ],
            "structuredContent": {"results": [{"url": "https://docs.python.org/3/"}]},
            "isError": False,
        }

    def respond(self, request):
        self.requests.append(request)
        if request.method == "GET":
            return httpx.Response(405)
        message = json.loads(request.content)
        if "id" not in message:
            return httpx.Response(202)
        if message["method"] == "initialize":
            result = {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fixture", "version": "1"},
            }
        elif message["method"] == "tools/call":
            self.calls.append(message["params"])
            result = self.result
        elif message["method"] == "tools/list":
            result = {
                "tools": [
                    {"name": name, "inputSchema": {"type": "object"}}
                    for name in ("web_search", "web_fetch")
                ]
            }
        else:
            raise AssertionError(f"Unexpected method: {message['method']}")
        return httpx.Response(
            200, json={"jsonrpc": "2.0", "id": message["id"], "result": result}
        )

    def transport(self):
        client_class = httpx.AsyncClient

        def create(**kwargs):
            return client_class(transport=httpx.MockTransport(self.respond), **kwargs)

        return patch("httpx.AsyncClient", side_effect=create)

    def test_sdk_search_and_fetch_requests_and_results(self):
        tool = Parallel_Search_Tool()
        with self.transport():
            search = tool.execute(
                objective="Python docs",
                search_queries=["Python official documentation"],
            )
            fetch = tool.execute(urls=["https://docs.python.org/3/"])
        self.assertFalse(search.get("error"), search)
        self.assertEqual(search["structuredContent"], self.result["structuredContent"])
        self.assertEqual(fetch["content"], self.result["content"])
        self.assertEqual(
            [call["name"] for call in self.calls], ["web_search", "web_fetch"]
        )
        self.assertEqual(
            self.calls[0]["arguments"]["search_queries"],
            ["Python official documentation"],
        )
        self.assertEqual(
            self.calls[1]["arguments"]["urls"], ["https://docs.python.org/3/"]
        )
        self.assertEqual(
            self.calls[0]["arguments"]["session_id"],
            self.calls[1]["arguments"]["session_id"],
        )
        for request in self.requests:
            self.assertEqual(str(request.url), MCP_URL)
            self.assertEqual(request.headers["user-agent"], USER_AGENT)
            self.assertNotIn("authorization", request.headers)
        self.assertGreaterEqual(len(self.requests), 6)

    def test_explicit_session_is_preserved_without_model_guess(self):
        with self.transport():
            result = Parallel_Search_Tool().execute(
                objective="Python docs",
                search_queries=["Python docs"],
                session_id="conversation-123",
            )
        self.assertFalse(result.get("error"), result)
        arguments = self.calls[0]["arguments"]
        self.assertEqual(arguments["session_id"], "conversation-123")
        self.assertNotIn("model_name", arguments)

    def test_server_tool_error_is_preserved(self):
        self.result = {
            "content": [{"type": "text", "text": "Unable to fetch"}],
            "isError": True,
        }
        with self.transport():
            result = Parallel_Search_Tool().execute(urls=["https://example.com"])
        self.assertTrue(result["isError"])
        self.assertEqual(result["content"][0]["text"], "Unable to fetch")

    def test_invalid_arguments_make_no_request(self):
        cases = [
            {},
            {"search_queries": ["query"]},
            {"objective": "docs", "search_queries": []},
            {"objective": "docs", "search_queries": "query"},
            {"objective": "docs", "search_queries": [""]},
            {"urls": ["file:///etc/passwd"]},
            {"urls": ["https://example.com"] * 21},
            {"urls": ["https://example.com"], "objective": "x" * 201},
            {"urls": ["https://example.com"], "search_queries": ["query"]},
            {"urls": ["https://example.com"], "session_id": "x" * 101},
            {"urls": ["https://example.com"], "session_id": ""},
        ]
        with self.transport():
            for arguments in cases:
                with self.subTest(arguments=arguments):
                    self.assertIn("error", Parallel_Search_Tool().execute(**arguments))
        self.assertEqual(self.requests, [])

    def test_total_timeout_cancels_operation(self):
        cancelled = []

        async def slow_call(*args):
            try:
                await asyncio.sleep(10)
            finally:
                cancelled.append(True)

        tool = Parallel_Search_Tool(timeout=0.01)
        with patch.object(tool, "_call", side_effect=slow_call):
            result = tool.execute(urls=["https://example.com"])
        self.assertIn("timed out", result["error"])
        self.assertEqual(cancelled, [True])

    def test_invalid_timeout(self):
        for timeout in (0, -1, float("inf"), float("nan"), "60"):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                Parallel_Search_Tool(timeout=timeout)

    def test_missing_sdk_prevents_registration_and_explains_installation(self):
        original = builtins.__import__

        def without_mcp(name, *args, **kwargs):
            if name == "mcp":
                raise ImportError("mcp not installed")
            return original(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=without_mcp):
            with self.assertRaisesRegex(ImportError, "parallel-search"):
                Parallel_Search_Tool()

            # Isolate discovery from unrelated tools and their dependencies.
            tool_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "octotools", "tools", "parallel_search",
            )
            with patch(
                "octotools.models.initializer.os.walk",
                return_value=[(tool_dir, [], ["tool.py"])],
            ), self.transport():
                for enabled_tools in (["all"], ["Parallel_Search_Tool"]):
                    with self.subTest(enabled_tools=enabled_tools):
                        selected = Initializer(
                            enabled_tools=enabled_tools, model_string="gpt-4o"
                        )
                        self.assertNotIn("Parallel_Search_Tool", selected.available_tools)
                        self.assertNotIn("Parallel_Search_Tool", selected.toolbox_metadata)
        self.assertEqual(self.requests, [])

    def test_active_event_loop_returns_clear_error(self):
        async def run():
            return Parallel_Search_Tool().execute(urls=["https://example.com"])

        self.assertIn("event loop", asyncio.run(run())["error"])

    def test_initializer_selection_and_default(self):
        with self.transport():
            selected = Initializer(
                enabled_tools=["Parallel_Search_Tool"], model_string="gpt-4o"
            )
            self.assertEqual(selected.available_tools, ["Parallel_Search_Tool"])
            self.assertEqual(
                selected.tool_directory_mapping["Parallel_Search_Tool"],
                "parallel_search",
            )
            self.assertFalse(
                selected.toolbox_metadata["Parallel_Search_Tool"]["require_llm_engine"]
            )
            default = Initializer(model_string="gpt-4o")
            self.assertEqual(default.available_tools, [])
            self.assertEqual(default.enabled_tools, [])
        self.assertEqual(self.requests, [])

    def test_transport_failure_returns_error(self):
        def unavailable(request):
            raise httpx.ConnectError("fixture unavailable", request=request)

        self.respond = unavailable
        with self.transport():
            result = Parallel_Search_Tool().execute(urls=["https://example.com"])
        self.assertIn("error", result)
        self.assertIn("fixture unavailable", result["error"])

    def test_executor_dispatches_selected_native_tool(self):
        selected = Initializer(
            enabled_tools=["Parallel_Search_Tool"], model_string="gpt-4o"
        )
        with tempfile.TemporaryDirectory() as cache_dir, self.transport():
            executor = Executor(
                llm_engine_name="gpt-4o", available_tools=selected.available_tools
            )
            executor.set_query_cache_dir(cache_dir)
            results = executor.execute_tool_command(
                selected.available_tools[0],
                json.dumps([{
                    "objective": "Python docs",
                    "search_queries": ["Python official documentation"],
                    "session_id": "executor-conversation",
                }]),
            )
        self.assertIsInstance(results, list, results)
        self.assertEqual(
            results[0]["structuredContent"], self.result["structuredContent"]
        )
        self.assertEqual(
            self.calls[0]["arguments"]["session_id"], "executor-conversation"
        )


if __name__ == "__main__":
    unittest.main()
