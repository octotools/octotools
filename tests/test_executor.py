import importlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from octotools.models.executor import (
    Executor,
    MAX_COMMAND_LENGTH,
    MAX_JSON_DEPTH,
    MAX_TOOL_CALLS,
)
from octotools.models.formatters import ToolCommand


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.executor = Executor("gpt-4o", available_tools=["Fake_Tool"])
        self.executor.set_query_cache_dir(self.temp_dir.name)
        self.calls = []
        self.instances = []
        owner = self

        class FakeTool:
            require_llm_engine = False

            def __init__(self):
                owner.instances.append(self)

            def set_custom_output_dir(self, output_dir):
                self.output_dir = output_dir

            def execute(self, query, count=1, data=None):
                result = {"query": query, "count": count, "data": data}
                owner.calls.append(result)
                return result

        self.tool_class = FakeTool
        self.module = SimpleNamespace(Fake_Tool=FakeTool)
        real_import_module = importlib.import_module

        def import_tool(name, package=None):
            if name == "tools.fake.tool":
                return self.module
            return real_import_module(name, package)

        importer = patch(
            "octotools.models.executor.importlib.import_module",
            side_effect=import_tool,
        )
        self.import_module = importer.start()
        self.addCleanup(importer.stop)

    def assert_rejected(self, command):
        result = self.executor.execute_tool_command("Fake_Tool", command)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error in execute_tool_command:"), result)
        self.assertEqual(self.calls, [])
        return result

    def test_calls_tool_with_json_values_and_returns_results(self):
        data = {"labels": ["cat", "dog"], "threshold": 0.5, "enabled": True, "extra": None}
        result = self.executor.execute_tool_command(
            "Fake_Tool", json.dumps([{"query": "describe image", "data": data}])
        )
        self.assertEqual(result, [{"query": "describe image", "count": 1, "data": data}])
        self.assertEqual(self.calls, result)
        self.assertEqual(self.instances[0].output_dir, self.temp_dir.name)

    def test_multiple_calls_preserve_order(self):
        result = self.executor.execute_tool_command(
            "Fake_Tool", '[{"query":"first"},{"query":"second","count":2}]'
        )
        self.assertEqual([item["query"] for item in result], ["first", "second"])
        self.assertEqual([item["count"] for item in result], [1, 2])
        self.assertEqual(self.calls, result)

    def test_no_argument_tool_accepts_empty_object(self):
        with patch.object(self.tool_class, "execute", lambda tool: "done"):
            result = self.executor.execute_tool_command("Fake_Tool", "[{}]")
        self.assertEqual(result, ["done"])

    def test_code_inside_string_is_passed_as_data(self):
        canary = Path(self.temp_dir.name) / "string-canary"
        query = f"__import__('pathlib').Path({str(canary)!r}).write_text('unexpected')"
        result = self.executor.execute_tool_command(
            "Fake_Tool", json.dumps([{"query": query}])
        )
        self.assertEqual(result[0]["query"], query)
        self.assertFalse(canary.exists())

    def test_python_prelude_cannot_write_file_or_call_tool(self):
        canary = Path(self.temp_dir.name) / "python-canary"
        command = (
            f"__import__('pathlib').Path({str(canary)!r}).write_text('unexpected')\n"
            "execution = tool.execute(query='test')"
        )
        self.assert_rejected(command)
        self.assertFalse(canary.exists())

    def test_invalid_json_shapes_are_rejected(self):
        for command in (
            "not json", "{}", "[]", "null", '["query"]', "[null]", "[[{}]]",
            '[{"query":"ok"}] trailing', '[{"query":"ok",}]',
        ):
            with self.subTest(command=command):
                self.assert_rejected(command)

    def test_missing_and_unknown_parameters_are_rejected(self):
        for command in ("[{}]", '[{"query":"ok","unknown":1}]'):
            with self.subTest(command=command):
                self.assert_rejected(command)

    def test_all_arguments_are_validated_before_first_tool_call(self):
        self.assert_rejected('[{"query":"first"},{"unknown":"second"}]')

    def test_bound_parameter_conflict_prevents_all_calls_with_kwargs(self):
        calls = self.calls

        def execute(self, query, **kwargs):
            calls.append(query)
            return query

        with patch.object(self.tool_class, "execute", execute):
            self.assert_rejected('[{"query":"first"},{"query":"second","self":"unexpected"}]')

    def test_valid_kwargs_and_method_descriptors_remain_supported(self):
        def normal(self, query, **kwargs):
            return {"query": query, **kwargs}

        def static(query, **kwargs):
            return {"query": query, **kwargs}

        def class_method(cls, query, **kwargs):
            return {"query": query, **kwargs}

        def positional_only(self, /, query, **kwargs):
            return {"query": query, **kwargs}

        for name, method, arguments in (
            ("normal", normal, {"query": "hello", "extra": 3}),
            ("static", staticmethod(static), {"query": "hello", "self": "data"}),
            ("class", classmethod(class_method), {"query": "hello", "extra": 3}),
            ("positional_only", positional_only, {"query": "hello", "self": "data"}),
        ):
            with self.subTest(method=name), patch.object(self.tool_class, "execute", method):
                result = self.executor.execute_tool_command("Fake_Tool", json.dumps([arguments]))
                self.assertEqual(result, [arguments])

    def test_invalid_later_json_item_prevents_first_call(self):
        self.assert_rejected('[{"query":"first"},"not an argument object"]')

    def test_duplicate_keys_are_rejected(self):
        for command in (
            '[{"query":"first","query":"second"}]',
            '[{"query":"ok","data":{"key":1,"key":2}}]',
        ):
            with self.subTest(command=command):
                self.assert_rejected(command)

    def test_nonfinite_numbers_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity", "1e9999"):
            with self.subTest(value=value):
                self.assert_rejected('[{"query":"ok","data":' + value + "}]")

    def test_command_size_limit_prevents_execution(self):
        self.assert_rejected(json.dumps([{"query": "x" * MAX_COMMAND_LENGTH}]))

    def test_call_count_limit_prevents_execution(self):
        self.assert_rejected(json.dumps([{"query": "ok"}] * (MAX_TOOL_CALLS + 1)))

    def test_excessive_nesting_is_rejected(self):
        value = "0"
        for _ in range(MAX_JSON_DEPTH + 2):
            value = "[" + value + "]"
        self.assert_rejected('[{"query":"ok","data":' + value + "}]")

    def test_unauthorized_tools_are_rejected_before_import(self):
        for name in ("Python_Code_Generator_Tool", "Unknown_Tool", "../Fake_Tool"):
            with self.subTest(name=name):
                result = self.executor.execute_tool_command(name, '[{"query":"ok"}]')
                self.assertIsInstance(result, str)
                self.assertTrue(result.startswith("Error in execute_tool_command:"))
        self.import_module.assert_not_called()
        self.assertEqual(self.instances, [])

    def test_no_tools_are_authorized_by_default(self):
        executor = Executor("gpt-4o")
        result = executor.execute_tool_command("Fake_Tool", '[{"query":"ok"}]')
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error in execute_tool_command:"))
        self.import_module.assert_not_called()

    def test_extracts_structured_object_and_json_envelope(self):
        command = '[{"query":"hello"}]'
        payload = {"analysis": " analysis ", "explanation": " explanation ", "command": command}
        for response in (ToolCommand(**payload), json.dumps(payload)):
            with self.subTest(response_type=type(response).__name__):
                self.assertEqual(
                    self.executor.extract_explanation_and_command(response),
                    ("analysis", "explanation", command),
                )

    def test_extracts_text_response_with_json_code_block(self):
        response = (
            "Analysis: choose the search tool\n"
            "Command Explanation: pass the query\n"
            "Generated Command:\n```json\n[{\"query\":\"hello\"}]\n```"
        )
        self.assertEqual(
            self.executor.extract_explanation_and_command(response),
            ("choose the search tool", "pass the query", '[{"query":"hello"}]'),
        )

    def test_json_fence_with_trailing_text_executes_only_arguments(self):
        canary = Path(self.temp_dir.name) / "trailing-text-canary"
        response = (
            "Analysis: choose search\nCommand Explanation: pass query\n"
            "Generated Command:\n```json\n[{\"query\":\"hello\"}]\n```\n"
            "This searches for the requested topic.\n"
            f"__import__('pathlib').Path({str(canary)!r}).write_text('unexpected')"
        )
        _, _, command = self.executor.extract_explanation_and_command(response)
        result = self.executor.execute_tool_command("Fake_Tool", command)
        self.assertEqual(result, [{"query": "hello", "count": 1, "data": None}])
        self.assertEqual(self.calls, result)
        self.assertFalse(canary.exists())

    def test_unfenced_command_with_trailing_text_is_rejected(self):
        response = (
            "Analysis: choose search\nCommand Explanation: pass query\n"
            'Generated Command:\n[{"query":"hello"}]\nThis is trailing text.'
        )
        _, _, command = self.executor.extract_explanation_and_command(response)
        self.assert_rejected(command)

    def test_legacy_python_response_cannot_execute(self):
        canary = Path(self.temp_dir.name) / "legacy-canary"
        response = (
            "Analysis: legacy\nCommand Explanation: legacy\nGenerated Command:\n```python\n"
            f"__import__('pathlib').Path({str(canary)!r}).write_text('unexpected')\n"
            "execution = tool.execute(query='hello')\n```"
        )
        _, _, command = self.executor.extract_explanation_and_command(response)
        self.assert_rejected(command)
        self.assertFalse(canary.exists())

    def test_generation_keeps_toolcommand_response_contract(self):
        expected = ToolCommand(
            analysis="use search", explanation="pass query", command='[{"query":"hello"}]'
        )
        engine = Mock(return_value=expected)
        with patch("octotools.models.executor.create_llm_engine", return_value=engine):
            actual = self.executor.generate_tool_command(
                "question", None, "context", "sub-goal", "Fake_Tool", {"input_types": {"query": "str"}}
            )
        self.assertIs(actual, expected)
        self.assertEqual(engine.call_args.kwargs["response_format"], ToolCommand)


if __name__ == "__main__":
    unittest.main()
