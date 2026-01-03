# 🤖 AI-Powered PDF Analyzer Telegram Bot

A powerful and efficient Telegram Bot that leverages Large Language Models (LLM) to read, analyze, and extract insights from **any PDF document**. Built with Python, Flask, and the Groq API (Llama 3).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Telegram API](https://img.shields.io/badge/Telegram-Bot%20API-blue)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama3-orange)

## 📖 Overview

This project is a server-side application designed to act as an intelligent document assistant on Telegram. Users can upload PDF files directly to the bot, which then extracts the text and uses advanced AI to process the content. Whether you need to summarize a long report, analyze a contract, extract specific data, or review a CV, this bot handles it all seamlessly.

## ✨ Key Features

* **Universal PDF Support:** Accepts and processes any standard PDF document sent via Telegram.
* **AI-Powered Analysis:** Utilizes the Groq API (Llama 3 model) for high-speed and accurate text understanding.
* **Context-Aware:** The bot reads the document content and answers user queries based specifically on the file provided.
* **Smart Message Handling:** Automatically handles long AI responses by chunking messages to fit within Telegram's character limits.
* **Webhook Integration:** Uses Flask to receive real-time updates from Telegram, ensuring instant responsiveness.
* **Serverless Ready:** Optimized for deployment on platforms like PythonAnywhere.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Framework:** Flask (Web Server)
* **APIs:**
    * [Telegram Bot API](https://core.telegram.org/bots/api) (Interface)
    * [Groq API](https://groq.com/) (LLM/Inference)
* **Libraries:**
    * `pypdf`: For robust PDF parsing and text extraction.
    * `openai`: Client SDK used to communicate with Groq.
    * `requests`: For handling HTTP requests.
    * `python-dotenv`: For secure environment variable management.

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/gdepradd/waBotPdfTelegram](https://github.com/gdepradd/waBotPdfTelegram)
cd your-repo-name