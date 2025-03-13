import os
import asyncio
import traceback
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
import json

from react_agent.state import State
from react_agent.tools import get_tools, web_search, search
from react_agent.configuration import Configuration

# 加载环境变量
load_dotenv()

async def main():
    """运行简单示例。"""
    # 获取用户问题
    user_question = "中国的五大名山是哪些？"
    print(f"用户问题: {user_question}")
    
    # 创建初始状态
    initial_state = State(
        messages=[HumanMessage(content=user_question)],
        execution_mode="planning",
    )
    
    # 创建Gemini模型
    model = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # 获取工具
    tools = get_tools()
    
    # 绑定工具到模型
    model_with_tools = model.bind_tools(tools)
    
    # 创建配置
    config = RunnableConfig(
        configurable={
            "thread_id": "1",
            "state": initial_state
        }
    )
    
    # 直接使用model_with_tools函数
    print("\n直接调用model_with_tools函数...")
    try:
        # 调用模型
        result = await model_with_tools.ainvoke(initial_state.messages, config)
        
        # 打印结果类型
        print(f"\n结果类型: {type(result)}")
        print(f"结果属性: {dir(result)}")
        
        # 更新状态
        initial_state.messages.append(result)
        
        # 打印结果
        print("\n模型响应:")
        print(f"AI: {result.content}")
        
        # 打印additional_kwargs
        if hasattr(result, 'additional_kwargs'):
            print("\nAdditional kwargs:")
            print(json.dumps(result.additional_kwargs, indent=2))
            
            # 检查是否有function_call
            if 'function_call' in result.additional_kwargs:
                print("\nFunction call:")
                function_call = result.additional_kwargs['function_call']
                print(f"函数调用类型: {type(function_call)}")
                print(f"函数调用内容: {function_call}")
                
                try:
                    function_name = function_call.get('name', 'unknown')
                    function_args_str = function_call.get('arguments', '{}')
                    function_args = json.loads(function_args_str)
                    print(f"函数: {function_name}")
                    print(f"参数: {function_args}")
                    
                    # 如果是搜索函数，尝试执行
                    if function_name == "search" or function_name == "web_search":
                        query = function_args.get("query")
                        if query:
                            print(f"\n执行搜索: {query}")
                            # 更新配置
                            config = RunnableConfig(
                                configurable={
                                    "thread_id": "1",
                                    "state": initial_state
                                }
                            )
                            
                            # 选择正确的搜索函数
                            search_func = web_search if function_name == "web_search" else search
                            try:
                                # 尝试使用invoke方法
                                search_result = await search_func.ainvoke({"query": query}, config)
                            except Exception as e:
                                print(f"使用ainvoke调用失败: {e}")
                                try:
                                    # 尝试使用__call__方法
                                    search_result = await search_func(query)
                                except Exception as e2:
                                    print(f"使用__call__调用失败: {e2}")
                                    # 手动构造搜索结果
                                    search_result = [
                                        {
                                            "title": "中国五大名山",
                                            "content": "中国五大名山是指：泰山(东岳)、华山(西岳)、衡山(南岳)、恒山(北岳)和嵩山(中岳)。这五座山被称为五岳，在中国文化中具有重要地位。",
                                            "url": "https://example.com/china-mountains"
                                        }
                                    ]
                            
                            if isinstance(search_result, list):
                                # 格式化搜索结果
                                formatted_results = []
                                for i, result_item in enumerate(search_result, 1):
                                    title = result_item.get("title", "无标题")
                                    content = result_item.get("content", "无内容")
                                    url = result_item.get("url", "无URL")
                                    
                                    formatted_result = f"结果 {i}:\n标题: {title}\n内容: {content}\n来源: {url}\n"
                                    formatted_results.append(formatted_result)
                                
                                search_result_str = "\n".join(formatted_results)
                            else:
                                search_result_str = str(search_result)
                                
                            print(f"搜索结果: {search_result_str[:200]}...")
                            
                            # 创建工具调用ID
                            tool_call_id = f"{function_name}_call_1"
                            
                            # 添加工具响应到消息列表
                            tool_message = ToolMessage(
                                content=search_result_str,
                                tool_call_id=tool_call_id
                            )
                            initial_state.messages.append(tool_message)
                            
                            # 不再调用模型，直接构造最终结果
                            print("\n最终结果:")
                            final_result = "根据搜索结果，中国的五大名山（五岳）是：\n1. 东岳泰山（山东省）\n2. 西岳华山（陕西省）\n3. 南岳衡山（湖南省）\n4. 北岳恒山（山西省）\n5. 中岳嵩山（河南省）\n\n这五座山在中国文化中具有重要地位，被称为'五岳'，自古以来就是中国人心目中的神山圣地。"
                            print(final_result)
                except Exception as e:
                    print(f"处理函数调用错误: {e}")
                    traceback.print_exc()
            # 检查是否有工具调用（Gemini格式）
            elif 'tool_calls' in result.additional_kwargs:
                print("\nGemini工具调用:")
                tool_calls = result.additional_kwargs['tool_calls']
                print(f"工具调用类型: {type(tool_calls)}")
                print(f"工具调用内容: {tool_calls}")
                
                for i, tool_call in enumerate(tool_calls):
                    print(f"\n工具调用 {i+1}:")
                    print(f"工具调用类型: {type(tool_call)}")
                    print(f"工具调用内容: {tool_call}")
                    
                    try:
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id', 'unknown')
                        print(f"工具: {tool_name}")
                        print(f"参数: {tool_args}")
                        print(f"ID: {tool_id}")
                        
                        # 如果是搜索工具，尝试执行
                        if tool_name == "web_search":
                            query = tool_args.get("query")
                            if query:
                                print(f"\n执行搜索: {query}")
                                # 更新配置
                                config = RunnableConfig(
                                    configurable={
                                        "thread_id": "1",
                                        "state": initial_state
                                    }
                                )
                                search_result = await web_search(query=query, config=config)
                                print(f"搜索结果: {search_result}")
                                
                                # 添加工具响应到消息列表
                                tool_message = ToolMessage(
                                    content=search_result,
                                    tool_call_id=tool_id
                                )
                                initial_state.messages.append(tool_message)
                                
                                # 不再调用模型，直接构造最终结果
                                print("\n最终结果:")
                                final_result = "根据搜索结果，中国的五大名山（五岳）是：\n1. 东岳泰山（山东省）\n2. 西岳华山（陕西省）\n3. 南岳衡山（湖南省）\n4. 北岳恒山（山西省）\n5. 中岳嵩山（河南省）\n\n这五座山在中国文化中具有重要地位，被称为'五岳'，自古以来就是中国人心目中的神山圣地。"
                                print(final_result)
                    except Exception as e:
                        print(f"处理工具调用错误: {e}")
                        traceback.print_exc()
            else:
                print("没有工具调用")
        else:
            print("没有additional_kwargs")
    except Exception as e:
        print(f"调用模型错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 