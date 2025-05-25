import os
from octotools.tools.base import BaseTool


class Robo_Action_Tool(BaseTool):
    """
    A mock tool that simulates sending commands to a dual-arm robot for demo purposes.
    Supported actions include grasping, lifting, moving, rotating, tilting, and releasing objects.
    """

    SUPPORTED_ACTIONS = [
        "grasp",
        "release",
        "lift",
        "place",
        "move",
        "rotate",
        "tilt",
        "push",
        "pull",
    ]

    def __init__(self):
        super().__init__(
            tool_name="Robo_Action_Tool",
            tool_description=(
                "A tool that sends high-level commands to a two-handed robot for manipulation tasks. "
                "Actions cover common operations like grasp, lift, move, rotate, and release."
            ),
            tool_version="1.0.0",
            input_types={
                "action": "str - Name of the action to perform (one of SUPPORTED_ACTIONS)",
                "target": "str - Identifier or description of the target object (e.g., 'box1')",  # noqa: E501
                "parameters": (
                    "dict - Additional parameters such as {\n"
                    "    'hand': 'left'|'right'|'both',\n"
                    "    'position': [x, y, z],  # in meters\n"
                    "    'orientation': {'roll': deg, 'pitch': deg, 'yaw': deg},\n"
                    "    'speed': float  # optional speed parameter in m/s\n"
                    "}"
                ),
            },
            output_type="dict - A dictionary containing status, executed action, and details.",
            demo_commands=[
                {
                    "command": (
                        "execution = tool.execute(action='grasp', target='cube_1', "
                        "parameters={'hand':'both', 'position':[0.1,0.2,0.3]})"
                    ),
                    "description": (
                        "Grasp cube_1 at the specified position using both hands."
                    ),
                },
                {
                    "command": (
                        "execution = tool.execute(action='lift', target='cube_1', "
                        "parameters={'hand':'both', 'speed':0.2})"
                    ),
                    "description": "Lift the previously grasped object at 0.2 m/s.",
                },
                {
                    "command": (
                        "execution = tool.execute(action='rotate', target='cube_1', "
                        "parameters={'hand':'both', 'orientation':{'yaw':90}})"
                    ),
                    "description": "Rotate the object 90 degrees around the yaw axis.",
                },
            ],
            user_metadata={
                "limitations": (
                    "This is a mock implementation for demonstration. It does not communicate with real hardware. "
                    "For actual robot control, integrate with a motion planning and execution stack."
                )
            },
        )

    def execute(self, action, target, parameters=None):
        """
        Simulate execution of a robot action.

        Args:
            action (str): The name of the action to perform.
            target (str): The object to act upon.
            parameters (dict, optional): Additional action parameters.

        Returns:
            dict: A dictionary with execution results and status.
        """
        parameters = parameters or {}

        # Validate action
        if action not in self.SUPPORTED_ACTIONS:
            return {
                "status": "error",
                "message": f"Unsupported action '{action}'. Supported actions: {self.SUPPORTED_ACTIONS}",
                "action": action,
                "target": target,
                "parameters": parameters,
            }

        # Mock execution: in real use, send command to robot middleware
        result = {
            "status": "success",
            "action": action,
            "target": target,
            "parameters": parameters,
            "message": f"Action '{action}' executed on target '{target}' with parameters {parameters}.",
        }
        return result


if __name__ == "__main__":
    # Example usage
    tool = Robo_Action_Tool()
    tool.set_custom_output_dir("robot_actions_logs")

    # Demo: grasp, lift, rotate sequence
    seq = [
        tool.execute(
            action="grasp",
            target="cube_1",
            parameters={"hand": "both", "position": [0.1, 0.2, 0.3]},
        ),
        tool.execute(
            action="lift", target="cube_1", parameters={"hand": "both", "speed": 0.2}
        ),
        tool.execute(
            action="rotate",
            target="cube_1",
            parameters={"hand": "both", "orientation": {"yaw": 90}},
        ),
    ]
    print(seq)
