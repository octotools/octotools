import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from octotools.models.formatters import (
    MemoryVerification,
    NextStep,
    QueryAnalysis,
    ToolCommand,
)
from octotools.solver import construct_solver
from octotools.tools.keenable_search import tool as search_tool


class SolverFlowTests(unittest.TestCase):
    def test_public_solver_runs_tool_and_records_result_before_answering(self):
        tool_name = "Keenable_Search_Tool"
        command = json.dumps([{"query": "capital of France", "num_results": 1}])
        search_result = {
            "title": "France",
            "link": "https://example.com/france",
            "snippet": "The capital of France is Paris.",
        }
        responses = {
            "structured": ToolCommand(
                analysis="Look up the capital.", explanation="Search once.", command=command
            ),
            "text": (
                "Analysis: Look up the capital.\nCommand Explanation: Search once.\n"
                f"Generated Command:\n```json\n{command}\n```\n"
                "This searches for the requested fact."
            ),
        }
        tool_dir = str(Path(search_tool.__file__).parent)

        for response_type, command_response in responses.items():
            with self.subTest(response_type=response_type):
                formats = []

                def generate(prompt, response_format=None, **kwargs):
                    formats.append(response_format)
                    if response_format is QueryAnalysis:
                        return QueryAnalysis(
                            concise_summary="Find the capital of France.",
                            required_skills="Fact lookup",
                            relevant_tools=tool_name,
                            additional_considerations="None",
                        )
                    if response_format is NextStep:
                        return NextStep(
                            justification="Search for the capital.",
                            context="The requested country is France.",
                            sub_goal="Find the capital.",
                            tool_name=tool_name,
                        )
                    if response_format is ToolCommand:
                        return command_response
                    self.assertIn(search_result["snippet"], str(prompt))
                    if response_format is MemoryVerification:
                        return MemoryVerification(analysis="The search answered it.", stop_signal=True)
                    self.assertIsNone(response_format)
                    return "Paris"

                engine = Mock(side_effect=generate)
                http_response = Mock(status_code=200)
                http_response.json.return_value = {
                    "results": [{
                        "title": search_result["title"],
                        "url": search_result["link"],
                        "snippet": search_result["snippet"],
                    }]
                }
                with tempfile.TemporaryDirectory() as cache_dir, patch.dict(
                    os.environ
                ), patch.object(sys, "path", sys.path.copy()), patch.dict(
                    sys.modules, {"tools.keenable_search.tool": search_tool}
                ), patch(
                    "octotools.models.initializer.os.walk",
                    return_value=[(tool_dir, [], ["tool.py"])],
                ), patch(
                    "octotools.models.planner.create_llm_engine", return_value=engine
                ), patch(
                    "octotools.models.executor.create_llm_engine", return_value=engine
                ), patch.object(search_tool.requests, "post", return_value=http_response) as post:
                    os.environ.pop("KEENABLE_API_KEY", None)
                    solver = construct_solver(
                        llm_engine_name="offline",
                        enabled_tools=[tool_name],
                        root_cache_dir=cache_dir,
                        max_steps=2,
                        verbose=False,
                    )
                    self.assertEqual(solver.executor.available_tools, {tool_name})
                    result = solver.solve("What is the capital of France?")

                post.assert_called_once()
                self.assertEqual(post.call_args.kwargs["json"], {
                    "query": "capital of France", "max_results": 1,
                })
                self.assertEqual(result["step_count"], 1)
                self.assertEqual(result["memory"], solver.memory.get_actions())
                self.assertEqual(result["memory"]["Action Step 1"], {
                    "tool_name": tool_name,
                    "sub_goal": "Find the capital.",
                    "command": command,
                    "result": [[search_result]],
                })
                self.assertEqual(result["final_output"], "Paris")
                self.assertEqual(result["direct_output"], "Paris")
                self.assertEqual(formats, [
                    QueryAnalysis, NextStep, ToolCommand, MemoryVerification, None, None,
                ])


if __name__ == "__main__":
    unittest.main()
