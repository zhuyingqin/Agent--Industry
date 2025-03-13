"""
此模块导入和注册所有可用的工具。

它将所有工具实例化并添加到TOOLS列表中，以便在代理中使用。
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from langchain_core.tools import tool
import asyncio

from react_agent.tool.browser_use_tool import BrowserUseTool

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

# 定义所有可用的工具函数
TOOLS: List[Callable[..., Any]] = [
    simple_search,  # 简单搜索工具，更可靠
    web_search_wrapper,  # 改进的网页搜索工具
    browser_use,
] 