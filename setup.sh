#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始安装 React Agent 依赖...${NC}"

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}检测到 Python 版本: ${python_version}${NC}"

# 检查是否需要创建虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}创建虚拟环境失败，请检查 Python 版本是否 >= 3.11${NC}"
        exit 1
    fi
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}安装依赖失败，请检查网络连接或手动安装${NC}"
    exit 1
fi

# 安装 Playwright 浏览器
echo -e "${YELLOW}安装 Playwright 浏览器...${NC}"
playwright install
if [ $? -ne 0 ]; then
    echo -e "${RED}安装 Playwright 浏览器失败，请手动安装：playwright install${NC}"
    exit 1
fi

# 创建 .env 文件
echo -e "${YELLOW}创建 .env 文件...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << EOF
# API 密钥
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here

# 其他配置
EOF
    echo -e "${GREEN}.env 文件已创建，请编辑文件添加您的 API 密钥${NC}"
else
    echo -e "${YELLOW}.env 文件已存在，跳过创建${NC}"
fi

echo -e "${GREEN}安装完成！${NC}"
echo -e "${YELLOW}请确保在 .env 文件中设置了必要的 API 密钥：${NC}"
echo -e "  - GOOGLE_API_KEY: 用于 Google Gemini 模型和 Google 搜索"
echo -e "  - SERPAPI_API_KEY: 用于 Google Scholar 搜索"
echo -e "${YELLOW}使用方法：${NC}"
echo -e "  1. 激活虚拟环境：source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)"
echo -e "  2. 运行测试脚本：python examples/test_all_tools.py"
echo -e "  3. 或者运行特定工具测试：python examples/test_code_execution.py" 