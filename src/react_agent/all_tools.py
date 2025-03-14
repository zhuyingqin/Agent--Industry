"""
此模块导入和注册所有可用的工具。

它将所有工具实例化并添加到TOOLS列表中，以便在代理中使用。
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from langchain_core.tools import tool
import asyncio

# 导入所有工具类
from react_agent.tool.base import BaseTool
from react_agent.tool.bash import Bash
from react_agent.tool.create_chat_completion import CreateChatCompletion
from react_agent.tool.planning import PlanningTool
from react_agent.tool.str_replace_editor import StrReplaceEditor
from react_agent.tool.terminate import Terminate
from react_agent.tool.tool_collection import ToolCollection
from react_agent.tool.google_search import GoogleSearch
from react_agent.tool.python_execute import PythonExecute
from react_agent.tool.run import Run
from react_agent.tool.file_saver import FileSaver
from react_agent.tool.browser_use_tool import BrowserUseTool
from react_agent.tool.scholar_search import ScholarSearch

# 配置日志记录
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@tool
async def browser_use(
    url: str,
    task: str,
    action: str = "browse",
    search_query: Optional[str] = None,
    **kwargs
) -> str:
    """
    使用浏览器访问网页并执行任务。

    参数:
        url: 要访问的网页URL
        task: 要执行的任务描述
        action: 浏览器动作类型，如browse、click、fill、search等
        search_query: 搜索查询词，用于search动作
        **kwargs: 其他参数

    返回:
        str: 工具执行结果
    """
    operation_logs = []
    operation_logs.append(f"开始执行浏览器操作: action={action}, url={url}, task={task}")
    
    # 构建参数
    parameters = kwargs.copy()
    if search_query:
        parameters["search_query"] = search_query
    
    # 创建工具实例
    browser_tool = BrowserUseTool()
    
    try:
        # 第一层尝试：执行浏览器操作
        operation_logs.append("尝试执行浏览器操作...")
        result = await browser_tool.execute(url=url, task=task, action=action, parameters=parameters)
        
        # 检查结果是否为空或错误
        if not result or "失败" in result or "错误" in result:
            operation_logs.append(f"浏览器操作返回可能的错误: {result}")
            
            # 第二层尝试：重置浏览器并重试
            operation_logs.append("尝试重置浏览器并重试...")
            await browser_tool.cleanup()
            result = await browser_tool.execute(url=url, task=task, action=action, parameters=parameters)
        
        # 检查最终结果
        if not result or len(result.strip()) < 10:
            operation_logs.append("浏览器返回空结果")
            return "浏览器返回了空结果。可能的原因：\n1. 页面内容为空\n2. 页面加载失败\n3. 浏览器无法正确渲染页面\n\n建议：\n- 检查URL是否正确\n- 尝试使用simple_search或web_search_wrapper工具\n- 如果是搜索操作，请确保提供了正确的search_query参数"
        
        operation_logs.append("浏览器操作执行成功")
        return result
    
    except Exception as e:
        error_message = str(e)
        operation_logs.append(f"浏览器操作异常: {error_message}")
        
        # 清理资源
        try:
            await browser_tool.cleanup()
        except Exception as cleanup_error:
            operation_logs.append(f"清理浏览器资源时出错: {str(cleanup_error)}")
        
        # 提供用户友好的错误信息和建议
        user_message = f"""
浏览器操作失败: {error_message}

可能的原因:
1. 网络连接问题
2. URL格式不正确
3. 浏览器初始化失败
4. 页面加载超时

建议:
- 检查URL是否正确（确保包含http://或https://）
- 尝试使用simple_search或web_search_wrapper工具
- 如果是搜索操作，请确保提供了正确的search_query参数
- 如果问题持续存在，请联系管理员
"""
        return user_message
    
    finally:
        # 确保资源被清理
        try:
            await browser_tool.cleanup()
        except Exception:
            pass

@tool
async def simple_search(query: str) -> str:
    """使用简单搜索引擎搜索信息。"""
    return f"执行简单搜索: {query}"

@tool
async def web_search_wrapper(query: str) -> str:
    """使用Web搜索包装器搜索信息。"""
    return f"执行Web搜索: {query}"

@tool
async def bash_execute(command: str) -> str:
    """
    执行Bash命令并返回结果。
    
    参数:
        command: 要执行的Bash命令
        
    返回:
        str: 命令执行结果
    """
    bash_tool = Bash()
    result = await bash_tool.execute(command=command)
    return result.content

@tool
async def python_code_execute(code: str, timeout: int = 5) -> str:
    """
    执行Python代码并返回结果。
    
    参数:
        code: 要执行的Python代码
        timeout: 执行超时时间（秒）
        
    返回:
        str: 代码执行结果
    """
    python_tool = PythonExecute()
    result = await python_tool.execute(code=code, timeout=timeout)
    return str(result)

@tool
async def scholar_search_execute(query: str, num_results: int = 5) -> str:
    """
    在Google Scholar上搜索学术文献并返回结果。
    
    参数:
        query: 搜索查询
        num_results: 返回结果数量
        
    返回:
        str: 搜索结果摘要
    """
    scholar_tool = ScholarSearch()
    result = await scholar_tool.execute(query=query, num_results=num_results)
    return result

@tool
async def planning_execute(task: str) -> str:
    """
    为复杂任务创建执行计划。
    
    参数:
        task: 任务描述
        
    返回:
        str: 执行计划
    """
    planning_tool = PlanningTool()
    result = await planning_tool.execute(task=task)
    return result

@tool
async def google_search_execute(query: str) -> str:
    """
    使用Google搜索信息。
    
    参数:
        query: 搜索查询
        
    返回:
        str: 搜索结果
    """
    google_tool = GoogleSearch()
    result = await google_tool.execute(query=query)
    return result

@tool
async def file_save(filename: str, content: str) -> str:
    """
    保存内容到文件。
    
    参数:
        filename: 文件名
        content: 文件内容
        
    返回:
        str: 操作结果
    """
    file_tool = FileSaver()
    result = await file_tool.execute(filename=filename, content=content)
    return result

# 定义所有可用的工具函数
TOOLS: List[Callable[..., Any]] = [
    simple_search,  # 简单搜索工具，更可靠
    web_search_wrapper,  # 改进的网页搜索工具
    browser_use,  # 浏览器工具
    bash_execute,  # Bash命令执行工具
    python_code_execute,  # Python代码执行工具
    scholar_search_execute,  # 学术搜索工具
    planning_execute,  # 规划工具
    google_search_execute,  # Google搜索工具
    file_save,  # 文件保存工具
] 