# octotools/tools/__init__.py
# Purpose: Create a tool registry: Dict[class_name: BaseTool2VerlTool]

import os
import importlib
import inspect
from .base import BaseTool
from .base_verl import BaseTool2VerlTool
from typing import Dict, Optional


def _discover_tools() -> Dict[str, BaseTool2VerlTool]:
    """
    Discover all tool classes wrapped w/ BaseTool2VerlTool(BaseTool).
    
    Returns: {
                tool_name1: BaseTool2VerlTool(tool=BaseTool),
                tool_name2: BaseTool2VerlTool(tool=BaseTool),                    
             }
    """
    tool_registry = {}
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for root, _, files in os.walk(current_dir):
        if root == current_dir or '__pycache__' in root:
            continue
        if 'tool.py' in files:
            relative_path = os.path.relpath(root, current_dir)
            tool_folder_name = f"{relative_path.replace(os.sep, '.')}"
            try:
                tool_module = importlib.import_module(f".{tool_folder_name}.tool", __package__)
                for name, obj in inspect.getmembers(tool_module):
                    if (inspect.isclass(obj) and issubclass(obj, BaseTool) and obj != BaseTool):
                        obj = BaseTool2VerlTool(tool=obj())                        
                        #######################Tool Registry Format############################
                        tool_registry[name] = obj # Obj is not a class, but an instance! 
                        #########################################################
                        break
            except Exception as e:
                print(f"Could not import tool from {tool_folder_name}: {e}")
    
    return tool_registry

TOOL_REGISTRY = _discover_tools()

__all__ = ['TOOL_REGISTRY']
