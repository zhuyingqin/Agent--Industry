"""
子图模块使用示例

此脚本展示了如何使用子图模块处理日志数据，
包括故障分析和问题总结。
"""

from sub_graph import run_graph, graph
from pprint import pprint

def main():
    """运行子图示例"""
    print("=== 子图模块使用示例 ===")
    
    # 创建一些示例日志数据
    raw_logs = [
        {
            "session_id": "123",
            "user_id": "user1",
            "question": "如何使用向量数据库?",
            "timestamp": "2023-03-14T12:00:00Z"
        },
        {
            "session_id": "124",
            "user_id": "user2",
            "question": "LangGraph如何实现子图?",
            "timestamp": "2023-03-14T12:30:00Z"
        }
    ]
    
    print("\n1. 使用便捷函数运行图:")
    result1 = run_graph(raw_logs)
    pprint(result1)
    
    print("\n2. 直接使用图对象运行:")
    result2 = graph.invoke({"raw_logs": raw_logs})
    pprint(result2)
    
    print("\n3. 使用调试模式运行:")
    result3 = run_graph(raw_logs, debug=True)
    # 调试模式下的结果包含更多信息，这里只打印部分
    print(f"结果包含的键: {list(result3.keys())}")
    if "docs" in result3:
        print(f"处理的文档数量: {len(result3['docs'])}")
    if "fa_summary" in result3:
        print(f"故障分析摘要: {result3['fa_summary']}")
    if "report" in result3:
        print(f"生成的报告: {result3['report']}")

if __name__ == "__main__":
    main() 