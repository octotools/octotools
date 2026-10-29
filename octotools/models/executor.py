import importlib
import inspect
import json
import math
import os
import re
import signal
from datetime import datetime
from typing import Any, Dict, List, Optional

from octotools.engine.factory import create_llm_engine
from octotools.models.formatters import ToolCommand

MAX_COMMAND_LENGTH = 65536
MAX_TOOL_CALLS = 16
MAX_JSON_DEPTH = 16

try:
    TimeoutError
except NameError:
    class TimeoutError(Exception):
        pass

def timeout_handler(signum, frame):
    raise TimeoutError("Function execution timed out")

class Executor:
    def __init__(self, llm_engine_name: str, root_cache_dir: str = "solver_cache",  num_threads: int = 1, max_time: int = 120, max_output_length: int = 100000, verbose: bool = False, available_tools: Optional[List[str]] = None):
        self.llm_engine_name = llm_engine_name
        self.root_cache_dir = root_cache_dir
        self.num_threads = num_threads
        self.max_time = max_time
        self.max_output_length = max_output_length
        self.verbose = verbose
        self.available_tools = frozenset(available_tools or [])

    def set_query_cache_dir(self, query_cache_dir):
        if query_cache_dir:
            self.query_cache_dir = query_cache_dir
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.query_cache_dir = os.path.join(self.root_cache_dir, timestamp)
        os.makedirs(self.query_cache_dir, exist_ok=True)

    def generate_tool_command(self, question: str, image: str, context: str, sub_goal: str, tool_name: str, tool_metadata: Dict[str, Any]) -> Any:
        prompt_generate_tool_command = f"""
Task: Prepare arguments for the selected tool. Return data, not executable code.

Query: {question}
Image: {image}
Context: {context}
Sub-Goal: {sub_goal}
Selected Tool: {tool_name}
Tool Metadata: {tool_metadata}

Instructions:
1. Use the tool's input_types and execute examples to identify its parameters.
2. Set command to a JSON-encoded nonempty list of argument objects. Each object
   becomes one call to the selected tool. Use [{{}}] for a call with no arguments.
3. Include all required parameters, using exact parameter names. Supply literal
   strings, numbers, booleans, null, arrays, or objects. Use context to fill values.
4. Tool-card demo_commands are Python API examples for reference only. Convert
   their arguments to JSON. Never include Python, assignments, imports, expressions,
   function calls, tool names, or method names in command.
5. Use at most {MAX_TOOL_CALLS} calls and {MAX_COMMAND_LENGTH} characters in command.
   Keep nested arrays and objects within {MAX_JSON_DEPTH} levels.
6. Do not generate preprocessing code. If further processing is needed, explain
   it in analysis and provide only valid arguments for this step's selected tool.

Examples of command values:
- One image: [{{"image": "path/to/image.png", "labels": ["baseball"], "threshold": 0.5}}]
- Multiple calls: [{{"query": "first topic"}}, {{"query": "second topic"}}]
- No arguments: [{{}}]

Return analysis, explanation, and command using the requested response schema.
The command field remains a string containing the JSON list. If using plain text,
use Analysis:, Command Explanation:, and Generated Command:, followed by that list.
"""

        llm_generate_tool_command = create_llm_engine(model_string=self.llm_engine_name, is_multimodal=False)
        tool_command = llm_generate_tool_command(prompt_generate_tool_command, response_format=ToolCommand)

        return tool_command

    def extract_explanation_and_command(self, response: Any) -> tuple:

        if isinstance(response, str):
            # Attempt to parse the response as JSON
            try:
                response_dict = json.loads(response)
                response = ToolCommand(**response_dict)
            except Exception as e:
                print(f"Failed to parse response as JSON: {str(e)}")
        if isinstance(response, ToolCommand):
            analysis = response.analysis.strip()
            explanation = response.explanation.strip()
            command = response.command.strip()
        else:
            # Extract analysis
            analysis_pattern = r"Analysis:(.*?)Command Explanation"
            analysis_match = re.search(analysis_pattern, response, re.DOTALL)
            analysis = analysis_match.group(1).strip() if analysis_match else "No analysis found."
            # Extract explanation
            explanation_pattern = r"Command Explanation:(.*?)Generated Command"
            explanation_match = re.search(explanation_pattern, response, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else "No explanation found."
            # Extract command
            command_pattern = r"Generated Command:\s*(.*)\Z"
            command_match = re.search(command_pattern, response, re.DOTALL)
            command = command_match.group(1).strip() if command_match else "No command found."
            # Plain-text models may append prose after a fenced JSON command.
            json_fence = re.match(
                r"```(?:json)?[ \t]*\r?\n(.*?)\r?\n[ \t]*```(?=\s|$)",
                command, re.DOTALL,
            )
            if json_fence:
                command = json_fence.group(1).strip()

        fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", command, re.DOTALL)
        if fence:
            command = fence.group(1).strip()

        return analysis, explanation, command

    @staticmethod
    def _parse_arguments(command: str) -> List[dict]:
        if not isinstance(command, str) or len(command) > MAX_COMMAND_LENGTH:
            raise ValueError("Command must be a JSON string of at most 65536 characters")

        def reject_constant(value):
            raise ValueError(f"Non-finite JSON number: {value}")

        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"Duplicate JSON key: {key}")
                result[key] = value
            return result

        calls = json.loads(command, parse_constant=reject_constant, object_pairs_hook=unique_object)
        if not isinstance(calls, list) or not 1 <= len(calls) <= MAX_TOOL_CALLS:
            raise ValueError("Command must contain 1 to 16 argument objects")
        if any(not isinstance(arguments, dict) for arguments in calls):
            raise ValueError("Each tool call must be an argument object")

        pending = [(calls, 0)]
        while pending:
            value, depth = pending.pop()
            if depth > MAX_JSON_DEPTH:
                raise ValueError("JSON nesting exceeds 16 levels")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("JSON numbers must be finite")
            if isinstance(value, dict):
                pending.extend((item, depth + 1) for item in value.values())
            elif isinstance(value, list):
                pending.extend((item, depth + 1) for item in value)
        return calls

    def execute_tool_command(self, tool_name: str, command: str) -> Any:
        """Call an enabled tool with JSON arguments; never evaluate generated code."""
        def execute_with_timeout(tool, arguments):
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.max_time)
            try:
                return tool.execute(**arguments)
            except TimeoutError:
                return f"Execution timed out after {self.max_time} seconds"
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

        try:
            if tool_name not in self.available_tools:
                raise ValueError(f"Tool '{tool_name}' is not enabled")
            calls = self._parse_arguments(command)

            module_name = f"tools.{tool_name.lower().replace('_tool', '')}.tool"
            module = importlib.import_module(module_name)
            tool_class = getattr(module, tool_name)
            if getattr(tool_class, 'require_llm_engine', False):
                tool = tool_class(model_string=self.llm_engine_name)
            else:
                tool = tool_class()

            # Validate the whole batch before any tool call can have side effects.
            execute = tool.execute
            bound_args = ()
            if inspect.ismethod(execute):
                # Keep self/cls conflicts visible even when the method accepts **kwargs.
                bound_args = (execute.__self__,)
                execute = execute.__func__
            signature = inspect.signature(execute)
            for arguments in calls:
                signature.bind(*bound_args, **arguments)
            tool.set_custom_output_dir(self.query_cache_dir)

            executions = []
            for arguments in calls:
                result = execute_with_timeout(tool, arguments)
                if result is not None:
                    executions.append(result)
                else:
                    executions.append(f"No execution captured for arguments: {arguments}")
            return executions
        except Exception as e:
            return f"Error in execute_tool_command: {str(e)}"
