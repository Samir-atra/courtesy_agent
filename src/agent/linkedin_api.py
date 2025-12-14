"""
LinkedIn API module for OAuth 2.0 authentication and messaging.

This module handles the complete OAuth 2.0 flow (3-legged OAuth) for LinkedIn API access
and provides functions to validate account access and send messages to connections.

IMPORTANT: LinkedIn's Messaging API requires Partner Program approval.
For sending messages, you'll need to apply at: https://business.linkedin.com/marketing-solutions/partner-integrations

References:
- OAuth 2.0 Documentation: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow
- Developer Portal: https://www.linkedin.com/developers/
"""

import json
import os
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from typing import Optional

import requests

import config

# --- API Configuration ---
API_BASE_URL = "https://api.linkedin.com/v2"
OAUTH2_AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
OAUTH2_ACCESS_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Load credentials from config
CLIENT_ID = config.LINKEDIN_API.get("client_id", "")
CLIENT_SECRET = config.LINKEDIN_API.get("client_secret", "")
REDIRECT_URI = config.LINKEDIN_API.get("redirect_uri", "http://localhost:8000/callback")

# Token storage file path
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "../../linkedin_token.json")

# OAuth 2.0 Scopes
# Reference: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
SCOPES = [
    "openid",           # OpenID Connect
    "profile",          # Basic profile information
    "email",            # Email address
    "w_member_social",  # Post, comment, and react on behalf of the member
]


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler to capture OAuth callback with authorization code."""

    authorization_code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None

    def log_message(self, format: str, *args) -> None:
        """Suppress HTTP server logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET request from OAuth redirect."""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if "code" in query_params:
            OAuthCallbackHandler.authorization_code = query_params["code"][0]
            OAuthCallbackHandler.state = query_params.get("state", [None])[0]
            self._send_success_response()
        elif "error" in query_params:
            OAuthCallbackHandler.error = query_params.get("error_description", ["Unknown error"])[0]
            self._send_error_response()
        else:
            self._send_error_response("Invalid callback request")

    def _send_success_response(self) -> None:
        """Send success HTML response to browser."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkedIn Authorization</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                       display: flex; justify-content: center; align-items: center;
                       height: 100vh; margin: 0; background: linear-gradient(135deg, #0077b5, #00a0dc); }
                .container { text-align: center; background: white; padding: 40px;
                            border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
                h1 { color: #0077b5; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Authorization Successful</h1>
                <p>You can close this window and return to the application.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def _send_error_response(self, message: str = None) -> None:
        """Send error HTML response to browser."""
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        error_msg = message or OAuthCallbackHandler.error or "An error occurred"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkedIn Authorization Error</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                       display: flex; justify-content: center; align-items: center;
                       height: 100vh; margin: 0; background: #f5f5f5; }}
                .container {{ text-align: center; background: white; padding: 40px;
                            border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                h1 {{ color: #cc0000; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✗ Authorization Failed</h1>
                <p>{error_msg}</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())


def _load_token() -> Optional[dict]:
    """Load stored access token from file.

    Returns:
        dict: Token data containing access_token, expires_in, etc., or None if not found.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load token file: {e}")
    return None


def _save_token(token_data: dict) -> None:
    """Save access token to file.

    Args:
        token_data: Token response from LinkedIn OAuth.
    """
    try:
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
        print(f"Token saved to {TOKEN_FILE}")
    except IOError as e:
        print(f"Warning: Failed to save token: {e}")


def _get_authorization_url(state: str) -> str:
    """Generate LinkedIn OAuth 2.0 authorization URL.

    Args:
        state: Random state string for CSRF protection.

    Returns:
        str: Complete authorization URL to redirect the user to.
    """
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": " ".join(SCOPES),
    }
    return f"{OAUTH2_AUTHORIZATION_URL}?{urlencode(params)}"


def _exchange_code_for_token(authorization_code: str) -> Optional[dict]:
    """Exchange authorization code for access token.

    Args:
        authorization_code: The authorization code received from LinkedIn callback.

    Returns:
        dict: Token response containing access_token and expires_in, or None on failure.
    """
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(OAUTH2_ACCESS_TOKEN_URL, data=data, headers=headers, timeout=30)
        response.raise_for_status()

        token_data = response.json()
        print("Successfully obtained access token!")
        return token_data

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error during token exchange: {e}")
        if response.text:
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request error during token exchange: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse token response: {e}")

    return None


def authenticate() -> Optional[str]:
    """Perform complete OAuth 2.0 authentication flow.

    This initiates the 3-legged OAuth flow:
    1. Opens browser for user authorization
    2. Starts local server to capture callback
    3. Exchanges authorization code for access token

    Returns:
        str: Access token if successful, None otherwise.
    """
    # Validate configuration
    if not CLIENT_ID or CLIENT_ID == "YOUR_LINKEDIN_CLIENT_ID":
        print("Error: LinkedIn CLIENT_ID not configured.")
        print("Please update LINKEDIN_API settings in config.py or .env file")
        return None

    if not CLIENT_SECRET or CLIENT_SECRET == "YOUR_LINKEDIN_CLIENT_SECRET":
        print("Error: LinkedIn CLIENT_SECRET not configured.")
        print("Please update LINKEDIN_API settings in config.py or .env file")
        return None

    # Check for existing valid token
    existing_token = _load_token()
    if existing_token and "access_token" in existing_token:
        # Verify token is still valid by making a test request
        if validate_access(existing_token["access_token"]):
            print("Using existing valid access token.")
            return existing_token["access_token"]
        print("Existing token is invalid or expired. Re-authenticating...")

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(16)

    # Reset handler state
    OAuthCallbackHandler.authorization_code = None
    OAuthCallbackHandler.state = None
    OAuthCallbackHandler.error = None

    # Parse redirect URI to get host and port
    parsed_uri = urlparse(REDIRECT_URI)
    host = parsed_uri.hostname or "localhost"
    port = parsed_uri.port or 8000

    # Generate authorization URL
    auth_url = _get_authorization_url(state)

    print("\n" + "=" * 60)
    print("LinkedIn OAuth 2.0 Authorization")
    print("=" * 60)
    print("\nOpening browser for LinkedIn authorization...")
    print(f"If browser doesn't open, visit this URL:\n{auth_url}\n")

    # Open browser for user authorization
    webbrowser.open(auth_url)

    # Start local server to capture callback
    server = HTTPServer((host, port), OAuthCallbackHandler)
    server.timeout = 120  # 2 minute timeout

    print(f"Waiting for authorization callback on {REDIRECT_URI}...")
    server.handle_request()

    # Check for errors
    if OAuthCallbackHandler.error:
        print(f"Authorization failed: {OAuthCallbackHandler.error}")
        return None

    # Verify state to prevent CSRF
    if OAuthCallbackHandler.state != state:
        print("Error: State mismatch. Possible CSRF attack detected.")
        return None

    # Check for authorization code
    if not OAuthCallbackHandler.authorization_code:
        print("Error: No authorization code received.")
        return None

    # Exchange code for token
    token_data = _exchange_code_for_token(OAuthCallbackHandler.authorization_code)
    if token_data:
        _save_token(token_data)
        return token_data.get("access_token")

    return None


def get_linkedin_service() -> Optional[str]:
    """Get LinkedIn API access token (service object).

    Attempts to load existing token or initiate new authentication.

    Returns:
        str: Access token if available/authenticated, None otherwise.
    """
    # Try to load existing token
    existing_token = _load_token()
    if existing_token and "access_token" in existing_token:
        access_token = existing_token["access_token"]
        if validate_access(access_token):
            return access_token
        print("Stored token is invalid. Please re-authenticate using authenticate().")
        return None

    print("No valid token found. Use authenticate() to perform OAuth flow.")
    return None


def validate_access(access_token: str) -> bool:
    """Validate LinkedIn access by fetching the member's profile.

    Args:
        access_token: The OAuth 2.0 access token.

    Returns:
        bool: True if access is valid, False otherwise.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        # Use the /userinfo endpoint (OpenID Connect)
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            user_info = response.json()
            name = user_info.get("name", "Unknown")
            email = user_info.get("email", "Not available")
            print(f"✓ LinkedIn access validated for: {name} ({email})")
            return True
        elif response.status_code == 401:
            print("Access token is invalid or expired.")
            return False
        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error validating access: {e}")
        return False


def get_profile(access_token: str) -> Optional[dict]:
    """Fetch the authenticated member's LinkedIn profile.

    Args:
        access_token: The OAuth 2.0 access token.

    Returns:
        dict: Profile information if successful, None otherwise.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching profile: {e}")
        return None


def get_connections(access_token: str, start: int = 0, count: int = 50) -> Optional[dict]:
    """Fetch the authenticated member's connections.

    NOTE: This API requires specific product access.
    Reference: https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/connections-api

    Args:
        access_token: The OAuth 2.0 access token.
        start: Pagination start index.
        count: Number of connections to fetch.

    Returns:
        dict: Connections data if successful, None otherwise.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    params = {
        "start": start,
        "count": count,
        "q": "viewer",
    }

    try:
        response = requests.get(
            f"{API_BASE_URL}/connections",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 403:
            print("Connections API access not available. Partner Program approval required.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching connections: {e}")
        return None


def send_linkedin_message(access_token: str, recipient_urn: str, message_text: str,
                          simulate: bool = True) -> bool:
    """Send a message to a LinkedIn connection.

    IMPORTANT: LinkedIn's Messaging API requires Partner Program approval.
    Without partner access, this function will simulate message sending.

    API Reference: https://learn.microsoft.com/en-us/linkedin/shared/integrations/communications/messages

    Args:
        access_token: The OAuth 2.0 access token.
        recipient_urn: The URN of the recipient (e.g., "urn:li:person:abcdef123").
        message_text: The message content to send.
        simulate: If True, only simulate the send; if False, attempt real send.

    Returns:
        bool: True if message sent (or simulated) successfully, False otherwise.
    """
    if simulate or not access_token or access_token == "DUMMY_ACCESS_TOKEN":
        print("\n--- SIMULATING LINKEDIN MESSAGE SEND ---")
        print(f"To LinkedIn URN: {recipient_urn}")
        print(f"Message: {message_text[:200]}..." if len(message_text) > 200 else f"Message: {message_text}")
        print("----------------------------------------")
        return True

    # Real message sending (requires Partner Program access)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Get sender's URN (required for message payload)
    profile = get_profile(access_token)
    if not profile or "sub" not in profile:
        print("Error: Could not get sender's profile for messaging.")
        return False

    sender_urn = f"urn:li:person:{profile['sub']}"

    # Message payload structure per LinkedIn API
    message_body = {
        "recipients": [recipient_urn],
        "message": {
            "body": message_text
        },
        "from": sender_urn
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/messages",
            headers=headers,
            json=message_body,
            timeout=30
        )

        if response.status_code == 201:
            print(f"✓ Message sent successfully to {recipient_urn}")
            return True
        elif response.status_code == 403:
            print("Messaging API access denied. Partner Program approval required.")
            print("Apply at: https://business.linkedin.com/marketing-solutions/partner-integrations")
            return False
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return False


def send_inmail(access_token: str, recipient_urn: str, subject: str,
                message_body: str, simulate: bool = True) -> bool:
    """Send an InMail to a LinkedIn member (not necessarily a connection).

    IMPORTANT: InMail API requires Sales Navigator or Recruiter license and Partner approval.

    Args:
        access_token: The OAuth 2.0 access token.
        recipient_urn: The URN of the recipient.
        subject: The InMail subject line.
        message_body: The InMail message content.
        simulate: If True, only simulate the send.

    Returns:
        bool: True if InMail sent (or simulated) successfully, False otherwise.
    """
    if simulate:
        print("\n--- SIMULATING LINKEDIN INMAIL SEND ---")
        print(f"To LinkedIn URN: {recipient_urn}")
        print(f"Subject: {subject}")
        print(f"Body: {message_body[:200]}..." if len(message_body) > 200 else f"Body: {message_body}")
        print("---------------------------------------")
        return True

    # Real InMail sending would go here (requires special API access)
    print("InMail API access requires Sales Navigator or Recruiter license.")
    return False


# --- Interactive Example and Testing ---

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LinkedIn API Module - Interactive Test")
    print("=" * 60 + "\n")

    # Check if credentials are configured
    if CLIENT_ID == "YOUR_LINKEDIN_CLIENT_ID":
        print("⚠ LinkedIn API credentials not configured!")
        print("\nTo use this module:")
        print("1. Go to https://www.linkedin.com/developers/")
        print("2. Create an application")
        print("3. Update LINKEDIN_API in config.py with your credentials")
        print("4. Add the following environment variables to .env:")
        print("   LINKEDIN_CLIENT_ID=your_client_id")
        print("   LINKEDIN_CLIENT_SECRET=your_client_secret")
        print("\n" + "-" * 60 + "\n")
        print("Running in simulation mode...\n")

        # Demonstrate simulated functionality
        mock_token = "DUMMY_ACCESS_TOKEN"
        recipient = "urn:li:person:mock_recipient"
        message = "Hello! This is a test message from the courtesy_server application."

        print("1. Simulating message send:")
        send_linkedin_message(mock_token, recipient, message)

        print("\n2. Simulating InMail send:")
        send_inmail(mock_token, recipient, "Test Subject", message)

    else:
        print("LinkedIn credentials found. Initiating OAuth flow...\n")

        # Perform authentication
        token = authenticate()

        if token:
            print("\n✓ Authentication successful!")

            # Validate access
            print("\nValidating access...")
            if validate_access(token):
                # Fetch profile
                print("\nFetching profile...")
                profile = get_profile(token)
                if profile:
                    print(f"Profile data: {json.dumps(profile, indent=2)}")

                # Test message simulation
                print("\nTesting message send (simulation):")
                send_linkedin_message(
                    token,
                    "urn:li:person:test_recipient",
                    "Hello from the courtesy_server application!",
                    simulate=True
                )
        else:
            print("\n✗ Authentication failed.")