# Courtesy_server

Application to generate and send courtesy emails and messages to a list of accounts using an LLM for content generation.

## Overview

This program uses a Large Language Model (LLM) to generate personalized messages and sends them to a predefined list of contacts via the Gmail API.

This guide provides the necessary steps to set up and run the application.

## Features

- **LLM-Powered Content:** Generates message content using the Gemini LLM.
- **Gmail Integration:** Sends emails through the Gmail API.
- **Configurable:** API keys and settings are managed in a `.env` file.
- **Contact Management:** Contacts are managed in a `contacts.csv` file.
- **Error Handling:** Configurable error handling to either stop on an error or continue.

## Prerequisites

- Python 3.8+
- `pip` for installing packages

## Setup and Configuration

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Curtisy_server
```

### 2. Install Dependencies

Install the required Python libraries using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Configure the APIs

You will need to obtain API credentials from Google.

#### A. Gmail API Setup

1.  **Go to the Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Create a new project.**
3.  **Enable the Gmail API:**
    - In the navigation menu, go to **APIs & Services > Library**.
    - Search for "Gmail API" and enable it.
4.  **Create OAuth 2.0 Credentials:**
    - Go to **APIs & Services > Credentials**.
    - Click **Create Credentials > OAuth client ID**.
    - Select **Desktop app** as the application type.
    - Click **Create**.
5.  **Download Credentials:**
    - A window will appear with your Client ID and Client Secret. Click **Download JSON**.
    - Rename the downloaded file to `credentials.json` and place it in the root directory of this project.

#### B. Gemini LLM API

1.  **Go to the Google AI Studio:** [https://aistudio.google.com/](https://aistudio.google.com/)
2.  **Create an API key.**
3.  **Update the `.env` file:**
    - Open the `.env` file.
    - Replace the placeholder value for `YOUR_GEMINI_API_KEY` with your actual API key.

### 4. Create the `.env` File

Create a `.env` file in the root directory and add the following content:

```
# Gmail API
GMAIL_API_CREDENTIALS_PATH="credentials.json"
GMAIL_API_TOKEN_PATH="token.json"

# Gemini LLM
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Sender Info
SENDER_NAME="[Your Name]"
SENDER_EMAIL="your-email@gmail.com"
```

### 5. Create the `contacts.csv` File

Create a `contacts.csv` file in the root directory with the following format:

```csv
name,email,platform
Alice,alice@example.com,gmail
Bob,bob@example.com,gmail
```

### 6. Running the Application

The first time you run the application, you will be prompted to authenticate with Google.

```bash
python -m src.main
```

- A browser window will open, asking you to log in to your Google account and grant permissions.
- After you approve, a `token.json` file will be created in the root directory. This file stores your authentication tokens so you don't have to log in every time.

**Note:** The LinkedIn API flow is mocked in this version.

## How It Works

- **`src/main.py`**: The main script that orchestrates the entire process.
- **`src/config.py`**: Stores all API keys and configuration settings.
- **`src/llm_generator.py`**: Generates the message content.
- **`src/gmail_api.py`**: Handles authentication and sending emails via the Gmail API.
- **`src/linkedin_api.py`**: Handles authentication and sending messages via the LinkedIn API.
