"""React Agent.

这个模块定义了一个自定义推理和行动代理图。
它在一个简单的循环中调用工具。
"""

# 避免循环导入
# from react_agent.graph import graph

__all__ = ["graph"]

# 延迟导入
def get_graph():
    """获取代理图实例。
    
    返回:
        StateGraph: 代理图实例
    """
    from react_agent.graph import graph
    return graph
