# Gemini 模型示例

本目录包含使用 Google Gemini 模型的示例脚本。

## 前提条件

在运行示例之前，请确保：

1. 已安装所有必要的依赖项：
   ```bash
   pip install -e .
   ```

2. 已设置 Google API 密钥：
   - 在 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取 API 密钥
   - 将密钥添加到 `.env` 文件：
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

## 示例文件

- `gemini_example.py`: 基本的 Gemini 模型使用示例，展示如何配置和使用 Gemini 模型

## 运行示例

```bash
# 运行基本示例
python examples/gemini_example.py
```

## 配置选项

在代码中配置 Gemini 模型时，可以使用以下选项：

```python
config = {
    "configurable": {
        "model_provider": "google",  # 指定使用 Google 作为提供商
        "gemini_model": "models/gemini-2.0-flash"  # 指定 Gemini 模型版本
    }
}
```

可用的 Gemini 模型版本包括：
- `models/gemini-2.0-flash`: 快速响应版本
- `models/gemini-2.0-pro`: 高级版本
- `models/gemini-1.5-flash`: 旧版快速响应版本
- `models/gemini-1.5-pro`: 旧版高级版本

## 故障排除

如果遇到问题：

1. 确保 API 密钥正确且有效
2. 检查是否已安装 `langchain-google-genai` 包
3. 确保网络连接正常，可以访问 Google API 