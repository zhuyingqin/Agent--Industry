"""此模块提供了任务规划和网页搜索功能的工具。

它包括:
1. 任务规划工具 - 用于创建和管理任务执行计划
2. 网页搜索工具 - 用于获取网络信息
3. 其他辅助工具

这些工具旨在支持代理的任务规划和执行功能。
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union, cast

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, InjectedToolArg, Tool, tool
from typing_extensions import Annotated
import requests
from googlesearch import search as google_search_lib
from bs4 import BeautifulSoup

from react_agent.configuration import Configuration


@tool
async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> List[Dict[str, Any]]:
    """搜索一般网络结果。

    此函数使用Google搜索引擎执行搜索，返回结构化的搜索结果。
    它对于回答有关当前事件的问题特别有用。
    
    参数:
        query: 要搜索的查询字符串
        config: 运行配置
        
    返回:
        List[Dict[str, Any]]: 搜索结果列表，每个结果包含标题、内容和URL
    """
    configuration = Configuration.from_runnable_config(config)
    max_results = configuration.max_search_results
    
    # 使用googlesearch-python库执行搜索
    loop = asyncio.get_event_loop()
    urls = await loop.run_in_executor(
        None, lambda: list(google_search_lib(query, num=max_results))
    )
    
    results = []
    for url in urls:
        try:
            # 获取网页内容
            response = requests.get(url, timeout=5)
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
                
                # 添加到结果
                results.append({
                    "title": title,
                    "content": content[:500] + "..." if len(content) > 500 else content,
                    "url": url
                })
        except Exception as e:
            # 如果无法获取内容，添加基本信息
            results.append({
                "title": url,
                "content": f"无法获取内容: {str(e)}",
                "url": url
            })
    
    return results


@tool
async def web_search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> str:
    """搜索网络以获取特定查询的信息。

    此工具使用Google搜索引擎查找与查询相关的信息，并返回格式化的结果。
    它对于获取最新信息、事实核查和研究特别有用。

    参数:
        query: 要搜索的查询字符串
        config: 运行配置

    返回:
        str: 搜索结果的格式化字符串
    """
    # 使用search工具获取结果
    results = await search(query, config=config)
    
    # 格式化结果
    formatted_results = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "无标题")
        content = result.get("content", "无内容")
        url = result.get("url", "无URL")
        
        formatted_result = f"结果 {i}:\n标题: {title}\n内容: {content}\n来源: {url}\n"
        formatted_results.append(formatted_result)
    
    return "\n".join(formatted_results)


@tool
async def planning(
    command: str,
    plan_id: Optional[str] = None,
    title: Optional[str] = None,
    steps: Optional[List[str]] = None,
    step_index: Optional[int] = None,
    step_status: Optional[str] = None,
    *, 
    config: Annotated[RunnableConfig, InjectedToolArg]
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
        config: 运行配置

    返回:
        str: 操作结果的描述
    """
    # 从配置中获取状态
    configuration = Configuration.from_runnable_config(config)
    state = configuration.state
    
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
        plans = state.get("plans", {}).copy()
        plans[new_plan_id] = plan
        
        # 返回成功消息
        return f"Plan created successfully with ID: {new_plan_id}\nTitle: {title}\nSteps:\n" + "\n".join(
            f"{i+1}: {step}" for i, step in enumerate(steps)
        )
    
    elif command == "get":
        # 获取计划详情
        if not plan_id:
            return "错误: 获取计划需要提供计划ID。"
        
        plans = state.get("plans", {})
        if plan_id not in plans:
            return f"错误: 找不到ID为 {plan_id} 的计划。"
        
        plan = plans[plan_id]
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
        plans = state.get("plans", {})
        if not plans:
            return "没有找到计划。"
        
        # 格式化计划列表
        formatted_plans = []
        for pid, plan in plans.items():
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
        
        plans = state.get("plans", {})
        if plan_id not in plans:
            return f"错误: 找不到ID为 {plan_id} 的计划。"
        
        plan = plans[plan_id]
        steps = plan.get("steps", [])
        step_statuses = plan.get("step_statuses", [])
        
        if step_index < 0 or step_index >= len(steps):
            return f"错误: 步骤索引 {step_index} 超出范围 (0-{len(steps)-1})。"
        
        # 更新步骤状态
        step_statuses[step_index] = step_status
        plan["step_statuses"] = step_statuses
        
        # 更新状态
        plans = state.get("plans", {}).copy()
        plans[plan_id] = plan
        
        # 返回成功消息
        return f"Plan updated successfully: {plan_id}\nStep {step_index+1} marked as {step_status}.\n\n" + "\n".join(
            f"{i+1}: {step} {'[COMPLETED]' if status == 'completed' else '[IN PROGRESS]' if status == 'in_progress' else ''}"
            for i, (step, status) in enumerate(zip(steps, step_statuses))
        )
    
    else:
        return f"错误: 未知命令 '{command}'。支持的命令: create, get, list, mark_step"


def get_tools() -> List[Callable[..., Any]]:
    """获取所有可用工具的列表。
    
    返回:
        List[Callable[..., Any]]: 可用工具的列表
    """
    return [search, web_search, planning]
