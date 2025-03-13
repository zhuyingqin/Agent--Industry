"""Utility to run shell commands asynchronously with a timeout."""

import asyncio
from typing import Optional, Tuple

from react_agent.tool.base import BaseTool


TRUNCATED_MESSAGE: str = "<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>"
MAX_RESPONSE_LEN: int = 16000


def maybe_truncate(content: str, truncate_after: int | None = MAX_RESPONSE_LEN):
    """Truncate content and append a notice if content exceeds the specified length."""
    return (
        content
        if not truncate_after or len(content) <= truncate_after
        else content[:truncate_after] + TRUNCATED_MESSAGE
    )


async def run(
    cmd: str,
    timeout: float | None = 120.0,  # seconds
    truncate_after: int | None = MAX_RESPONSE_LEN,
) -> Tuple[int, str, str]:
    """Run a shell command asynchronously with a timeout."""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        return (
            process.returncode or 0,
            maybe_truncate(stdout.decode(), truncate_after=truncate_after),
            maybe_truncate(stderr.decode(), truncate_after=truncate_after),
        )
    except asyncio.TimeoutError as exc:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        raise TimeoutError(
            f"Command '{cmd}' timed out after {timeout} seconds"
        ) from exc


class Run(BaseTool):
    """工具类，用于执行shell命令。"""
    
    name: str = "run"
    description: str = """运行shell命令并返回结果。
使用此工具可以执行各种shell命令，如列出文件、查看文件内容、安装软件包等。
该工具返回命令的退出代码、标准输出和标准错误。
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "cmd": {
                "type": "string",
                "description": "(必需) 要执行的shell命令。",
            },
            "timeout": {
                "type": "number",
                "description": "(可选) 命令执行的超时时间（秒）。默认为120秒。",
                "default": 120.0,
            },
        },
        "required": ["cmd"],
    }

    async def execute(self, cmd: str, timeout: Optional[float] = 120.0) -> str:
        """
        执行shell命令并返回结果。

        参数:
            cmd (str): 要执行的shell命令。
            timeout (float, optional): 命令执行的超时时间（秒）。默认为120秒。

        返回:
            str: 命令的输出结果，包括退出代码、标准输出和标准错误。
        """
        try:
            returncode, stdout, stderr = await run(cmd, timeout=timeout)
            
            result = f"Exit Code: {returncode}\n"
            if stdout:
                result += f"\nStandard Output:\n{stdout}\n"
            if stderr:
                result += f"\nStandard Error:\n{stderr}\n"
                
            return result
        except TimeoutError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
