from typing import Optional

from react_agent.tool.base import BaseTool


_TERMINATE_DESCRIPTION = """Terminate the interaction when the request is met OR if the assistant cannot proceed further with the task."""


class Terminate(BaseTool):
    """终止工具。"""
    
    def __init__(self, **data):
        """初始化Terminate工具。"""
        super().__init__(
            name="terminate",
            description="终止当前任务。",
            parameters={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "终止状态，例如 'success', 'failure', 'canceled'",
                        "default": "success"
                    }
                },
                "required": []
            },
            **data
        )
    
    async def execute(self, status: str = "success") -> str:
        """Finish the current execution"""
        return f"The interaction has been completed with status: {status}"
