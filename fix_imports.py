#!/usr/bin/env python
"""
修复工具文件中的导入路径

此脚本将所有工具文件中的 'app' 相关导入路径替换为 'react_agent' 相关路径
"""

import os
import re

# 工具目录路径
TOOL_DIR = "src/react_agent/tool"

# 要替换的模式列表
PATTERNS = [
    (r"from app\.tool", "from react_agent.tool"),
    (r"import app\.tool", "import react_agent.tool"),
    (r"from app\.", "from react_agent."),
    (r"import app\.", "import react_agent."),
]

# 遍历工具目录中的所有 Python 文件
for filename in os.listdir(TOOL_DIR):
    if filename.endswith(".py"):
        filepath = os.path.join(TOOL_DIR, filename)
        
        # 读取文件内容
        with open(filepath, "r") as file:
            content = file.read()
        
        # 应用所有替换模式
        new_content = content
        for pattern, replacement in PATTERNS:
            new_content = re.sub(pattern, replacement, new_content)
        
        # 如果内容有变化，写回文件
        if new_content != content:
            with open(filepath, "w") as file:
                file.write(new_content)
            print(f"已修复文件: {filepath}")

print("所有文件导入路径修复完成！") 