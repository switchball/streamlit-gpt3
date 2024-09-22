# streamlit-gpt3
[![在 Streamlit 中打开][share_badge]][share_link] [![GitHub][github_badge]][github_link]

Streamlit-GPT3 是一个基于 Streamlit 创建的网页预览工具界面。此工具通过 OpenAI 的 GPT3 API 提供多种问答任务。

## 特性

* **预设身份** - 从多个预设身份中选择，以特定的人设生成文本。您还可以自定义提示并获取示例对话。
* **对话回应** - 输入提示，AI 将像进行对话一样作出回应。
* **参数条件** - 通过修改各种参数来自定义生成文本的上下文和输出。
* **模型选择** - 从一系列针对不同应用场景优化的 GPT-3 模型中选择，默认使用 Qwen，也支持其他模型。

## 高级特性
* **回溯最后消息** - 如果需要编辑您的问题，可以回溯最后发送给 AI 的消息。
* **响应编辑** - 在特定情况下引导其答案。根据需求定制和指导与助手的对话。
* **链接分享** - 通过唯一链接与他人共享生成的文本。同时提供更快捷的保存/加载方式。
* **节省 Token** - 通过设置对话轮数来减少 Token 使用量，从而支持更长的对话。

## 安装

开始之前，请克隆仓库并安装所需包：

```
git clone https://github.com/switchball/streamlit-gpt3.git
cd streamlit-gpt3
pip install -r requirements.txt
```

根据你使用的模型，准备 Qwen / OpenAI 的密钥

## 准备您的 Qwen 密钥

1. 在仓库根目录下创建一个名为 `.streamlit` 的文件夹。
2. 在 `.streamlit` 文件夹内创建一个 `secrets.toml` 文件。
3. 在配置文件中写入如下，其中 DASH_API_KEY 的获取可参考 [阿里云官方文档](https://help.aliyun.com/zh/dashscope/developer-reference/acquisition-and-configuration-of-api-key)
```
[Qwen]
DASHSCOPE_API_KEY = "sk-xxx"
```

## 准备您的 OpenAI 密钥

1. 在仓库根目录下创建一个名为 `.streamlit` 的文件夹。
2. 在 `.streamlit` 文件夹内创建一个 `secrets.toml` 文件。
3. 在配置文件中写入一行 `OPENAI_API_KEY = "sk-xxxx"`，以便 Streamlit 能够将其加载为 `st.secrets`。

## 使用方法

运行以下命令启动 Streamlit 应用：
```
streamlit run app.py
```


应用启动后，您可以通过访问浏览器中的 `localhost:8501` 来使用它。

## 贡献

欢迎贡献！如果您希望为此项目做出贡献，请提交拉取请求。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件获取更多信息。

[share_badge]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[share_link]: https://playgpt3.streamlit.app/

[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/switchball/streamlit-gpt3