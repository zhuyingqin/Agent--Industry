import threading
from typing import Dict

from react_agent.tool.base import BaseTool


class PythonExecute(BaseTool):
    """Python执行工具。"""

    name: str = "python_execute"
    description: str = "执行Python代码并返回结果。"
    parameters: dict = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute.",
            },
        },
        "required": ["code"],
    }

    async def execute(
        self,
        code: str,
        timeout: int = 5,
    ) -> Dict:
        """
        Executes the provided Python code with a timeout.

        Args:
            code (str): The Python code to execute.
            timeout (int): Execution timeout in seconds.

        Returns:
            Dict: Contains 'output' with execution output or error message and 'success' status.
        """
        result = {"observation": ""}

        def run_code():
            try:
                safe_globals = {"__builtins__": dict(__builtins__)}

                import sys
                from io import StringIO

                output_buffer = StringIO()
                sys.stdout = output_buffer

                exec(code, safe_globals, {})

                sys.stdout = sys.__stdout__

                result["observation"] = output_buffer.getvalue()

            except Exception as e:
                result["observation"] = str(e)
                result["success"] = False

        thread = threading.Thread(target=run_code)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            return {
                "observation": f"Execution timeout after {timeout} seconds",
                "success": False,
            }

        return result
