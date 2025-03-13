"""定义代理的可配置参数。"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional, Literal

from langchain_core.runnables import RunnableConfig, ensure_config

from react_agent import prompts


@dataclass(kw_only=True)
class Configuration:
    """代理的配置。"""

    system_prompt: str = field(
        default=prompts.SYSTEM_PROMPT,
        metadata={
            "description": "用于代理交互的系统提示。"
            "这个提示设置了代理的上下文和行为。"
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="google/gemini-2.0-flash",
        metadata={
            "description": "用于代理主要交互的语言模型的名称。"
            "应该采用以下形式：提供商/模型名称。"
            "支持的提供商包括：anthropic, google, openai等。"
        },
    )
    
    model_provider: Literal["anthropic", "google", "openai"] = field(
        default="gemini",
        metadata={
            "description": "语言模型提供商。"
            "目前支持：anthropic (Claude), google (Gemini), openai (GPT)。"
        },
    )
    
    gemini_model: str = field(
        default="models/gemini-2.0-flash",
        metadata={
            "description": "当model_provider为'google'时使用的Gemini模型版本。"
            "可选值包括：gemini-1.5-pro-latest, gemini-1.5-flash-latest等。"
        },
    )

    max_search_results: int = field(
        default=10,
        metadata={
            "description": "每个搜索查询返回的最大搜索结果数量。"
        },
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """从RunnableConfig对象创建Configuration实例。"""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
