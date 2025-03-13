"""定义自定义推理和行动代理。

与支持工具调用的聊天模型一起工作。
"""

from datetime import datetime, timezone
from typing import Dict, List, Literal, cast, Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from react_agent.all_tools import TOOLS
from react_agent.configuration import Configuration
from react_agent.state import InputState, State
from react_agent.utils import load_chat_model

# 定义调用模型的函数
async def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """调用为我们的"代理"提供动力的LLM。

    此函数准备提示，初始化模型，并处理响应。

    参数:
        state (State): 对话的当前状态。
        config (RunnableConfig): 模型运行的配置。

    返回:
        dict: 包含模型响应消息的字典。
    """
    configuration = Configuration.from_runnable_config(config)

    # 根据配置选择模型
    model_name = configuration.model
    
    # 如果指定了Google作为提供商，使用Gemini模型
    if configuration.model_provider.lower() == "google":
        model_name = f"google/{configuration.gemini_model}"
    
    # 使用工具绑定初始化模型
    model = load_chat_model(model_name).bind_tools(TOOLS)

    # 格式化系统提示
    system_message = configuration.system_prompt or ""
    
    # 如果系统提示包含格式化占位符，则进行格式化
    if "{system_time}" in system_message:
        system_message = system_message.format(
            system_time=datetime.now(tz=timezone.utc).isoformat()
        )

    # 获取模型的响应
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages], config
        ),
    )

    # 处理最后一步但模型仍想使用工具的情况
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="抱歉，我无法在指定的步骤数内找到您问题的答案。",
                )
            ]
        }

    # 将模型的响应作为列表返回，以添加到现有消息中
    return {"messages": [response]}


# 定义路由函数
def should_continue(state: State) -> Literal["tools", "__end__"]:
    """确定是否应该继续执行工具。

    此函数检查模型的最后一条消息是否包含工具调用。

    参数:
        state (State): 对话的当前状态。

    返回:
        str: 下一个节点的名称 ("tools" 或 "__end__")。
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"期望AIMessage，但得到了{type(last_message).__name__}"
        )
    
    # 如果有工具调用，继续执行工具
    if last_message.tool_calls:
        return "tools"
    
    # 否则结束
    return "__end__"


# 创建图构建器
builder = StateGraph(State, input=InputState, config_schema=Configuration)

# 添加节点
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(TOOLS))

# 设置入口点
builder.add_edge("__start__", "call_model")

# 添加条件边
builder.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "tools": "tools",
        "__end__": "__end__",
    },
)

# 从工具节点返回到模型节点
builder.add_edge("tools", "call_model")

# 编译图
graph = builder.compile()

# 设置图的名称
graph.name = "简化版ReAct代理"


