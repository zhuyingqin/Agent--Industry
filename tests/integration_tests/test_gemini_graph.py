"""测试使用Gemini模型的代理图。"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from langchain_core.messages import AIMessage

from react_agent import get_graph
from react_agent.configuration import Configuration

# 获取图实例
graph = get_graph()

@pytest.mark.asyncio
@patch("react_agent.utils.ChatGoogleGenerativeAI")
async def test_gemini_agent_mock(mock_chat_google: MagicMock) -> None:
    """测试使用模拟的Gemini模型的代理。"""
    # 设置模拟模型
    mock_model = MagicMock()
    mock_chat_google.return_value = mock_model
    
    # 设置模拟响应
    mock_response = AIMessage(content="这是来自Gemini模型的模拟响应")
    mock_model.bind_tools.return_value = mock_model
    
    # 使用AsyncMock来模拟异步方法
    async_mock = AsyncMock(return_value=mock_response)
    mock_model.ainvoke = async_mock
    
    # 调用代理
    res = await graph.ainvoke(
        {"messages": [("user", "你好，请介绍一下自己")]},
        {
            "configurable": {
                "system_prompt": "你是一个有帮助的AI助手。",
                "model_provider": "google",
                "gemini_model": "models/gemini-2.0-flash"
            }
        },
    )
    
    # 验证结果
    assert res["messages"][-1].content == "这是来自Gemini模型的模拟响应"
    
    # 验证是否正确调用了Gemini模型
    mock_chat_google.assert_called_once_with(model="models/gemini-2.0-flash")
    
    # 验证ainvoke是否被调用
    assert async_mock.called


@pytest.mark.asyncio
@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="需要GOOGLE_API_KEY")
async def test_gemini_agent_real() -> None:
    """测试使用真实Gemini模型的代理（需要API密钥）。"""
    # 只有在设置了GOOGLE_API_KEY时才运行此测试
    res = await graph.ainvoke(
        {"messages": [("user", "你好，请用一句话介绍一下自己")]},
        {
            "configurable": {
                "system_prompt": "你是一个有帮助的AI助手。",
                "model_provider": "google",
                "gemini_model": "models/gemini-2.0-flash"
            }
        },
    )
    
    # 验证结果
    assert res["messages"][-1].content
    assert isinstance(res["messages"][-1].content, str)
    assert len(res["messages"][-1].content) > 0 