# Courtesy_server

Application to generate and send courtesy emails and messages to a list of accounts using an LLM for content generation.

## Overview

This program uses a Large Language Model (LLM) to generate personalized messages and sends them to a predefined list of contacts via the Gmail and LinkedIn APIs. The current implementation provides a complete architectural skeleton, but requires user configuration to be fully functional, as it cannot perform the interactive OAuth 2.0 flow required by these APIs on its own.

This guide provides the necessary steps to set up and run the application.

## Features

- **LLM-Powered Content:** Generates message content using a placeholder LLM module.
- **Gmail Integration:** Sends emails through the Gmail API (requires user authentication).
- **LinkedIn Integration:** Sends messages to LinkedIn connections (requires user authentication).
- **Configurable:** API keys and settings are managed in a central `config.py` file.

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

You will need to obtain API credentials from Google and LinkedIn.

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

#### B. LinkedIn API Setup

1.  **Go to the LinkedIn Developer Portal:** [https://www.linkedin.com/developers/](https://www.linkedin.com/developers/)
2.  **Create an App:** Follow the instructions to create a new application.
3.  **Get Credentials:**
    - Once your app is created, navigate to the **Auth** tab.
    - You will find your **Client ID** and **Client Secret** here.
4.  **Update Configuration:**
    - Open the `src/config.py` file.
    - Replace the placeholder values for `YOUR_LINKEDIN_CLIENT_ID` and `YOUR_LINKEDIN_CLIENT_SECRET` with your actual credentials.

#### C. LLM API (Optional)

If you wish to integrate a real LLM:
1.  Obtain an API key from your preferred LLM provider (e.g., OpenAI, Cohere).
2.  Update the `LLM_API` dictionary in `src/config.py` with your key.
3.  Modify `src/llm_generator.py` to make an actual API call using the credentials.

### 4. Running the Application

The first time you run the application, you will be prompted to authenticate with Google.

```bash
python -m src.main
```

- A browser window will open, asking you to log in to your Google account and grant permissions.
- After you approve, a `token.json` file will be created in the root directory. This file stores your authentication tokens so you don't have to log in every time.

**Note:** The LinkedIn API flow is mocked in this version. A similar interactive flow would need to be implemented in `src/linkedin_api.py` for full functionality.

## How It Works

- **`src/main.py`**: The main script that orchestrates the entire process.
- **`src/config.py`**: Stores all API keys and configuration settings.
- **`src/llm_generator.py`**: Generates the message content.
- **`src/gmail_api.py`**: Handles authentication and sending emails via the Gmail API.
- **`src/linkedin_api.py`**: Handles authentication and sending messages via the LinkedIn API.
