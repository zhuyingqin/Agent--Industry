"""
此模块导入和注册所有可用的工具。

它将所有工具实例化并添加到TOOLS列表中，以便在代理中使用。
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Literal
from langchain_core.tools import tool
import uuid
import asyncio
from datetime import datetime

from react_agent.tool import (
    Bash,
    BrowserUseTool,
    CreateChatCompletion,
    FileSaver,
    GoogleSearch,
    PlanningTool,
    PythonExecute,
    Run,
    ScholarSearch,
    StrReplaceEditor,
    Terminate,
    ToolCollection,
)
from react_agent.tools import search

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tools")

# 实例化所有工具
bash_tool = Bash()
browser_tool = BrowserUseTool()
chat_completion_tool = CreateChatCompletion()
file_saver_tool = FileSaver()
google_search_tool = GoogleSearch()
planning_tool = PlanningTool()
python_execute_tool = PythonExecute()
run_tool = Run()
scholar_search_tool = ScholarSearch()
str_replace_editor_tool = StrReplaceEditor()
terminate_tool = Terminate()

# 创建工具集合
tool_collection = ToolCollection(
    bash_tool,
    browser_tool,
    chat_completion_tool,
    file_saver_tool,
    google_search_tool,
    planning_tool,
    python_execute_tool,
    run_tool,
    scholar_search_tool,
    str_replace_editor_tool,
    terminate_tool,
)

# 将工具转换为LangChain工具格式
@tool
async def bash(cmd: str, timeout: float = 120.0) -> str:
    """执行bash命令并返回结果。
    
    此工具用于执行bash命令并返回命令的输出。
    
    参数:
        cmd: 要执行的bash命令
        timeout: 命令执行的最大超时时间（秒）
        
    返回:
        str: 命令执行的输出结果
    """
    if not cmd:
        return "错误: 必须提供要执行的命令。"
        
    logger.info(f"调用 bash 工具: cmd={cmd}, timeout={timeout}")
    try:
        result = await bash_tool.execute(cmd=cmd, timeout=timeout)
        logger.info(f"bash 工具返回结果: {result[:100]}..." if len(str(result)) > 100 else f"bash 工具返回结果: {result}")
        return result
    except Exception as e:
        logger.error(f"bash 工具执行错误: {str(e)}")
        return f"执行bash命令出错: {str(e)}"

@tool
async def browser_use(url: str, task: str, action: str = "browse") -> str:
    """使用浏览器访问网页并执行任务。
    
    此工具用于访问网页并执行指定的任务，如浏览、点击、填写表单等。
    
    参数:
        url: 要访问的网页URL
        task: 要执行的任务描述
        action: 浏览器动作类型，默认为"browse"
        
    返回:
        str: 执行结果的描述
    """
    logger.info(f"调用 browser_use 工具: url={url}, task={task}, action={action}")
    try:
        result = await browser_tool.execute(url=url, task=task, action=action)
        # 处理ToolResult对象，确保我们获取正确的结果内容
        result_str = str(result)  # 将结果转换为字符串
        logger.info(f"browser_use 工具返回结果: {result_str[:100]}..." if len(result_str) > 100 else f"browser_use 工具返回结果: {result_str}")
        return result_str
    except Exception as e:
        logger.error(f"browser_use 工具执行错误: {str(e)}")
        return f"浏览器工具执行出错: {str(e)}"

@tool
async def chat_completion(prompt: str) -> str:
    """创建聊天完成并返回结果。"""
    logger.info(f"调用 chat_completion 工具: prompt={prompt}")
    result = await chat_completion_tool.execute(prompt=prompt)
    logger.info(f"chat_completion 工具返回结果: {result[:100]}..." if len(str(result)) > 100 else f"chat_completion 工具返回结果: {result}")
    return result

@tool
async def file_saver(content: str, filename: str) -> str:
    """将内容保存到文件。"""
    logger.info(f"调用 file_saver 工具: filename={filename}, content长度={len(content)}")
    result = await file_saver_tool.execute(content=content, filename=filename)
    logger.info(f"file_saver 工具返回结果: {result}")
    return result

@tool
async def google_search(query: str) -> str:
    """使用Google搜索指定查询并返回结果。"""
    logger.info(f"调用 google_search 工具: query={query}")
    try:
        # 添加超时控制
        result = await asyncio.wait_for(
            google_search_tool.execute(query=query),
            timeout=10.0  # 10秒超时
        )
        logger.info(f"google_search 工具返回结果: {result[:100]}..." if len(str(result)) > 100 else f"google_search 工具返回结果: {result}")
        return result
    except asyncio.TimeoutError:
        logger.error(f"google_search 工具超时: query={query}")
        return "搜索超时，请尝试简化查询或稍后重试。"
    except Exception as e:
        logger.error(f"google_search 工具错误: {str(e)}")
        return f"搜索出错: {str(e)}"

@tool
async def simple_search(query: str) -> str:
    """简单搜索网络信息，返回相关结果。
    
    此工具执行基本的网络搜索并返回结果列表。
    适用于快速获取信息而不需要详细内容。
    
    参数:
        query: 要搜索的查询字符串
        
    返回:
        str: 搜索结果列表
    """
    logger.info(f"调用 simple_search 工具: query={query}")
    
    try:
        # 导入必要的库
        from googlesearch import search as google_search_lib
        
        # 执行搜索，限制结果数量
        urls = list(google_search_lib(query, num=5, stop=5))
        
        # 格式化结果
        if not urls:
            return "未找到搜索结果。"
        
        result = f"搜索 '{query}' 的结果:\n\n" + "\n".join([f"{i+1}. {url}" for i, url in enumerate(urls)])
        logger.info(f"simple_search 工具返回结果: {result[:100]}..." if len(result) > 100 else f"simple_search 工具返回结果: {result}")
        return result
    except Exception as e:
        logger.error(f"simple_search 工具错误: {str(e)}")
        return f"搜索出错: {str(e)}"

@tool
async def web_search_wrapper(query: str) -> str:
    """搜索网络以获取特定查询的信息，并返回格式化的结果。
    
    此工具使用Google搜索引擎查找与查询相关的信息，并返回格式化的结果。
    它对于获取最新信息、事实核查和研究特别有用。
    
    参数:
        query: 要搜索的查询字符串
        
    返回:
        str: 搜索结果的格式化字符串
    """
    logger.info(f"调用 web_search_wrapper 工具: query={query}")
    
    try:
        # 导入必要的库
        import requests
        from bs4 import BeautifulSoup
        from googlesearch import search as google_search_lib
        import concurrent.futures
        
        # 直接使用googlesearch-python库执行搜索
        try:
            urls = list(google_search_lib(query, num=5, stop=5))
        except Exception as e:
            logger.error(f"搜索URL失败: {str(e)}")
            return f"搜索失败: {str(e)}。请尝试简化查询或使用其他搜索词。"
        
        if not urls:
            return "未找到搜索结果。请尝试使用其他搜索词。"
        
        # 定义获取单个URL内容的函数
        def get_url_content(url, index):
            try:
                # 设置请求头，模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # 发送请求，设置较短的超时
                response = requests.get(url, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    # 解析HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取标题
                    title = soup.title.string if soup.title else "无标题"
                    
                    # 提取内容（简单实现，仅提取部分文本）
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text() for p in paragraphs[:3]])
                    if not content:
                        content = "无法提取内容"
                    
                    # 格式化结果
                    return f"结果 {index}:\n标题: {title}\n内容: {content[:300]}...\n来源: {url}\n"
                else:
                    return f"结果 {index}:\n无法访问URL: {url}\n状态码: {response.status_code}\n"
            except Exception as e:
                return f"结果 {index}:\n无法获取内容: {url}\n错误: {str(e)[:100]}\n"
        
        # 使用线程池并行获取内容，设置较短的超时
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(get_url_content, url, i+1): url for i, url in enumerate(urls)}
            
            # 收集结果，设置总体超时
            try:
                completed, _ = concurrent.futures.wait(
                    future_to_url, 
                    timeout=10,
                    return_when=concurrent.futures.ALL_COMPLETED
                )
                
                # 获取已完成的结果
                for future in completed:
                    results.append(future.result())
            except Exception as e:
                logger.error(f"获取搜索结果超时: {str(e)}")
                # 添加已完成的结果
                for future in future_to_url:
                    if future.done():
                        results.append(future.result())
        
        # 如果没有结果，返回简单的URL列表
        if not results:
            return f"无法获取详细内容，但找到了以下URL:\n" + "\n".join([f"{i+1}. {url}" for i, url in enumerate(urls)])
        
        result = "\n".join(results)
        logger.info(f"web_search_wrapper 工具返回结果: {result[:100]}..." if len(result) > 100 else f"web_search_wrapper 工具返回结果: {result}")
        return result
    
    except Exception as e:
        logger.error(f"web_search_wrapper 工具错误: {str(e)}")
        return f"搜索出错: {str(e)}。请尝试使用simple_search工具代替。"

@tool
async def planning_wrapper(
    command: str,
    plan_id: Optional[str] = None,
    title: Optional[str] = None,
    steps: Optional[List[str]] = None,
    step_index: Optional[int] = None,
    step_status: Optional[str] = None,
) -> str:
    """管理任务执行计划。
    
    此工具用于创建、更新和管理任务执行计划。
    它支持以下命令:
    - create: 创建新计划
    - get: 获取计划详情
    - list: 列出所有计划
    - mark_step: 更新步骤状态
    
    参数:
        command: 要执行的命令 (create, get, list, mark_step)
        plan_id: 计划ID (除create外的命令需要)
        title: 计划标题 (create命令需要)
        steps: 计划步骤列表 (create命令需要)
        step_index: 步骤索引 (mark_step命令需要)
        step_status: 步骤状态 (mark_step命令需要)
    
    返回:
        str: 操作结果的描述
    """
    logger.info(f"调用 planning_wrapper 工具: command={command}, plan_id={plan_id}, title={title}, steps={steps}, step_index={step_index}, step_status={step_status}")
    
    # 验证命令参数
    if not command:
        return "错误: 必须提供命令参数。支持的命令: create, get, list, mark_step"
    
    # 简单的内存存储，实际应用中应该使用更持久的存储
    if not hasattr(planning_wrapper, "_plans"):
        planning_wrapper._plans = {}
    
    if command == "create":
        # 创建新计划
        if not title or not steps:
            return "错误: 创建计划需要提供标题和步骤。"
        
        # 生成唯一ID
        new_plan_id = plan_id or f"plan_{uuid.uuid4().hex[:8]}"
        
        # 初始化所有步骤状态为"not_started"
        step_statuses = ["not_started"] * len(steps)
        
        # 创建计划对象
        plan = {
            "plan_id": new_plan_id,
            "title": title,
            "steps": steps,
            "step_statuses": step_statuses,
            "created_at": datetime.now().isoformat()
        }
        
        # 更新状态
        planning_wrapper._plans[new_plan_id] = plan
        
        # 返回成功消息
        return f"Plan created successfully with ID: {new_plan_id}\nTitle: {title}\nSteps:\n" + "\n".join(
            f"{i+1}: {step}" for i, step in enumerate(steps)
        )
    
    elif command == "get":
        # 获取计划详情
        if not plan_id:
            return "错误: 获取计划需要提供计划ID。"
        
        if plan_id not in planning_wrapper._plans:
            return f"错误: 找不到ID为 {plan_id} 的计划。"
        
        plan = planning_wrapper._plans[plan_id]
        steps = plan.get("steps", [])
        step_statuses = plan.get("step_statuses", [])
        
        # 格式化步骤和状态
        formatted_steps = []
        for i, (step, status) in enumerate(zip(steps, step_statuses)):
            status_marker = ""
            if status == "completed":
                status_marker = "[COMPLETED]"
            elif status == "in_progress":
                status_marker = "[IN PROGRESS]"
            
            formatted_steps.append(f"{i+1}: {step} {status_marker}")
        
        # 返回计划详情
        return f"Plan ID: {plan_id}\nTitle: {plan.get('title', 'Untitled')}\nSteps:\n" + "\n".join(formatted_steps)
    
    elif command == "list":
        # 列出所有计划
        if not planning_wrapper._plans:
            return "没有找到计划。"
        
        # 格式化计划列表
        formatted_plans = []
        for pid, plan in planning_wrapper._plans.items():
            title = plan.get("title", "Untitled")
            steps = plan.get("steps", [])
            step_statuses = plan.get("step_statuses", [])
            
            completed_steps = sum(1 for status in step_statuses if status == "completed")
            total_steps = len(steps)
            
            formatted_plans.append(f"ID: {pid}, 标题: {title}, 进度: {completed_steps}/{total_steps}")
        
        # 返回计划列表
        return "Plans:\n" + "\n".join(formatted_plans)
    
    elif command == "mark_step":
        # 更新步骤状态
        if not plan_id or step_index is None or not step_status:
            return "错误: 更新步骤状态需要提供计划ID、步骤索引和状态。"
        
        if plan_id not in planning_wrapper._plans:
            return f"错误: 找不到ID为 {plan_id} 的计划。"
        
        plan = planning_wrapper._plans[plan_id]
        steps = plan.get("steps", [])
        step_statuses = plan.get("step_statuses", [])
        
        if step_index < 0 or step_index >= len(steps):
            return f"错误: 步骤索引 {step_index} 超出范围 (0-{len(steps)-1})。"
        
        # 更新步骤状态
        step_statuses[step_index] = step_status
        plan["step_statuses"] = step_statuses
        
        # 返回成功消息
        return f"Plan updated successfully: {plan_id}\nStep {step_index+1} marked as {step_status}.\n\n" + "\n".join(
            f"{i+1}: {step} {'[COMPLETED]' if status == 'completed' else '[IN PROGRESS]' if status == 'in_progress' else ''}"
            for i, (step, status) in enumerate(zip(steps, step_statuses))
        )
    
    else:
        return f"错误: 未知命令 '{command}'。支持的命令: create, get, list, mark_step"

@tool
async def python_execute(code: str, timeout: int = 5) -> str:
    """执行Python代码并返回结果。"""
    logger.info(f"调用 python_execute 工具: code={code}, timeout={timeout}")
    result = await python_execute_tool.execute(code=code, timeout=timeout)
    logger.info(f"python_execute 工具返回结果: {result}")
    return result

@tool
async def run(cmd: str, timeout: float = 120.0) -> str:
    """运行shell命令并返回结果。
    
    此工具用于执行shell命令并返回命令的输出。
    
    参数:
        cmd: 要执行的shell命令
        timeout: 命令执行的最大超时时间（秒）
        
    返回:
        str: 命令执行的输出结果
    """
    if not cmd:
        return "错误: 必须提供要执行的命令。"
        
    logger.info(f"调用 run 工具: cmd={cmd}, timeout={timeout}")
    try:
        result = await run_tool.execute(cmd=cmd, timeout=timeout)
        logger.info(f"run 工具返回结果: {result[:100]}..." if len(str(result)) > 100 else f"run 工具返回结果: {result}")
        return result
    except Exception as e:
        logger.error(f"run 工具执行错误: {str(e)}")
        return f"执行shell命令出错: {str(e)}"

@tool
async def scholar_search(
    query: str,
    num_results: int = 5,
    year_from: int = None,
    year_to: int = None,
    summarize: bool = True
) -> str:
    """在 Google Scholar 上搜索学术文献并总结结果。"""
    logger.info(f"调用 scholar_search 工具: query={query}, num_results={num_results}, year_from={year_from}, year_to={year_to}, summarize={summarize}")
    try:
        # 添加超时控制
        result = await asyncio.wait_for(
            scholar_search_tool.execute(
                query=query,
                num_results=num_results,
                year_from=year_from,
                year_to=year_to,
                summarize=summarize
            ),
            timeout=15.0  # 15秒超时
        )
        logger.info(f"scholar_search 工具返回结果: {result[:100]}..." if len(str(result)) > 100 else f"scholar_search 工具返回结果: {result}")
        return result
    except asyncio.TimeoutError:
        logger.error(f"scholar_search 工具超时: query={query}")
        return "学术搜索超时，请尝试简化查询或减少结果数量。"
    except Exception as e:
        logger.error(f"scholar_search 工具错误: {str(e)}")
        return f"学术搜索出错: {str(e)}"

@tool
async def str_replace_editor(text: str, find: str, replace: str) -> str:
    """在文本中查找并替换字符串。"""
    logger.info(f"调用 str_replace_editor 工具: find={find}, replace={replace}, text长度={len(text)}")
    result = await str_replace_editor_tool.execute(text=text, find=find, replace=replace)
    logger.info(f"str_replace_editor 工具返回结果: {result[:100]}..." if len(str(result)) > 100 else f"str_replace_editor 工具返回结果: {result}")
    return result

@tool
async def terminate(status: str = "success") -> str:
    """终止当前任务。
    
    此工具用于终止当前正在执行的任务。
    可以指定终止状态，默认为"success"。
    
    参数:
        status: 终止状态，默认为"success"
        
    返回:
        str: 终止操作的结果描述
    """
    logger.info(f"调用 terminate 工具: status={status}")
    result = await terminate_tool.execute(status=status)
    logger.info(f"terminate 工具返回结果: {result}")
    return result

# 定义所有可用的工具函数
TOOLS: List[Callable[..., Any]] = [
    simple_search,  # 简单搜索工具，更可靠
    web_search_wrapper,  # 改进的网页搜索工具
    bash,
    browser_use,
    chat_completion,
    file_saver,
    google_search,
    planning_wrapper,  # 不需要config参数的计划工具
    python_execute,
    run,
    scholar_search,
    str_replace_editor,
    terminate,
] 