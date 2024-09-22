# streamlit-gpt3
[![Open in Streamlit][share_badge]][share_link] [![GitHub][github_badge]][github_link]

Streamlit-GPT3 is a web-based preview tool interface created using Streamlit. This tool offers  several Q&amp;A task, provided by OpenAI GPT3 API.

## Features

* **Preset Identities** - Select from various preset identities to generate text with a specific persona. You can also customize the prompt and get example dialogues.
* **Conversation Response** - Input prompts and the AI will respond as if engaged in a conversation.
* **Parameter Conditions** - Customize the context and output of the generated text by modifying various parameters.
* **Model Selection** - Choose from a range of GPT-3 models tailored to suit your application.  Default is GPT-3.5-Turbo, davinci-model is also supported.

## Features (Advanced)
* **Recall Last Message** - You can recall the last message sent to the AI if you would like to edit your question.
* **Response Editing** - Guide its answers in specific situations. Customize and direct the conversation with the assistant to best fit your needs.
* **Link Sharing** - Share the generated text with others via a unique link. Also a faster alternative of save/load.
* **Token Saving** - Reduce token usages by setting the number of conversation, in order to support longer conversations. 

## Installation

To get started, clone the repository and install the required packages:
```
git clone https://github.com/switchball/streamlit-gpt3.git
cd streamlit-gpt3
pip install -r requirements.txt
```

## Prepare your OpenAI key

1. Create a folder named `.streamlit` under repo root
2. Create a `secrets.toml` file in the `.streamlit` folder
3. Write a line `OPENAI_API_KEY = "sk-xxxx"` into the config file, so streamlit can load it as `st.secrets`

## Usage

Run the following command to start the Streamlit app:
```
streamlit run app.py
```

Once the app is running, you'll be able to access it by visiting `localhost:8501` in your web browser.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please submit a pull request. 

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

[share_badge]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[share_link]: https://playgpt3.streamlit.app/

[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/switchball/streamlit-gpt3
