#!/usr/bin/env python
"""
Gemini模型工具调用测试

此脚本测试Gemini模型使用工具的能力，特别是搜索工具。
在运行此脚本之前，请确保已设置GOOGLE_API_KEY和TAVILY_API_KEY环境变量。

使用方法:
    python examples/gemini_tools_test.py
"""

import asyncio
import os
from dotenv import load_dotenv

from react_agent import get_graph

# 加载环境变量
load_dotenv()

# 检查必要的API密钥
if not os.environ.get("GOOGLE_API_KEY"):
    print("错误: 未设置GOOGLE_API_KEY环境变量")
    print("请在.env文件中添加GOOGLE_API_KEY=your_api_key或直接设置环境变量")
    exit(1)

if not os.environ.get("TAVILY_API_KEY"):
    print("错误: 未设置TAVILY_API_KEY环境变量")
    print("请在.env文件中添加TAVILY_API_KEY=your_api_key或直接设置环境变量")
    exit(1)

# 获取图实例
graph = get_graph()

async def test_search_tool():
    """测试搜索工具。"""
    print("测试Gemini模型使用搜索工具")
    print("-----------------------------------")
    
    # 配置使用Gemini模型
    config = {
        "configurable": {
            "system_prompt": "你是一个有帮助的AI助手，专注于提供准确的信息。如果你不确定答案，请使用搜索工具查找最新信息。",
            "model_provider": "google",
            "gemini_model": "models/gemini-2.0-flash",
            "max_search_results": 3
        }
    }
    
    # 需要搜索的问题
    questions = [
        "2024年奥运会在哪里举办？",
        "最新的iPhone型号是什么？",
        "中国最近发射的航天器有哪些？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n测试 {i}/{len(questions)}: {question}")
        print("正在处理...")
        
        # 调用代理
        result = await graph.ainvoke(
            {"messages": [("user", question)]},
            config,
        )
        
        # 打印结果
        print("\nGemini回答:")
        print(result["messages"][-1].content)
        print("\n" + "-" * 50)


async def main():
    """运行所有测试。"""
    print("Gemini模型工具调用测试")
    print("=" * 50)
    
    await test_search_tool()
    
    print("\n所有测试完成！")


if __name__ == "__main__":
    asyncio.run(main()) 