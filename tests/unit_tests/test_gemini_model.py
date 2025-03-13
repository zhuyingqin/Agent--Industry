"""测试Gemini模型配置和加载。"""

import os
import pytest
from unittest.mock import patch, MagicMock

from react_agent.configuration import Configuration
from react_agent.utils import load_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI


def test_gemini_configuration() -> None:
    """测试Gemini配置是否正确设置。"""
    # 创建一个使用Gemini的配置
    config = Configuration(
        model_provider="google",
        gemini_model="models/gemini-2.0-flash"
    )
    
    # 验证配置
    assert config.model_provider == "google"
    assert config.gemini_model == "models/gemini-2.0-flash"


@patch("react_agent.utils.ChatGoogleGenerativeAI")
def test_load_gemini_model(mock_chat_google: MagicMock) -> None:
    """测试Gemini模型是否正确加载。"""
    # 设置模拟返回值
    mock_instance = MagicMock()
    mock_chat_google.return_value = mock_instance
    
    # 调用加载函数
    model = load_chat_model("google/models/gemini-2.0-flash")
    
    # 验证是否正确调用了ChatGoogleGenerativeAI
    mock_chat_google.assert_called_once_with(model="models/gemini-2.0-flash")
    assert model == mock_instance


@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="需要GOOGLE_API_KEY")
def test_real_gemini_model_creation() -> None:
    """测试实际的Gemini模型创建（需要API密钥）。"""
    # 只有在设置了GOOGLE_API_KEY时才运行此测试
    model = load_chat_model("google/models/gemini-2.0-flash")
    assert isinstance(model, ChatGoogleGenerativeAI)
    assert model.model == "models/gemini-2.0-flash" 