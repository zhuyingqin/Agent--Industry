# Agent--Industry

基于LangGraph的智能代理系统，专为行业应用场景设计。本项目基于ReAct代理模式，通过LangGraph实现，可以灵活扩展到多种工具和行业应用场景。

![智能代理系统架构](./static/studio_ui.png)

## 功能介绍

Agent--Industry智能代理系统：

1. 接收用户**查询**作为输入
2. 分析查询并决定采取的行动
3. 使用可用工具执行所选操作
4. 观察操作结果
5. 重复步骤2-4，直到能够提供最终答案

系统默认配置了一套基本工具，但可以根据不同行业和应用场景轻松扩展自定义工具。

### 增强的规划与执行能力

代理系统支持增强的工作流程，具有明确的规划和逐步执行功能：

1. **规划阶段**：代理首先分析用户的请求，创建详细的执行计划，将复杂任务分解为可管理的步骤。
2. **执行阶段**：代理按顺序执行每个步骤，使用适当的工具完成每个步骤并跟踪进度。
3. **响应阶段**：完成所有步骤后，代理总结结果并提供全面的答案。

这种结构化方法帮助代理更有效地处理复杂任务：
- 将复杂问题分解为更小、更易管理的步骤
- 在执行单个步骤的同时保持对总体目标的关注
- 提供代理推理过程的更好可见性
- 确保解决用户请求的所有方面

### 可用工具

代理系统配备了多种内置工具：
- **搜索**：使用Tavily的网络搜索功能
- **Python执行**：执行Python代码片段
- **Bash**：运行shell命令
- **学术搜索**：在Google Scholar上搜索学术文献并总结发现
- **规划**：为复杂任务创建和管理执行计划

### 浏览器搜索功能

我们添加了强大的浏览器搜索功能，允许代理：

1. **自动识别搜索输入字段**：它可以识别各种常见的搜索输入字段，包括来自百度、谷歌和GitHub等流行网站的字段。
2. **输入搜索词**：它自动将用户指定的搜索词输入到搜索输入字段中。
3. **提交搜索请求**：它支持点击搜索按钮或提交表单来执行搜索。
4. **检索搜索结果**：它等待搜索结果加载并返回页面内容。

#### 使用方法

```python
# 创建BrowserUseTool实例
browser_tool = BrowserUseTool()

# 执行搜索
result = await browser_tool.execute(
    url='https://www.baidu.com',  # 要搜索的网站URL
    task='在百度上搜索Python教程',  # 任务描述
    action='search',  # 指定操作为搜索
    parameters={'search_query': 'Python教程'}  # 搜索查询词
)
```

#### 支持的网站

当前版本已在以下网站上进行了测试：

- **百度**：它可以准确识别搜索输入字段并执行搜索操作。
- **GitHub**：它可以识别搜索输入字段和提交按钮来执行搜索操作。
- **谷歌**：它可以通过识别搜索元素，使用通用方法执行搜索操作。

## 开始使用

假设你已经安装了LangGraph Studio，按照以下步骤设置：

1. 运行设置脚本安装所有依赖项并设置环境变量：

```bash
bash setup.sh
```

或手动：

```bash
cp .env.example .env
```

2. 在`.env`文件中定义所需的API密钥。

主要使用的搜索工具是[Tavily](https://tavily.com/)。在[这里](https://app.tavily.com/sign-in)创建API密钥。

对于学术搜索工具，你需要[SerpAPI](https://serpapi.com/)的API密钥。将其添加到你的`.env`文件中：

```
SERPAPI_API_KEY=your-serpapi-api-key
```

### 设置模型

`model`的默认值如下：

```yaml
model: anthropic/claude-3-5-sonnet-20240620
```

按照以下说明进行设置，或选择其他选项。

#### Anthropic

使用Anthropic的聊天模型：

1. 如果你还没有，请注册[Anthropic API密钥](https://console.anthropic.com/)。
2. 获得API密钥后，将其添加到你的`.env`文件中：

```
ANTHROPIC_API_KEY=your-api-key
```

#### OpenAI

使用OpenAI的聊天模型：

1. 注册[OpenAI API密钥](https://platform.openai.com/signup)。
2. 获得API密钥后，将其添加到你的`.env`文件中：
```
OPENAI_API_KEY=your-api-key
```

3. 根据需要自定义代码。
4. 在LangGraph Studio中打开文件夹！

## 如何自定义

1. **添加新工具**：通过在`src/react_agent/tools.py`中添加新工具来扩展代理的功能。这些可以是执行特定任务的任何Python函数。
2. **选择不同的模型**：我们默认使用Anthropic的Claude 3 Sonnet。你可以通过配置使用`provider/model-name`格式选择兼容的聊天模型。例如：`openai/gpt-4-turbo-preview`。
3. **自定义提示**：我们在`src/react_agent/prompts.py`中提供了默认的系统提示。你可以在Studio中通过配置轻松更新它。

你还可以通过以下方式快速扩展此模板：

- 在`src/react_agent/graph.py`中修改代理的推理过程。
- 调整ReAct循环或向代理的决策过程添加额外步骤。

## 开发

在迭代图形时，你可以编辑过去的状态并从过去的状态重新运行应用程序以调试特定节点。本地更改将通过热重载自动应用。尝试在代理调用工具之前添加中断，更新`src/react_agent/configuration.py`中的默认系统消息以采用角色，或添加其他节点和边！

后续请求将附加到同一线程。你可以使用右上角的`+`按钮创建一个全新的线程，清除之前的历史记录。

你可以在[LangGraph](https://github.com/langchain-ai/langgraph)找到最新的（正在建设中的）文档，包括示例和其他参考资料。使用这些指南可以帮助你选择适合在这里适应你的用例的正确模式。

LangGraph Studio还与[LangSmith](https://smith.langchain.com/)集成，用于更深入的跟踪和与团队成员的协作。