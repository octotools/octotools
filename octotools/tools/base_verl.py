# Converts Our BaseTool -> verl.tools.base_tool.Basetool
# Used to fit verl's expected format for tool. 
from .base import BaseTool
from verl.tools.base_tool import BaseTool as VerlTool # type: ignore
from verl.tools.schemas import OpenAIFunctionToolSchema # type: ignore
from verl.utils.rollout_trace import rollout_trace_op # type: ignore
from typing import Any, Optional
from uuid import uuid4


class BaseTool2VerlTool(VerlTool):
    '''Converts octotools.tools.base.BaseTool into verl.tools.base_tool.BaseTool'''
    def __init__(self, tool: BaseTool):
        config = {"type": "native"}  # We use in-place configs inside a class rather than separate .yaml file.
        tool_schema = self.tool.convert_schema()
        super().__init__(config, tool_schema)
        self.tool = tool
        
    def get_openai_tool_schema(self) -> OpenAIFunctionToolSchema:
        return self.tool_schema
        
    async def create(self, instance_id: Optional[str] = None, **kwargs) -> str:
        """Create a tool instance.

        Args:
            instance_id: The instance id of the tool.

        Returns:
            The instance id of the tool.
        """
        if instance_id is None:
            return str(uuid4())
        else:
            return instance_id
        
    
    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> tuple[str, float, dict]:
        """Execute the tool.

        Args:
            instance_id: The instance id of the tool.
            parameters: The json string of the parameters of the tool.

        Returns: tool_response, tool_reward_score, tool_metrics
            tool_response: The response str of the tool.
            tool_reward_score: The step reward score of the tool.
            tool_metrics: The metrics of the tool.
        """
        return "Updated the tool state.", 0.0, {}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """Calculate the reward of the tool.

        Args:
            instance_id: The instance id of the tool.

        Returns:
            The reward of the tool.
        """
        return 0.0

    async def release(self, instance_id: str, **kwargs) -> None:
        """Release the tool instance.

        Args:
            instance_id: The instance id of the tool.
        """
        pass