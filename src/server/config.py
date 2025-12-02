"""
Configuration settings for the courtesy_server application.

This module loads environment variables and defines various settings
for interacting with external APIs like Gmail, LinkedIn, and a Large Language Model (LLM).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows sensitive information and configurations to be managed outside the codebase.
load_dotenv()

# --- API Configuration ---

# Gmail API settings
# These settings are used for authenticating and interacting with the Gmail API.
GMAIL_API = {
    # Path to the OAuth 2.0 client credentials file.
    # Defaults to 'credentials.json' if GMAIL_API_CREDENTIALS_PATH env var is not set.
    "credentials_file": os.getenv("GMAIL_API_CREDENTIALS_PATH", "credentials.json"),
    # Path to the file where the user's access and refresh tokens are stored.
    # Defaults to 'token.json' if GMAIL_API_TOKEN_PATH env var is not set.
    "token_file": os.getenv("GMAIL_API_TOKEN_PATH", "token.json"),
    # OAuth 2.0 scopes required for sending emails.
    "scopes": ["https://www.googleapis.com/auth/gmail.send"]
}

# Feature flags
# Control whether to simulate email sending or perform actual sending.
SIMULATE_EMAIL_SEND = os.getenv("SIMULATE_EMAIL_SEND", "True").lower() == "true"

# LinkedIn API settings
# NOTE: These are placeholder values. A full LinkedIn integration would require
# obtaining proper API credentials and implementing the OAuth 2.0 flow.
LINKEDIN_API = {
    "client_id": "YOUR_LINKEDIN_CLIENT_ID", # Replace with actual Client ID
    "client_secret": "YOUR_LINKEDIN_CLIENT_SECRET", # Replace with actual Client Secret
    "redirect_uri": "http://localhost:8000/callback" # Replace with actual Redirect URI
}

# Large Language Model (LLM) API settings
# Used for configuring the generative AI model for content creation.
LLM_API = {
    # API key for authentication with the LLM service (e.g., Google Gemini API).
    # Loaded from the GEMINI_API_KEY environment variable.
    "api_key": os.getenv("GEMINI_API_KEY"),
    # The specific LLM model to use (e.g., "gemini-2.5-flash").
    "model": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]
}

# Sender's information
# Details about the sender of the courtesy messages.
SENDER_INFO = {
    # Sender's name. Defaults to "Samer Attrah" if SENDER_NAME env var is not set.
    "name": os.getenv("SENDER_NAME", "Samer Attrah"),
    # Sender's email address. Defaults to "samiratra95@gmail.com" if SENDER_EMAIL env var is not set.
    "email": os.getenv("SENDER_EMAIL", "samiratra95@gmail.com")
}
