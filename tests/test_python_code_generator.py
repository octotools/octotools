import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import warnings

from octotools.models.initializer import Initializer
from octotools.tools.python_code_generator import tool as python_tool


class PythonCodeGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tool = python_tool.Python_Code_Generator_Tool(model_string=None)

    def run_code(self, code):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return self.tool.execute_code_snippet(f"```python\n{code}\n```")

    def test_direct_execution_warns_and_preserves_output_and_variables(self):
        with self.assertWarnsRegex(RuntimeWarning, "without a sandbox"):
            result = self.tool.execute_code_snippet(
                "```python\nvalue = 2 + 3\nprint(value)\n```"
            )
        self.assertEqual(result, {"printed_output": "5", "variables": {"value": 5}})

    def test_execute_calls_model_once_and_returns_result(self):
        self.tool.llm_engine = Mock(return_value="```python\nprint(2 + 3)\n```")
        with self.assertWarnsRegex(RuntimeWarning, "without a sandbox"):
            result = self.tool.execute("Calculate 2 + 3")
        self.tool.llm_engine.assert_called_once()
        self.assertEqual(result, {"printed_output": "5", "variables": {}})

    def test_code_with_file_side_effect_runs_once(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "marker.txt"
            result = self.run_code(
                f"with open({str(marker)!r}, 'a') as marker:\n"
                "    marker.write('x')\n"
                "print('done')"
            )
            self.assertEqual(marker.read_text(), "x")
            self.assertEqual(result["printed_output"], "done")

    def test_functions_can_use_variables_in_the_same_snippet(self):
        result = self.run_code(
            "value = 5\ndef calculate():\n    return value + 2\nprint(calculate())"
        )
        self.assertEqual(result["printed_output"], "7")

    def test_imports_work_but_modules_and_builtins_are_not_returned(self):
        result = self.run_code("import math\nvalue = math.sqrt(9)\nprint(value)")
        self.assertEqual(result, {"printed_output": "3.0", "variables": {"value": 3.0}})

    def test_errors_preserve_error_result_and_restore_stdout(self):
        original_stdout = sys.stdout
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            for code, error in (
                ("print(5)", "No Python code block found in the response"),
                ("```python\n1 / 0\n```", "division by zero"),
            ):
                with self.subTest(code=code):
                    self.assertEqual(self.tool.execute_code_snippet(code), {"error": error})
                    self.assertIs(sys.stdout, original_stdout)

    def test_timeout_error_uses_the_configured_ten_seconds(self):
        with patch.object(
            python_tool, "timeout", side_effect=python_tool.TimeoutException
        ) as timeout:
            result = self.run_code("print(5)")
        timeout.assert_called_once_with(10)
        self.assertEqual(result, {"error": "Execution timed out after 10 seconds"})

    def test_loaded_only_when_explicitly_named(self):
        tool_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "octotools", "tools", "python_code_generator",
        )
        with patch(
            "octotools.models.initializer.os.walk",
            return_value=[(tool_dir, [], ["tool.py"])],
        ), patch.dict(
            sys.modules, {"tools.python_code_generator.tool": python_tool}
        ), patch.object(
            python_tool, "create_llm_engine"
        ) as factory, patch.object(sys, "path", sys.path.copy()):
            for enabled_tools, loaded in (
                (["all"], False),
                (["Python_Code_Generator_Tool"], True),
            ):
                with self.subTest(enabled_tools=enabled_tools):
                    selected = Initializer(enabled_tools=enabled_tools, model_string="gpt-4o")
                    self.assertEqual("Python_Code_Generator_Tool" in selected.available_tools, loaded)
                    self.assertEqual("Python_Code_Generator_Tool" in selected.toolbox_metadata, loaded)
                    if not loaded:
                        factory.assert_not_called()
        factory.return_value.assert_not_called()


if __name__ == "__main__":
    unittest.main()
