"""实用工具和辅助函数。"""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def get_message_text(msg: BaseMessage) -> str:
    """获取消息的文本内容。"""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """从完全指定的名称加载聊天模型。

    参数:
        fully_specified_name (str): 格式为'提供商/模型'的字符串。
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    
    # 处理Google Gemini模型
    if provider.lower() == "google":
        return ChatGoogleGenerativeAI(model=model)
    
    # 处理其他模型（Anthropic, OpenAI等）
    return init_chat_model(model, model_provider=provider)
