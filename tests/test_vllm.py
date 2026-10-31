import base64
import builtins
import io
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import httpx
from openai import OpenAI
from PIL import Image

from octotools import solver as solver_module
from octotools.engine.factory import create_llm_engine
from octotools.models.initializer import Initializer
from tasks import solve as task_module


MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"


class OptionalVLLMTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(redirect_stdout(io.StringIO()))
        self.stack.enter_context(patch.object(sys, "path", sys.path.copy()))
        self.stack.enter_context(patch("platform.platform", return_value="test-platform"))
        self.stack.enter_context(patch.dict(sys.modules))
        sys.modules.pop("octotools.engine.vllm", None)
        original_import = builtins.__import__

        def without_vllm(name, globals=None, locals=None, fromlist=(), level=0):
            if level == 0 and (name == "vllm" or name.startswith("vllm.")):
                raise ImportError("vllm is not installed")
            return original_import(name, globals, locals, fromlist, level)

        self.stack.enter_context(patch("builtins.__import__", side_effect=without_vllm))
        self.requests = []

        def respond(request):
            self.requests.append(request)
            if request.method == "GET" and request.url.path == "/v1/models":
                return httpx.Response(200, json={
                    "object": "list",
                    "data": [{"id": MODEL, "object": "model", "created": 0,
                              "owned_by": "vllm"}],
                })
            if request.method == "POST" and request.url.path == "/v1/chat/completions":
                return httpx.Response(200, json={
                    "id": "chat-test", "object": "chat.completion", "created": 0,
                    "model": MODEL,
                    "choices": [{"index": 0, "finish_reason": "stop",
                                 "message": {"role": "assistant", "content": "Test answer"}}],
                })
            raise AssertionError(f"Unexpected request: {request.method} {request.url}")

        def create_client(**kwargs):
            client = OpenAI(http_client=httpx.Client(transport=httpx.MockTransport(respond)),
                            **kwargs)
            self.addCleanup(client.close)
            return client

        self.stack.enter_context(patch("openai.OpenAI", side_effect=create_client))

    def test_factory_sends_text_and_images_without_vllm_installed(self):
        engine = create_llm_engine(f"vllm-{MODEL}")
        self.assertEqual(engine.generate("Hello", max_tokens=17), "Test answer")
        image_bytes = b"image bytes supplied by the caller"
        self.assertEqual(engine.generate(["Describe this", image_bytes]), "Test answer")

        self.assertEqual([request.method for request in self.requests], ["GET", "POST", "POST"])
        for request in self.requests:
            self.assertEqual(request.url.host, "localhost")
            self.assertEqual(request.url.port, 8888)
            self.assertEqual(request.headers["authorization"], "Bearer dummy-token")
        text_body = json.loads(self.requests[1].content)
        self.assertEqual(text_body["model"], MODEL)
        self.assertEqual(text_body["max_tokens"], 17)
        self.assertEqual(text_body["messages"][1], {"role": "user", "content": "Hello"})
        image_body = json.loads(self.requests[2].content)
        self.assertEqual(image_body["messages"][1]["content"], [
            {"type": "text", "text": "Describe this"},
            {"type": "image_url", "image_url": {
                "url": "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("utf-8")}},
        ])

    def test_external_solver_runs_image_query_without_starting_a_process(self):
        with tempfile.TemporaryDirectory() as directory, patch("subprocess.Popen") as spawn:
            image_path = Path(directory) / "image.png"
            Image.new("RGB", (1, 1), "white").save(image_path)
            solver = solver_module.construct_solver(
                llm_engine_name=f"vllm-{MODEL}", enabled_tools=[], output_types="base",
                root_cache_dir=directory, verbose=False, start_vllm_server=False,
            )
            result = solver.solve("What is in this image?", image_path=str(image_path))
            self.assertEqual(result["base_response"], "Test answer")
            spawn.assert_not_called()
            body = json.loads(self.requests[-1].content)
            image_url = body["messages"][1]["content"][1]["image_url"]["url"]
            self.assertEqual(base64.b64decode(image_url.split(",", 1)[1]), image_path.read_bytes())

    def test_initializer_keeps_automatic_start_as_default(self):
        with patch.object(Initializer, "_set_up_tools"), \
                patch.object(Initializer, "setup_vllm_server") as start:
            Initializer(model_string=f"vllm-{MODEL}")
            start.assert_called_once_with()

    def test_external_initializer_skips_server_setup(self):
        with patch.object(Initializer, "_set_up_tools"), \
                patch.object(Initializer, "setup_vllm_server") as start, \
                patch("subprocess.Popen") as spawn:
            initializer = Initializer(model_string=f"vllm-{MODEL}", start_vllm_server=False)
            self.assertIsNone(initializer.vllm_server_process)
            start.assert_not_called()
            spawn.assert_not_called()

    def test_other_models_do_not_start_vllm(self):
        with patch.object(Initializer, "_set_up_tools"), \
                patch.object(Initializer, "setup_vllm_server") as start:
            for auto_start in (True, False):
                with self.subTest(auto_start=auto_start):
                    Initializer(model_string="gpt-4o", start_vllm_server=auto_start)
            start.assert_not_called()

    def test_missing_vllm_default_explains_external_server_option(self):
        with patch.object(Initializer, "_set_up_tools"), patch("subprocess.Popen") as spawn:
            with self.assertRaisesRegex(ImportError, "start_vllm_server=False"):
                Initializer(model_string=f"vllm-{MODEL}")
            spawn.assert_not_called()

    def test_construct_solver_preserves_default_startup(self):
        with patch.object(Initializer, "_set_up_tools"), \
                patch.object(Initializer, "setup_vllm_server") as start, \
                patch.object(solver_module, "Planner"):
            solver_module.construct_solver(llm_engine_name=f"vllm-{MODEL}", enabled_tools=[])
            start.assert_called_once_with()

    def test_both_cli_entrypoints_forward_default_and_external_mode(self):
        for module in (solver_module, task_module):
            for flags, expected_start in (([], True), (["--no-start-vllm-server"], False)):
                with self.subTest(module=module.__name__, flags=flags), \
                        patch.object(sys, "argv", ["solve", "--llm_engine_name", f"vllm-{MODEL}",
                                                   "--enabled_tools", ""] + flags), \
                        patch.object(Initializer, "_set_up_tools"), \
                        patch.object(Initializer, "setup_vllm_server") as start, \
                        patch.object(module, "Planner"), \
                        patch.object(module, "Solver") as solver:
                    args = module.parse_arguments()
                    self.assertEqual(args.start_vllm_server, expected_start)
                    module.main(args)
                    self.assertEqual(start.call_count, int(expected_start))
                    solver.return_value.solve.assert_called_once()


if __name__ == "__main__":
    unittest.main()
