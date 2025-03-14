# 子图模块 (Sub Graph)

这个模块提供了用于构建复杂工作流的可组合子图，基于LangGraph实现。

## 功能概述

该模块包含三个主要组件：

1. **故障分析子图 (Failure Analysis)**：分析日志中的失败案例，生成故障摘要。
2. **问题总结子图 (Question Summarization)**：总结用户问题，生成报告并格式化。
3. **入口图 (Entry Graph)**：协调上述子图的执行，处理原始日志数据。

## 文件结构

- `__init__.py` - 模块入口点，导出主要组件
- `state.py` - 定义各个子图的状态类型
- `graph.py` - 实现子图和入口图的逻辑
- `example.py` - 使用示例
- `README.md` - 本文档

## 使用方法

### 基本用法

```python
from sub_graph import run_graph

# 准备原始日志数据
raw_logs = [
    {"session_id": "123", "user_id": "user1", "question": "如何使用向量数据库?"},
    {"session_id": "124", "user_id": "user2", "question": "LangGraph如何实现子图?"}
]

# 运行图处理数据
result = run_graph(raw_logs)
print(result)
```

### 高级用法

```python
from sub_graph import graph, fa_builder, qs_builder

# 直接使用图对象
result = graph.invoke({"raw_logs": raw_logs})

# 使用调试模式
debug_result = graph.invoke({"raw_logs": raw_logs}, debug=True)

# 单独使用故障分析子图
fa_result = fa_builder.compile().invoke({"docs": processed_docs})

# 单独使用问题总结子图
qs_result = qs_builder.compile().invoke({"docs": processed_docs})
```

## 自定义扩展

你可以通过修改现有节点或添加新节点来扩展子图功能：

```python
from sub_graph import entry_builder
from langgraph.graph import END

# 添加新节点
def new_processing_step(state):
    # 处理逻辑
    return {"new_result": processed_data}

entry_builder.add_node("new_step", new_processing_step)
entry_builder.add_edge("convert_logs_to_docs", "new_step")
entry_builder.add_edge("new_step", END)

# 重新编译图
custom_graph = entry_builder.compile()
```

## 运行示例

执行示例脚本查看子图的运行效果：

```bash
python -m src.sub_graph.example
``` 