#!/usr/bin/env python
"""
Gemini模型使用示例

此脚本展示了如何使用Gemini模型与React Agent进行交互。
在运行此脚本之前，请确保已设置GOOGLE_API_KEY环境变量。

使用方法:
    python examples/gemini_example.py
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
import inspect

from react_agent import get_graph
from react_agent.state import State

# 加载环境变量
load_dotenv()

# 检查是否设置了GOOGLE_API_KEY
if not os.environ.get("GOOGLE_API_KEY"):
    print("错误: 未设置GOOGLE_API_KEY环境变量")
    print("请在.env文件中添加GOOGLE_API_KEY=your_api_key或直接设置环境变量")
    exit(1)

# 获取图
graph = get_graph()

def main():
    """运行示例。"""
    # 获取用户问题
    user_question = "中国的五大名山是哪些？"
    print(f"用户问题: {user_question}")
    
    # 创建初始状态
    initial_state = State(
        messages=[HumanMessage(content=user_question)],
        execution_mode="planning",
    )
    
    # 检查图对象的属性和方法
    print("\n检查图对象的属性和方法:")
    print(f"图对象类型: {type(graph)}")
    print(f"图对象属性: {dir(graph)}")
    
    # 检查图对象是否有特定方法
    methods_to_check = [
        "invoke", "ainvoke", "stream", "astream", "run", "arun",
        "get_entry_point", "get_node", "get_next_node", "get_edges"
    ]
    
    print("\n检查图对象的特定方法:")
    for method in methods_to_check:
        has_method = hasattr(graph, method)
        print(f"- {method}: {'存在' if has_method else '不存在'}")
        if has_method:
            method_obj = getattr(graph, method)
            try:
                signature = inspect.signature(method_obj)
                print(f"  签名: {signature}")
            except (ValueError, TypeError):
                print(f"  无法获取签名")
    
    try:
        # 尝试使用最基本的方法
        print("\n尝试使用最基本的方法...")
        
        # 检查是否有入口点属性
        if hasattr(graph, "entry_point"):
            entry_point = graph.entry_point
            print(f"入口点: {entry_point}")
        else:
            print("图对象没有entry_point属性")
            
        # 检查是否有nodes属性
        if hasattr(graph, "nodes"):
            print(f"节点: {graph.nodes}")
        else:
            print("图对象没有nodes属性")
            
        # 检查是否有edges属性
        if hasattr(graph, "edges"):
            print(f"边: {graph.edges}")
        else:
            print("图对象没有edges属性")
        
        print("\n无法执行图，请检查langgraph版本和代码兼容性")
        
    except Exception as e:
        print(f"执行图错误: {e}")
        print("请检查langgraph版本和代码兼容性")

if __name__ == "__main__":
    main() 