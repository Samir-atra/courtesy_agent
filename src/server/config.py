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
SIMULATE_EMAIL_SEND = os.getenv("SIMULATE_EMAIL_SEND", "False").lower() == "true"

# LinkedIn API settings
# These credentials are loaded from environment variables.
# To configure, add the following to your .env file:
#   LINKEDIN_CLIENT_ID=your_client_id
#   LINKEDIN_CLIENT_SECRET=your_client_secret
#   LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
#
# Get your credentials from: https://www.linkedin.com/developers/
# LINKEDIN_API = {
#     "client_id": os.getenv("LINKEDIN_CLIENT_ID", "YOUR_LINKEDIN_CLIENT_ID"),
#     "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", "YOUR_LINKEDIN_CLIENT_SECRET"),
#     "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback"),
# }

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
