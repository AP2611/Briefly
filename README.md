# Briefly
# 🧠 Discord Summarizer Bot

A powerful and easy-to-use Discord bot built with Python and [Ollama Mistral](https://ollama.com/) to automatically **summarize long messages and conversations** in Discord servers.

## 🚀 Features

* 📚 Summarizes long text messages
* 🗣️ Summarizes full conversation threads
* ⚡ Fast and efficient responses using local LLMs via Ollama
* 🔧 Customizable commands
* 🔐 Runs locally without relying on external APIs

## 🛠️ Built With

* **Python** – Bot logic and Discord integration
* **discord.py** – For interacting with the Discord API
* **Ollama** – Local language model runner
* **Mistral** – The language model used for summarization

## 📦 Requirements

* Python 3.8+
* Ollama installed and running (`https://ollama.com`)
* A Discord bot token

## 📥 Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/yourusername/discord-summarizer-bot.git
   cd discord-summarizer-bot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start your Ollama model**

   ```bash
   ollama run mistral
   ```

4. **Set your environment variables**

   Create a `.env` file in the root folder:

   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

5. **Run the bot**

   ```bash
   python bot.py
   ```

## 💬 Usage

Once the bot is running and added to your server, you can use commands like:

* `!summarize <text>` — Summarizes a long message
* `!summarize_thread` — Summarizes the recent conversation in the current channel

You can customize these commands in the `bot.py` file.

## 🧠 Model Info

This bot uses the **Mistral** model via **Ollama**, which allows fast local inference without needing cloud APIs or keys.

## ✅ To-Do

* [ ] Add slash command support
* [ ] Improve context window handling
* [ ] Multi-language support
* [ ] Persistent conversation logging

## 🤝 Contributing

Pull requests are welcome! If you have suggestions for improvements, feel free to open an issue or a PR.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

🧠 Built with love and language models.
