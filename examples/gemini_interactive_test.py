#!/usr/bin/env python
"""
Gemini模型交互式测试

此脚本提供了一个交互式界面，允许用户输入问题并获取Gemini模型的回答。
在运行此脚本之前，请确保已设置GOOGLE_API_KEY环境变量。

使用方法:
    python examples/gemini_interactive_test.py
"""

import asyncio
import os
from dotenv import load_dotenv

from react_agent import get_graph

# 加载环境变量
load_dotenv()

# 检查是否设置了GOOGLE_API_KEY
if not os.environ.get("GOOGLE_API_KEY"):
    print("错误: 未设置GOOGLE_API_KEY环境变量")
    print("请在.env文件中添加GOOGLE_API_KEY=your_api_key或直接设置环境变量")
    exit(1)

# 获取图实例
graph = get_graph()

async def ask_question(question, config):
    """向Gemini模型提问并获取回答。"""
    result = await graph.ainvoke(
        {"messages": [("user", question)]},
        config,
    )
    return result["messages"][-1].content


async def main():
    """运行交互式测试。"""
    print("Gemini模型交互式测试")
    print("输入'退出'或'exit'结束测试")
    print("-----------------------------------")
    
    # 配置使用Gemini模型
    config = {
        "configurable": {
            "system_prompt": "你是一个有帮助的AI助手，专注于提供简洁明了的回答。",
            "model_provider": "google",
            "gemini_model": "models/gemini-2.0-flash"
        }
    }
    
    # 交互式循环
    conversation_history = []
    
    while True:
        # 获取用户输入
        user_question = input("\n请输入您的问题: ")
        
        # 检查是否退出
        if user_question.lower() in ["退出", "exit", "quit", "q"]:
            print("谢谢使用，再见！")
            break
        
        print("正在思考...")
        
        # 调用代理
        answer = await ask_question(user_question, config)
        
        # 打印结果
        print("\nGemini回答:")
        print(answer)
        
        # 保存对话历史
        conversation_history.append({"question": user_question, "answer": answer})
    
    # 打印对话摘要
    if conversation_history:
        print("\n-----------------------------------")
        print(f"本次对话共进行了 {len(conversation_history)} 轮")


if __name__ == "__main__":
    asyncio.run(main()) 