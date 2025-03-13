#!/usr/bin/env python
"""
测试所有工具

此脚本测试所有工具是否能正常绑定到Agent上，并执行简单的查询。
"""

import asyncio
import os
from dotenv import load_dotenv

from react_agent import get_graph
from react_agent.all_tools import TOOLS

# 加载环境变量
load_dotenv()

# 检查必要的API密钥
if not os.environ.get("GOOGLE_API_KEY"):
    print("警告: 未设置GOOGLE_API_KEY环境变量，某些工具可能无法正常工作")

# 获取图实例
graph = get_graph()

async def test_tools():
    """测试所有工具是否能正常工作。"""
    print("测试所有工具")
    print("=" * 50)
    
    # 列出所有可用的工具
    print(f"共有 {len(TOOLS)} 个工具可用:")
    for i, tool in enumerate(TOOLS, 1):
        tool_name = getattr(tool, "name", tool.__name__ if hasattr(tool, "__name__") else str(tool))
        print(f"{i}. {tool_name}")
    
    print("\n" + "=" * 50)
    
    # 配置使用Gemini模型
    config = {
        "configurable": {
            "system_prompt": "你是一个有帮助的AI助手，专注于提供准确的信息。你可以使用各种工具来完成任务。",
            "model_provider": "google",
            "gemini_model": "models/gemini-2.0-flash"
        }
    }
    
    # 测试查询
    questions = [
        "请编写一个Python程序，创建一个简单的计算器类，支持加减乘除四种基本运算。然后使用python_execute工具执行这个程序，确保在执行时展示计算结果。请明确使用python_execute工具，不要只是生成代码。"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n测试 {i}/{len(questions)}: {question}")
        print("正在处理...")
        
        try:
            # 调用代理
            result = await graph.ainvoke(
                {"messages": [("user", question)]},
                config,
            )
            
            # 打印结果
            print("\nAI回答:")
            print(result["messages"][-1].content)
        except Exception as e:
            print(f"错误: {e}")
        
        print("\n" + "-" * 50)


async def main():
    """运行所有测试。"""
    await test_tools()
    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main()) 