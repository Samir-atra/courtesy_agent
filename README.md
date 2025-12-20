# 📧 Courtesy Agent

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)
![Gemini](https://img.shields.io/badge/Gemini-LLM-purple.svg)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=samiratra95@gmail.com&item_name=Code+Broker+Donation&currency_code=USD)

**Automated courtesy email generation and delivery powered by AI** ✨

[Features](#-features) • [Setup](#-setup-and-configuration) • [Usage](#-running-the-application) • [Configuration](#-advanced-configuration--optional-flags)

</div>

---

## 📖 Overview

**Courtesy Agent** is an intelligent automation tool that uses Large Language Models (LLMs) to generate personalized courtesy emails and messages. It seamlessly integrates with the **Gmail API** to send professional, context-aware emails to your contacts with minimal effort.

Perfect for:
- 🎓 Academic outreach
- 💼 Professional networking
- 🤝 Relationship management
- 📬 Follow-up communications

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Content** | Generates personalized messages using Google's Gemini LLM |
| 📮 **Gmail Integration** | Sends emails directly through the Gmail API |
| ✏️ **Interactive Review** | Review and edit drafts in your terminal editor before sending |
| ⚙️ **Highly Configurable** | Manage all settings via `.env` file |
| 📊 **Contact Management** | Import contacts from CSV files |
| 🛡️ **Error Handling** | Configurable error handling with stop-on-error option |
| 🔄 **Smart Failover** | Automatic model switching when API quotas are exceeded |
| 🧪 **Simulation Mode** | Test without sending actual emails |

---

## 📋 Prerequisites

- 🐍 **Python 3.8+**
- 📦 **pip** for package management
- 🔑 **Google Cloud Account** (for Gmail API)
- 🧠 **Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/))

---

## 🚀 Setup and Configuration

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Samir-atra/courtesy_agent.git
cd courtesy_agent
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or use conda (recommended):

```bash
conda activate courtsey_server
```

### 3️⃣ Configure the APIs

#### 🔐 A. Gmail API Setup

1. **Visit the [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project**
3. **Enable the Gmail API:**
   - Navigate to **APIs & Services > Library**
   - Search for "Gmail API" and enable it
4. **Create OAuth 2.0 Credentials:**
   - Go to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Select **Desktop app** as the application type
5. **Download Credentials:**
   - Download the JSON file
   - Rename it to `credentials.json` and place it in the project root

> 💡 **Note:** On first run, you'll authorize the app via browser. This creates a `token.json` file for future use.

#### 🧠 B. Gemini LLM API

1. **Visit [Google AI Studio](https://aistudio.google.com/)**
2. **Create an API key**
3. **Add it to your `.env` file** (see below)

### 4️⃣ Create the `.env` File

Start with the provided template:

```bash
cp .env.template .env
```

Then edit `.env` with your credentials:

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | ✅ Yes | Your Gemini API key | - |
| `GMAIL_API_CREDENTIALS_PATH` | ❌ No | Path to Gmail credentials | `credentials.json` |
| `GMAIL_API_TOKEN_PATH` | ❌ No | Path to token storage | `token.json` |
| `SENDER_NAME` | ❌ No | Your name | `John Doe` |
| `SENDER_EMAIL` | ❌ No | Your email address | `john.doe@mail.com` |
| `MESSAGE_CONTEXT` | ❌ No | Context for LLM prompt | `sending a courtesy message` |
| `SIMULATE_EMAIL_SEND` | ❌ No | Test mode (no actual sends) | `True` |
| `REVIEW_IN_EDITOR` | ❌ No | Review drafts before sending | `True` |
| `START_CONTACT_INDEX` | ❌ No | Skip first N contacts | `0` |
| `LLM_PROMPT` | ❌ No | Custom LLM instruction | `Write a formal and courteous email.` |

**Example `.env`:**

```bash
GEMINI_API_KEY="your_api_key_here"
SENDER_NAME="Your Name"
SENDER_EMAIL="your.email@gmail.com"
MESSAGE_CONTEXT="following up on our recent conversation"
SIMULATE_EMAIL_SEND=True
REVIEW_IN_EDITOR=True
```

### 5️⃣ Create the Contacts File

Create a CSV file with your contacts (e.g., `contacts.csv`):

```csv
name,email,platform,linkedin_urn
Alice Smith,alice.s@example.com,gmail,
Bob Johnson,bob.j@example.com,linkedin,urn:li:person:mock_id_for_bob
Charlie Brown,charlie.b@example.com,gmail,
```

> 📌 **Note:** The `linkedin_urn` is only required for LinkedIn contacts (currently mocked).

---

## 🎯 Running the Application

Launch the agent:

```bash
python src/agent/main.py
```

### What happens:

1. 🔐 **Authentication** (first run only): Browser opens for Google OAuth
2. 📖 **Contact Loading**: Reads contacts from CSV
3. 🤖 **Content Generation**: LLM creates personalized emails
4. ✏️ **Review** (if enabled): Opens draft in text editor (nano/vim/etc.)
5. ✅ **Confirmation**: Prompts you to confirm sending
6. 📤 **Delivery**: Sends via Gmail API (or simulates if in test mode)

---

## ⚙️ Advanced Configuration / Optional Flags

### 🔄 LLM Configuration and Failover

The agent uses multiple Gemini models with automatic failover:
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.0-flash`

If a model hits quota limits, the system automatically switches to the next available model or waits for cooldown.

### 🧪 `SIMULATE_EMAIL_SEND` Flag

| Setting | Behavior |
|---------|----------|
| `True` (default) | 🖨️ Prints emails to console (safe testing) |
| `False` | 📧 Sends actual emails via Gmail API |

**Enable real sending:**
```bash
SIMULATE_EMAIL_SEND=False
```

### ✏️ `REVIEW_IN_EDITOR` Flag

| Setting | Behavior |
|---------|----------|
| `True` (default) | 📝 Opens draft in text editor for review |
| `False` | ⏭️ Skips editor, goes straight to confirmation |

**Editor used:** Defaults to `nano`, or uses your `$EDITOR` environment variable.

### 🛡️ Error Handling and Control

The `stop_on_error` parameter in `main.py` defaults to `True`:
- ✅ **Stops execution** on first error (safe default)
- ❌ **Continues processing** if set to `False` (skips failed contacts)

### 🔗 LinkedIn API Mocking

> ⚠️ **Currently mocked**: LinkedIn integration prints simulation details instead of sending real messages. The `linkedin_urn` is used for display purposes only.

---

## 📚 Additional Resources

- 📖 [Gmail API Documentation](https://developers.google.com/gmail/api)
- 🧠 [Google AI Studio](https://aistudio.google.com/)
- 🐍 [Python dotenv](https://pypi.org/project/python-dotenv/)
- 📝 [Google Style Guide](https://google.github.io/styleguide/)

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

---

## 🧩 For best experience

Checkout the [contacts manager](https://github.com/Samir-atra/Contacts_manager/tree/main)

---

<div align="center">

**Made with ❤️ by [Samer Attrah](https://github.com/Samir-atra)**

⭐ Star this repo if you find it helpful, and consider donating if you find it useful!

</div>
