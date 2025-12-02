# Courtesy_agent

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
    *Upon first execution, you will be prompted to open a web browser to authorize the application to send emails on your behalf. This process uses the `credentials.json` file and generates a `token.json` file which stores your credentials for future use.*

#### B. Gemini LLM API

1.  **Go to the Google AI Studio:** [https://aistudio.google.com/](https://aistudio.google.com/)
2.  **Create an API key.**
3.  **Update the `.env` file:**
    *See the detailed `.env` file configuration below.*

### 4. Create the `.env` File

Create a `.env` file in the root directory and add the following content:

*   **`.env` File Configuration:**
    *   `GMAIL_API_CREDENTIALS_PATH`: (Optional) Path to the Gmail OAuth credentials JSON file. Defaults to `credentials.json`.
    *   `GMAIL_API_TOKEN_PATH`: (Optional) Path to store the Gmail API access/refresh tokens. Defaults to `token.json`.
    *   `GEMINI_API_KEY`: (Required) Your API key for the Gemini LLM.
    *   `SENDER_NAME`: (Optional) The name to be used as the sender of emails. Defaults to "Samer Attrah".
    *   `SENDER_EMAIL`: (Optional) The email address to send emails from. Defaults to "samiratra95@gmail.com".
    *   `MESSAGE_CONTEXT`: (Optional) A general context string for the LLM prompt (e.g., "our follow-up meeting", "a thank you note"). Defaults to "sending a courtesy message".
    *   `SIMULATE_EMAIL_SEND`: (Optional) Set to `False` to send actual emails; otherwise, emails are simulated and printed to the console. Defaults to `True`.
    *   `LLM_PROMPT`: (Optional) Allows customization of the base prompt used to instruct the LLM.

```
# Example .env content:
# GMAIL_API_CREDENTIALS_PATH="credentials.json"
# GMAIL_API_TOKEN_PATH="token.json"
# GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
# SENDER_NAME="Your Name"
# SENDER_EMAIL="your.email@gmail.com"
# MESSAGE_CONTEXT="following up on our recent conversation"
# SIMULATE_EMAIL_SEND=True
# LLM_PROMPT="Draft a polite and professional email."
```

### 5. Create the `contacts.csv` File

Create a `contacts.csv` file in the root directory with the following format:

*   **`contacts.csv` File Format:**
    *   The CSV file should contain the following columns: `name`, `email`, `platform`, and `linkedin_urn`.
    *   `linkedin_urn` is required for contacts with `platform` set to `linkedin` and should follow the format `urn:li:person:<unique_id>`.

```csv
# Example contacts.csv content:
name,email,platform,linkedin_urn
Alice Smith,alice.s@example.com,gmail,
Bob Johnson,bob.j@example.com,linkedin,urn:li:person:mock_id_for_bob
Charlie Brown,charlie.b@example.com,gmail,
```

### 6. Running the Application

The first time you run the application, you will be prompted to authenticate with Google.

```bash
python -m src.main
```

- A browser window will open, asking you to log in to your Google account and grant permissions.
- After you approve, a `token.json` file will be created in the root directory. This file stores your authentication tokens so you don't have to log in every time.

**Note:** The LinkedIn API flow is mocked in this version.

## Advanced Configuration / Optional Flags

This section details advanced configuration options and flags that control the application's behavior.

### LLM Configuration and Failover

The application uses a list of Gemini models (e.g., `gemini-2.5-flash`) and includes logic to automatically retry with alternative models or after a cooldown period if API quotas are exceeded. This ensures resilience and continuous operation even under heavy API load.

### `SIMULATE_EMAIL_SEND` Flag

*   **Function:** This flag controls whether actual emails are sent or if the process is simulated.
*   **To enable actual email sending:** Set `SIMULATE_EMAIL_SEND=False` in your `.env` file.
*   **Default Behavior:** By default, emails are simulated and their details are printed to the console, which is useful for testing and preventing accidental sends.

### Error Handling and Control

*   The `stop_on_error` parameter in `main.py` defaults to `True`. This means the application will halt execution if any error occurs during contact processing, providing a safeguard against unexpected issues and ensuring you are aware of problems.

### LinkedIn API Mocking

*   The LinkedIn API integration is currently mocked. The `send_linkedin_message` function within `linkedin_api.py` will print simulation details to the console instead of sending real messages. The `linkedin_urn` is used for display purposes within these simulations.
