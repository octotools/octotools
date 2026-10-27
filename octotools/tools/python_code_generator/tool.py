# octotools/tools/python_code_generator/tool.py

import ast
import os
import re
import sys
from io import StringIO
import contextlib

import threading
from octotools.tools.base import BaseTool
from octotools.engine.factory import create_llm_engine

import signal
from contextlib import contextmanager

import platform
def is_windows_os():
    system=platform.system()
    return system == 'Windows'

# Custom exception for code execution timeout
class TimeoutException(Exception):
    pass

# Custom context manager for code execution timeout
@contextmanager
def timeout(seconds):
    
    if is_windows_os():
        # Windows timeout using threading.Timer
        def raise_timeout():
            raise TimeoutException("Code execution timed out")
        timer = threading.Timer(seconds, raise_timeout)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()
            
    else:
        def timeout_handler(signum, frame):
            raise TimeoutException("Code execution timed out")

        # Set the timeout handler
        original_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            # Restore the original handler and disable the alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, original_handler)


class Python_Code_Generator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string="gpt-4o-mini"):
        super().__init__(
            tool_name="Python_Code_Generator_Tool",
            tool_description="A tool that generates and executes simple Python code snippets for basic arithmetical calculations and math-related problems. The generated code runs in a highly restricted environment with only basic mathematical operations available.",
            tool_version="1.0.0",
            input_types={
                "query": "str - A clear, specific description of the arithmetic calculation or math problem to be solved, including any necessary numerical inputs."},
            output_type="dict - A dictionary containing the generated code, calculation result, and any error messages.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Calculate the factorial of 5")',
                    "description": "Generate a Python code snippet to calculate the factorial of 5."
                },
                {
                    "command": 'execution = tool.execute(query="Find the sum of prime numbers up to 50")',
                    "description": "Generate a Python code snippet to find the sum of prime numbers up to 50."
                },
                {
                    "command": 'query="Given the list [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], calculate the sum of squares of odd numbers"\nexecution = tool.execute(query=query)',
                    "description": "Generate a Python function for a specific mathematical operation on a given list of numbers."
                },
            ],
            user_metadata = {
                "limitations": [
                    "Restricted to basic Python arithmetic operations and built-in mathematical functions.",
                    "Cannot use any external libraries or modules, including those in the Python standard library.",
                    "Limited to simple mathematical calculations and problems.",
                    "Cannot perform any string processing, data structure manipulation, or complex algorithms.",
                    "No access to any system resources, file operations, or network requests.",
                    "Cannot use 'import' statements.",
                    "All calculations must be self-contained within a single function or script.",
                    "Input must be provided directly in the query string.",
                    "Output is limited to numerical results or simple lists/tuples of numbers."
                ],
                "best_practices": [
                    "Provide clear and specific queries that describe the desired mathematical calculation.",
                    "Include all necessary numerical inputs directly in the query string.",
                    "Keep tasks focused on basic arithmetic, algebraic calculations, or simple mathematical algorithms.",
                    "Ensure all required numerical data is included in the query.",
                    "Verify that the query only involves mathematical operations and does not require any data processing or complex algorithms.",
                    "Review generated code to ensure it only uses basic Python arithmetic operations and built-in math functions."
                ]
            }
        )
        print(f"Initializing Python_Code_Generator_Tool with model_string: {model_string}")
        self.llm_engine = create_llm_engine(model_string=model_string, is_multimodal=False) if model_string else None

    @staticmethod
    def preprocess_code(code):
        """
        Preprocesses the generated code snippet by extracting it from the response.
        Returns only the first Python code block found.

        Parameters:
            code (str): The response containing the code snippet.

        Returns:
            str: The extracted code snippet from the first Python block.
            
        Raises:
            ValueError: If no Python code block is found.
        """
        # Look for the first occurrence of a Python code block
        match = re.search(r"```python\s*(.*?)\s*```", code, re.DOTALL)
        if not match:
            raise ValueError("No Python code block found in the response")
        return match.group(1).strip()

    @contextlib.contextmanager
    def capture_output(self):
        """
        Context manager to capture the standard output.

        Yields:
            StringIO: The captured output.
        """
        new_out = StringIO()
        old_out = sys.stdout
        sys.stdout = new_out
        try:
            yield sys.stdout
        finally:
            sys.stdout = old_out

    def execute_code_snippet(self, code):
        """
        Executes the given Python code snippet in a restricted environment.

        Parameters:
            code (str): The Python code snippet to be executed.

        Returns:
            dict: A dictionary containing the printed output and local variables.
        """
        try:
            execution_code = self.preprocess_code(code)
        except Exception as e:
            return {"error": str(e)}

        # Enforce declared security invariants via AST analysis:
        # 1. Prohibit import statements (ast.Import, ast.ImportFrom)
        # 2. Prohibit access to private/dunder attributes
        # 3. Prohibit restricted functions/identifiers
        try:
            parsed_ast = ast.parse(execution_code)
            restricted_names = {
                "exit", "quit", "sys", "os", "subprocess", "eval", "exec",
                "open", "compile", "__import__", "breakpoint", "input"
            }
            for node in ast.walk(parsed_ast):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return {"error": "SecurityError: 'import' statements are prohibited in code snippet."}
                if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                    return {"error": f"SecurityError: Access to private attribute '{node.attr}' is prohibited."}
                if isinstance(node, ast.Name) and node.id in restricted_names:
                    return {"error": f"SecurityError: Access to '{node.id}' is prohibited."}
        except SyntaxError as e:
            return {"error": f"SyntaxError: {e}"}

        # Safe built-in functions allowlist for basic math / data manipulation
        safe_builtins = {
            "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
            "dict": dict, "divmod": divmod, "enumerate": enumerate,
            "filter": filter, "float": float, "hex": hex, "int": int,
            "isinstance": isinstance, "issubclass": issubclass, "iter": iter,
            "len": len, "list": list, "map": map, "max": max, "min": min,
            "next": next, "oct": oct, "ord": ord, "pow": pow, "print": print,
            "range": range, "reversed": reversed, "round": round, "set": set,
            "sorted": sorted, "str": str, "sum": sum, "tuple": tuple, "zip": zip,
            "True": True, "False": False, "None": None
        }
        safe_globals = {"__builtins__": safe_builtins}
        local_vars = {}

        try:
            # Execute with 10-second timeout and capture output
            with timeout(10):
                with self.capture_output() as output:
                    exec(execution_code, safe_globals, local_vars)
            
            printed_output = output.getvalue().strip()

            # Filter out built-in variables and internal attributes
            used_vars = {k: v for k, v in local_vars.items() if not k.startswith('__')}
            
            return {"printed_output": printed_output, "variables": used_vars}

        except TimeoutException:
            print("Error: Code execution exceeded timeout")
            return {"error": "Execution timed out after 10 seconds"}
        except Exception as e:
            print(f"Error executing code: {e}")
            return {"error": str(e)}

    def execute(self, query):
        """
        Generates and executes Python code based on the provided query.

        Parameters:
            query (str): A query describing the desired operation.

        Returns:
            dict: A dictionary containing the executed output, local variables, or any error message.
        """

        if not self.llm_engine:
            raise ValueError("LLM engine not initialized. Please provide a valid model_string when initializing the tool.")

        task_description = """
        Given a query, generate a Python code snippet that performs the specified operation on the provided data. Please think step by step. Ensure to break down the process into clear, logical steps. Make sure to print the final result in the generated code snippet with a descriptive message explaining what the output represents. The final output should be presented in the following format:

        ```python
        <code snippet>
        ```
        """
        task_description = task_description.strip()
        full_prompt = f"Task:\n{task_description}\n\nQuery:\n{query}"

        response = self.llm_engine(full_prompt)
        result_or_error = self.execute_code_snippet(response)
        return result_or_error

    def get_metadata(self):
        """
        Returns the metadata for the Python_Code_Generator_Tool.

        Returns:
            dict: A dictionary containing the tool's metadata.
        """
        metadata = super().get_metadata()
        metadata["require_llm_engine"] = self.require_llm_engine # NOTE: can be removed if not needed
        return metadata


if __name__ == "__main__":
    # Test command:
    """
    Run the following commands in the terminal to test the script:
    
    cd octotools/tools/python_code_generator
    python tool.py
    """

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Example usage of the Python_Code_Generator_Tool
    tool = Python_Code_Generator_Tool()
    tool = Python_Code_Generator_Tool(model_string="gpt-4o-mini")

    # Get tool metadata
    metadata = tool.get_metadata()
    print(metadata)

    # Sample query for generating and executing Python code
    queries = [
        "Given the number list: [1, 2, 3, 4, 5], calculate the sum of all the numbers in the list.",
    ]
    for query in queries:
        print(f"\n###Query: {query}")
        # Execute the tool with the sample query
        try:
            execution = tool.execute(query=query)
            print("\n###Execution Result:", execution)
        except ValueError as e:
            print(f"Execution failed: {e}")

    print("Done!")
