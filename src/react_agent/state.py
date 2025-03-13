"""定义代理的状态结构。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Dict, List, Optional, Any, Callable, TypedDict, Literal
import operator

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated


# 定义一个合并字典的函数
def merge_dicts(old_dict: Dict, new_dict: Dict) -> Dict:
    """合并两个字典，保留旧字典中的键，并添加或更新新字典中的键。"""
    result = old_dict.copy()
    result.update(new_dict)
    return result


@dataclass
class InputState:
    """定义代理的输入状态，表示与外部世界的更窄接口。

    此类用于定义初始状态和传入数据的结构。
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    """
    跟踪代理主要执行状态的消息。

    通常累积以下模式：
    1. HumanMessage - 用户输入
    2. 带有.tool_calls的AIMessage - 代理选择要使用的工具来收集信息
    3. ToolMessage(s) - 执行的工具的响应（或错误）
    4. 不带.tool_calls的AIMessage - 代理以非结构化格式响应用户
    5. HumanMessage - 用户以下一个对话轮次响应

    步骤2-5可根据需要重复。

    `add_messages`注解确保新消息与现有消息合并，
    通过ID更新以维持"仅追加"状态，除非提供了具有相同ID的消息。
    """


@dataclass
class State(InputState):
    """表示代理的完整状态，扩展InputState并添加额外属性。

    此类可用于存储代理生命周期中所需的任何信息。
    """

    is_last_step: IsLastStep = field(default=False)
    """
    指示当前步骤是否是最后一个步骤。
    当步骤计数达到recursion_limit - 1时，它被设置为'True'。
    """

    # 计划相关的状态
    has_plan: bool = field(default=False)
    """指示是否已经创建了计划。"""
    
    current_plan_id: Optional[str] = field(default=None)
    """当前活动计划的ID。"""
    
    current_step_index: Optional[int] = field(default=None)
    """当前正在执行的步骤索引。"""
    
    plan_complete: bool = field(default=False)
    """指示计划是否已完成。"""
    
    plan_feedback: Optional[str] = field(default=None)
    """用户对计划的反馈。"""
    
    plans: Annotated[Dict[str, Dict[str, Any]], merge_dicts] = field(default_factory=dict)
    """存储所有计划的字典，按计划ID索引。使用merge_dicts函数合并更新。"""
    
    execution_mode: str = field(default="planning")
    """
    代理的执行模式。可能的值：
    - "planning": 代理正在创建计划
    - "awaiting_feedback": 代理正在等待用户对计划的反馈
    - "executing": 代理正在执行计划步骤
    - "responding": 代理正在提供最终响应
    - "generate_queries": 代理正在生成搜索查询
    """
    
    # 查询生成相关字段
    generated_queries: List[str] = field(default_factory=list)
    """存储生成的搜索查询列表。"""

    # 可以根据需要在此处添加其他属性。
    # 常见示例包括：
    # retrieved_documents: List[Document] = field(default_factory=list)
    # extracted_entities: Dict[str, Any] = field(default_factory=dict)
    # api_connections: Dict[str, Any] = field(default_factory=dict)
