import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings for the application

# Gmail API settings
GMAIL_API = {
    "credentials_file": os.getenv("GMAIL_API_CREDENTIALS_PATH", "credentials.json"),
    "token_file": os.getenv("GMAIL_API_TOKEN_PATH", "token.json"),
    "scopes": ["https://www.googleapis.com/auth/gmail.send"]
}

# LinkedIn API settings
LINKEDIN_API = {
    "client_id": "YOUR_LINKEDIN_CLIENT_ID",
    "client_secret": "YOUR_LINKEDIN_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8000/callback"
}

# LLM settings (if using an API)
LLM_API = {
    "api_key": os.getenv("GEMINI_API_KEY"),
    "model": "gemini-1.5-flash"  # example model
}

# Sender's information
SENDER_INFO = {
    "name": os.getenv("SENDER_NAME", "[Your Name]"),
    "email": os.getenv("SENDER_EMAIL", "your-email@gmail.com")
}
