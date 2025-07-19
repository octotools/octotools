# octotools/tools/base.py
from pydantic import BaseModel
from verl.tools.schemas import OpenAIFunctionToolSchema,OpenAIFunctionSchema,OpenAIFunctionParametersSchema,OpenAIFunctionPropertySchema # type: ignore
import json
class BaseTool:
    """
    A base class for building tool classes that perform specific tasks, such as image processing or text detection.
    """

    require_llm_engine = False  # Default is False, tools that need LLM should set this to True

    def __init__(self, tool_name=None, tool_description=None, tool_version=None, input_types=None, output_type=None, demo_commands=None, output_dir=None, user_metadata=None, model_string=None):
        """
        Initialize the base tool with optional metadata.

        Parameters:
            tool_name (str): The name of the tool.
            tool_description (str): A description of the tool.
            tool_version (str): The version of the tool.
            input_types (dict): The expected input types for the tool.
            output_type (str): The expected output type for the tool.
            demo_commands (list): A list of example commands for using the tool.
            output_dir (str): The directory where the tool should save its output (optional).
            user_metadata (dict): Additional metadata specific to user needs (optional).
            model_string (str): The model string for the LLM engine (optional, only used if require_llm_engine is True).
        """
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.tool_version = tool_version
        self.input_types = input_types
        self.output_type = output_type
        self.demo_commands = demo_commands
        self.output_dir = output_dir
        self.user_metadata = user_metadata
        self.model_string = model_string

    def set_metadata(self, tool_name, tool_description, tool_version, input_types, output_type, demo_commands, user_metadata=None):
        """
        Set the metadata for the tool.

        Parameters:
            tool_name (str): The name of the tool.
            tool_description (str): A description of the tool.
            tool_version (str): The version of the tool.
            input_types (dict): The expected input types for the tool.
            output_type (str): The expected output type for the tool.
            demo_commands (list): A list of example commands for using the tool.
            user_metadata (dict): Additional metadata specific to user needs (optional).
        """
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.tool_version = tool_version
        self.input_types = input_types
        self.output_type = output_type
        self.demo_commands = demo_commands
        self.user_metadata = user_metadata

    def get_metadata(self):
        """
        Returns the metadata for the tool.

        Returns:
            dict: A dictionary containing the tool's metadata.
        """
        metadata = {
            "tool_name": self.tool_name,
            "tool_description": self.tool_description,
            "tool_version": self.tool_version,
            "input_types": self.input_types,
            "output_type": self.output_type,
            "demo_commands": self.demo_commands,
            "require_llm_engine": self.require_llm_engine,
        }
        if self.user_metadata:
            metadata["user_metadata"] = self.user_metadata
        return metadata

    def set_custom_output_dir(self, output_dir):
        """
        Set a custom output directory for the tool.

        Parameters:
            output_dir (str): The new output directory path.
        """
        self.output_dir = output_dir

    def set_llm_engine(self, model_string):
        """
        Set the LLM engine for the tool.

        Parameters:
            model_string (str): The model string for the LLM engine.
        """
        self.model_string = model_string

    def execute(self, *args, **kwargs):
        """
        Execute the tool's main functionality. This method should be overridden by subclasses.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")
    
    
    def convert_schema(self) -> OpenAIFunctionToolSchema:
        '''
        Converts self.input_types into OpenAIFunctionToolSchema
        '''
        
        def parse_type_and_description(value: str):
            """Parses self.input_types's values into ('type', 'description')"""
            # some used shorten text, so we need to resolve this.
            type_convert = { 
                "str": "string",
                "int": "integer",
                "float": "number",
                "bool": "boolean",
                "list": "array",
                "dict": "object"
            }
            type_part, desc_part = value.split(" - ", 1)
            return type_convert.get(type_part.strip(),type_part.strip()), desc_part.strip()

        description = self.tool_description
        
        # Note that OpenAI schema doesn't support output_type or demo_commands. So we merge with self.description.
        if self.demo_commands: # type: list[dict]
            description += "demo command(s) is: " + json.dumps(self.demo_commands, indent=2) + "."
        if self.output_type: # type: str
            param_type, param_description = parse_type_and_description(self.output_type)
            description += "output type is: " + param_type + "and it is " + param_description + "."
        
        properties = {}
        for param_name, value in self.input_types.items():
            # i.g. value = "str - this is the input param for url." 
            #       -> param_type = "string", param_description = "this is the input param for url."
            param_type, param_description = parse_type_and_description(value)
            
            properties[param_name] = OpenAIFunctionPropertySchema(
                type=param_type,
                description=param_description
            )

        required_fields = list(self.input_types.keys())

        # Check https://github.com/volcengine/verl/blob/main/verl/tools/schemas.py
        return OpenAIFunctionToolSchema(
            type="function",
            function=OpenAIFunctionSchema(
                name=self.tool_name,
                description=self.tool_description,
                parameters=OpenAIFunctionParametersSchema(
                    type="object", # type: str
                    properties=properties, # type: dict[str, OpenAIFunctionPropertySchema]
                    required=required_fields # type: list[str]
                )
            )
        )
        
class MCPTool(BaseTool):
    ...    
        
        
