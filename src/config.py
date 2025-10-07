# Configuration settings for the application

# Gmail API settings
GMAIL_API = {
    "credentials_file": "credentials.json",
    "token_file": "token.json",
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
    "api_key": "YOUR_LLM_API_KEY",
    "model": "text-davinci-003" # example model
}

# Sender's information
SENDER_INFO = {
    "name": "[Your Name]",
    "email": "your-email@gmail.com"
}