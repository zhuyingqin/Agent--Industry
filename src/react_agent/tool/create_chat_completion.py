"""
此模块提供了创建聊天完成的工具。
"""

import logging
import os
from typing import Any, Dict, List, Optional

from pydantic import Field
from react_agent.tool.base import BaseTool

logger = logging.getLogger(__name__)

class CreateChatCompletion(BaseTool):
    """创建聊天完成的工具。"""
    
    def __init__(self, **data):
        """初始化CreateChatCompletion工具。"""
        super().__init__(
            name="create_chat_completion",
            description="创建聊天完成并返回结果。",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "要发送给模型的提示文本"
                    }
                },
                "required": ["prompt"]
            },
            **data
        )

    async def execute(self, prompt: str) -> str:
        """执行聊天完成。

        参数:
            prompt: 要发送给模型的提示文本

        返回:
            str: 模型生成的回复
        """
        try:
            # 尝试使用OpenAI API
            try:
                import openai
                
                # 检查是否设置了API密钥
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("未设置OPENAI_API_KEY环境变量，尝试使用其他方法")
                    raise ImportError("未设置OPENAI_API_KEY")
                
                # 创建客户端
                client = openai.OpenAI(api_key=api_key)
                
                # 调用API
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个有用的AI助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000
                )
                
                # 提取回复内容
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                        return response.choices[0].message.content
                    else:
                        return str(response.choices[0])
                else:
                    return str(response)
            
            except (ImportError, Exception) as e:
                logger.warning(f"使用OpenAI API失败: {str(e)}，尝试使用本地模型")
                
                # 尝试使用langchain
                try:
                    from langchain_openai import ChatOpenAI
                    
                    chat = ChatOpenAI(model="gpt-3.5-turbo")
                    result = chat.invoke(prompt)
                    return result.content
                
                except Exception as e:
                    logger.warning(f"使用langchain失败: {str(e)}，尝试使用Anthropic")
                    
                    # 尝试使用Anthropic
                    try:
                        from langchain_anthropic import ChatAnthropic
                        
                        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
                        if not anthropic_api_key:
                            logger.warning("未设置ANTHROPIC_API_KEY环境变量，尝试使用其他方法")
                            raise ImportError("未设置ANTHROPIC_API_KEY")
                        
                        chat = ChatAnthropic(model="claude-3-haiku-20240307")
                        result = chat.invoke(prompt)
                        return result.content
                    
                    except Exception as e:
                        logger.warning(f"使用Anthropic失败: {str(e)}，尝试使用Google")
                        
                        # 尝试使用Google Gemini
                        try:
                            from langchain_google_genai import ChatGoogleGenerativeAI
                            
                            google_api_key = os.environ.get("GOOGLE_API_KEY")
                            if not google_api_key:
                                logger.warning("未设置GOOGLE_API_KEY环境变量，尝试使用其他方法")
                                raise ImportError("未设置GOOGLE_API_KEY")
                            
                            chat = ChatGoogleGenerativeAI(model="gemini-pro")
                            result = chat.invoke(prompt)
                            return result.content
                        
                        except Exception as e:
                            logger.warning(f"使用Google Gemini失败: {str(e)}，尝试使用本地模型")
                            
                            # 尝试使用本地模型
                            try:
                                import torch
                                from transformers import AutoModelForCausalLM, AutoTokenizer
                                
                                # 使用较小的模型，适合本地运行
                                model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                                
                                tokenizer = AutoTokenizer.from_pretrained(model_name)
                                model = AutoModelForCausalLM.from_pretrained(
                                    model_name, 
                                    torch_dtype=torch.float16,
                                    device_map="auto"
                                )
                                
                                # 准备输入
                                messages = [
                                    {"role": "system", "content": "你是一个有用的AI助手。"},
                                    {"role": "user", "content": prompt}
                                ]
                                
                                # 将消息格式化为模型可接受的格式
                                input_text = ""
                                for msg in messages:
                                    if msg["role"] == "system":
                                        input_text += f"<|system|>\n{msg['content']}\n"
                                    elif msg["role"] == "user":
                                        input_text += f"<|user|>\n{msg['content']}\n"
                                    elif msg["role"] == "assistant":
                                        input_text += f"<|assistant|>\n{msg['content']}\n"
                                
                                input_text += "<|assistant|>\n"
                                
                                # 生成回复
                                inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
                                outputs = model.generate(
                                    inputs["input_ids"],
                                    max_new_tokens=500,
                                    temperature=0.7,
                                    do_sample=True
                                )
                                
                                # 解码并返回生成的文本
                                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                                
                                # 提取助手的回复
                                assistant_response = generated_text.split("<|assistant|>\n")[-1].strip()
                                return assistant_response
                            
                            except Exception as e:
                                logger.warning(f"使用本地模型失败: {str(e)}，返回简单回复")
                                
                                # 如果所有方法都失败，返回一个简单的回复
                                return f"""
我收到了你的问题: '{prompt}'。

由于无法连接到任何外部或本地模型，我无法生成详细回复。这可能是由于以下原因：

1. 未设置任何API密钥（OpenAI、Anthropic、Google）
2. 网络连接问题
3. 本地环境不支持运行模型

请尝试以下解决方案：
- 设置OPENAI_API_KEY、ANTHROPIC_API_KEY或GOOGLE_API_KEY环境变量
- 检查网络连接
- 安装必要的依赖包（openai、langchain-openai、langchain-anthropic、langchain-google-genai、transformers、torch）

或者，您可以直接向我提问，我会尽力提供帮助。
"""
        
        except Exception as e:
            logger.error(f"创建聊天完成时出错: {str(e)}")
            return f"生成回复时出错: {str(e)}"
