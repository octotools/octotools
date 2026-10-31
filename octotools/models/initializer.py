import os
import sys
import importlib
import inspect
import traceback
from typing import Dict, Any, List, Tuple
import time
class Initializer:
    def __init__(self, enabled_tools: List[str] = [], model_string: str = None, verbose: bool = False, vllm_config_path: str = None, start_vllm_server: bool = True):
        self.toolbox_metadata = {}
        self.available_tools = []
        self.enabled_tools = enabled_tools
        self.load_all = self.enabled_tools == ["all"]
        self.model_string = model_string # llm model string
        self.verbose = verbose
        self.vllm_server_process = None
        self.vllm_config_path = vllm_config_path
        self.tool_directory_mapping = {}  # Maps tool class names to their directory names
        print("\n==> Initializing octotools...")
        print(f"Enabled tools: {self.enabled_tools}")
        print(f"LLM engine name: {self.model_string}")
        self._set_up_tools()

        # if vllm, set up the vllm server
        if model_string.startswith("vllm-") and start_vllm_server:
            self.setup_vllm_server()

    def get_project_root(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, 'octotools')):
                return os.path.join(current_dir, 'octotools')
            current_dir = os.path.dirname(current_dir)
        raise Exception("Could not find project root")
        
    def load_tools_and_get_metadata(self) -> Dict[str, Any]:
        # Implementation of load_tools_and_get_metadata function
        print("Loading tools and getting metadata...")
        self.toolbox_metadata = {}
        octotools_dir = self.get_project_root()
        tools_dir = os.path.join(octotools_dir, 'tools')        
        # print(f"octotools directory: {octotools_dir}")
        # print(f"Tools directory: {tools_dir}")
        
        # Add the octotools directory and its parent to the Python path
        sys.path.insert(0, octotools_dir)
        sys.path.insert(0, os.path.dirname(octotools_dir))
        print(f"Updated Python path: {sys.path}")
        
        if not os.path.exists(tools_dir):
            print(f"Error: Tools directory does not exist: {tools_dir}")
            return self.toolbox_metadata

        for root, dirs, files in os.walk(tools_dir):
            # print(f"\nScanning directory: {root}")
            if 'tool.py' in files and (self.load_all or os.path.basename(root) in self.available_tools):
                file = 'tool.py'
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                relative_path = os.path.relpath(module_path, octotools_dir)
                import_path = '.'.join(os.path.split(relative_path)).replace(os.sep, '.')[:-3]

                print(f"\n==> Attempting to import: {import_path}")
                try:
                    module = importlib.import_module(import_path)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and name.endswith('Tool') and name != 'BaseTool':
                            # Tools with load_with_all = False load only when named in enabled_tools
                            if self.load_all and not getattr(obj, 'load_with_all', True):
                                continue
                            print(f"Found tool class: {name}")
                            # Store the directory mapping for later use in run_demo_commands
                            directory_name = os.path.basename(root)
                            self.tool_directory_mapping[name] = directory_name
                            try:
                                # Check if the tool requires an LLM engine
                                if hasattr(obj, 'require_llm_engine') and obj.require_llm_engine:
                                    tool_instance = obj(model_string=self.model_string)
                                else:
                                    tool_instance = obj()

                                self.toolbox_metadata[name] = {
                                    'tool_name': getattr(tool_instance, 'tool_name', 'Unknown'),
                                    'tool_description': getattr(tool_instance, 'tool_description', 'No description'),
                                    'tool_version': getattr(tool_instance, 'tool_version', 'Unknown'),
                                    'input_types': getattr(tool_instance, 'input_types', {}),
                                    'output_type': getattr(tool_instance, 'output_type', 'Unknown'),
                                    'demo_commands': getattr(tool_instance, 'demo_commands', []),
                                    'user_metadata': getattr(tool_instance, 'user_metadata', {}), # This is a placeholder for user-defined metadata
                                    'require_llm_engine': getattr(obj, 'require_llm_engine', False),
                                }
                                print(f"Metadata for {name}: {self.toolbox_metadata[name]}")
                            except Exception as e:
                                print(f"Error instantiating {name}: {str(e)}")
                except Exception as e:
                    print(f"Error loading module {module_name}: {str(e)}")
                    
        print(f"\n==> Total number of tools imported: {len(self.toolbox_metadata)}")

        return self.toolbox_metadata

    def run_demo_commands(self) -> List[str]:
        print("\n==> Running demo commands for each tool...")
        self.available_tools = []

        for tool_name, tool_data in self.toolbox_metadata.items():
            print(f"Checking availability of {tool_name}...")

            try:
                # Import the tool module using the stored directory mapping
                directory_name = self.tool_directory_mapping.get(tool_name)
                if directory_name is None:
                    # Fallback to the old logic if mapping is not found
                    directory_name = tool_name.lower().replace('_tool', '')
                module_name = f"tools.{directory_name}.tool"
                module = importlib.import_module(module_name)

                # Get the tool class
                tool_class = getattr(module, tool_name)

                # Instantiate the tool
                tool_instance = tool_class()

                # FIXME This is a temporary workaround to avoid running demo commands
                self.available_tools.append(tool_name)

            except Exception as e:
                print(f"Error checking availability of {tool_name}: {str(e)}")
                print(traceback.format_exc())

        # update the toolmetadata with the available tools
        self.toolbox_metadata = {tool: self.toolbox_metadata[tool] for tool in self.available_tools}
        print("\n✅ Finished running demo commands for each tool.")
        # print(f"Updated total number of available tools: {len(self.toolbox_metadata)}")
        # print(f"Available tools: {self.available_tools}")
        return self.available_tools
    
    def _set_up_tools(self) -> None:
        print("\n==> Setting up tools...")

        # Keep enabled tools
        self.available_tools = [tool.lower().replace('_tool', '') for tool in self.enabled_tools]
        
        # Load tools and get metadata
        self.load_tools_and_get_metadata()
        
        # Run demo commands to determine available tools
        self.run_demo_commands()
        
        # Filter toolbox_metadata to include only available tools
        self.toolbox_metadata = {tool: self.toolbox_metadata[tool] for tool in self.available_tools}
        print("✅ Finished setting up tools.")
        print(f"✅ Total number of final available tools: {len(self.available_tools)}")
        print(f"✅ Final available tools: {self.available_tools}")

    def setup_vllm_server(self) -> None:
        # Check if vllm is installed
        try:
            import vllm
        except ImportError:
            raise ImportError(
                "Automatic vLLM startup requires vllm in this environment. "
                "To avoid dependency conflicts, run a patched vLLM server in a separate "
                "environment at localhost:8888 and set start_vllm_server=False "
                "(CLI: --no-start-vllm-server). See README: Optional vLLM server."
            )
        
        # Validate config path if provided
        if self.vllm_config_path is not None and not os.path.exists(self.vllm_config_path):
            raise ValueError(f"VLLM config path does not exist: {self.vllm_config_path}")
            
        # Start the VLLM server
        command = ["vllm", "serve", self.model_string.replace("vllm-", ""), "--port", "8888"]
        if self.vllm_config_path is not None:
            command = ["vllm", "serve", "--config", self.vllm_config_path, "--port", "8888"]

        import subprocess
        vllm_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        print("Starting VLLM server...")
        while True:
            output = vllm_process.stdout.readline()
            error = vllm_process.stderr.readline()
            time.sleep(5)
            if output.strip() != "":
                print("VLLM server standard output:", output.strip())
            if error.strip() != "":
                print("VLLM server standard error:", error.strip())

            if "Application startup complete." in output or "Application startup complete." in error:
                print("VLLM server started successfully.")
                break

            if vllm_process.poll() is not None:
                print("VLLM server process terminated unexpectedly. Please check the output above for more information.")
                break

        self.vllm_server_process = vllm_process

if __name__ == "__main__":
    enabled_tools = ["Generalist_Solution_Generator_Tool"]
    initializer = Initializer(enabled_tools=enabled_tools)

    print("\nAvailable tools:")
    print(initializer.available_tools)

    print("\nToolbox metadata for available tools:")
    print(initializer.toolbox_metadata)
    