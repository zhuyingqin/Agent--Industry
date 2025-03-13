#!/usr/bin/env python
"""
Gemini模型多轮对话测试

此脚本测试Gemini模型在多轮对话中的表现，模拟一个完整的对话流程。
在运行此脚本之前，请确保已设置GOOGLE_API_KEY环境变量。

使用方法:
    python examples/gemini_conversation_test.py
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from react_agent import get_graph

# 加载环境变量
load_dotenv()

# 检查必要的API密钥
if not os.environ.get("GOOGLE_API_KEY"):
    print("错误: 未设置GOOGLE_API_KEY环境变量")
    print("请在.env文件中添加GOOGLE_API_KEY=your_api_key或直接设置环境变量")
    exit(1)

# 获取图实例
graph = get_graph()

async def simulate_conversation():
    """模拟一个多轮对话。"""
    print("模拟多轮对话测试")
    print("-----------------------------------")
    
    # 配置使用Gemini模型
    config = {
        "configurable": {
            "system_prompt": "你是一个有帮助的AI助手，专注于提供友好、有用的回答。请记住用户之前提到的信息，保持对话的连贯性。",
            "model_provider": "google",
            "gemini_model": "models/gemini-2.0-flash"
        }
    }
    
    # 初始化对话状态
    conversation_state = {"messages": []}
    
    # 预设的对话流程
    conversation_flow = [
        "你好，我想了解一下人工智能。",
        "能给我介绍一下机器学习和深度学习的区别吗？",
        "谢谢，那么神经网络是如何工作的？",
        "这些技术在现实生活中有哪些应用？",
        "我对自然语言处理很感兴趣，能详细说说吗？"
    ]
    
    # 执行对话
    for i, user_message in enumerate(conversation_flow, 1):
        print(f"\n轮次 {i}/{len(conversation_flow)}")
        print(f"用户: {user_message}")
        
        # 添加用户消息
        conversation_state["messages"].append(HumanMessage(content=user_message))
        
        # 调用代理
        result = await graph.ainvoke(
            conversation_state,
            config,
        )
        
        # 更新对话状态
        conversation_state = result
        
        # 打印AI回答
        print(f"AI: {result['messages'][-1].content}")
        
        # 在轮次之间添加分隔线
        if i < len(conversation_flow):
            print("\n" + "-" * 30)


async def main():
    """运行所有测试。"""
    print("Gemini模型多轮对话测试")
    print("=" * 50)
    
    await simulate_conversation()
    
    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main()) 