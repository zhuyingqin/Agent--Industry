"""
子图模块 - 提供用于构建复杂工作流的可组合子图

此模块包含用于故障分析和问题总结的子图，以及一个入口图，
用于协调这些子图的执行。
"""

from typing import Dict, List, Any

# 导出状态类
from .state import (
    Logs,
    FailureAnalysisState,
    QuestionSummarizationState,
    EntryGraphState
)

# 导出图构建器和已编译的图
from .graph import (
    fa_builder,  # 故障分析子图构建器
    qs_builder,  # 问题总结子图构建器
    entry_builder,  # 入口图构建器
    graph  # 已编译的入口图
)

# 导出主要函数
from .graph import (
    get_failures,
    generate_summary,
    send_to_slack,
    format_report_for_slack,
    convert_logs_to_docs
)

__all__ = [
    # 状态类
    "Logs",
    "FailureAnalysisState",
    "QuestionSummarizationState",
    "EntryGraphState",
    
    # 图构建器和已编译的图
    "fa_builder",
    "qs_builder",
    "entry_builder",
    "graph",
    
    # 主要函数
    "get_failures",
    "generate_summary",
    "send_to_slack",
    "format_report_for_slack",
    "convert_logs_to_docs"
]

def run_graph(raw_logs: List[Dict[str, Any]], debug: bool = False) -> Dict[str, Any]:
    """
    运行入口图处理原始日志数据
    
    参数:
        raw_logs: 要处理的原始日志列表
        debug: 是否启用调试模式
        
    返回:
        处理结果字典
    """
    return graph.invoke({"raw_logs": raw_logs}, debug=debug) 