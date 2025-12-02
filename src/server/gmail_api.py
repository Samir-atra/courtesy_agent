"""
Module for interacting with the Gmail API, including authentication, message creation, and sending.

This module handles the OAuth 2.0 flow for Gmail API access and provides utility functions
to create and (simulated) send email messages.
"""

import os
import base64
import email # Added for parsing raw email content
from email.mime.text import MIMEText
import config

try:
    # Attempt to import Google API client libraries
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    # Fallback dummy implementations if libraries are not installed.
    # This allows the application to run in a mock mode without Gmail API access.
    InstalledAppFlow = None
    Request = None
    Credentials = None
    build = None
    print("Warning: Google Gmail API libraries not found. Gmail features will be mocked.")

# OAuth 2.0 scopes required for sending emails via the Gmail API.
SCOPES = config.GMAIL_API["scopes"]

def get_gmail_service():
    """
    Authenticates with the Gmail API using OAuth 2.0 and returns an authorized service object.

    The function first checks for existing credentials (token.json). If valid credentials
    are not found or are expired, it initiates an OAuth 2.0 flow to prompt the user for authorization.
    The credentials are then saved for future use.

    Returns:
        googleapiclient.discovery.Resource or None: An authenticated Gmail API service object
        if successful, otherwise None if required libraries are missing or an error occurs.
    """
    # If any of the essential Google API components are missing, return None.
    if any(x is None for x in (InstalledAppFlow, Request, Credentials, build)):
        print("Google Gmail API libraries are not installed. Skipping Gmail service initialization.")
        return None

    creds = None
    # The 'token.json' file stores the user's access and refresh tokens.
    # It's created automatically after the first successful authorization.
    if os.path.exists(config.GMAIL_API['token_file']):
        creds = Credentials.from_authorized_user_file(config.GMAIL_API['token_file'], SCOPES)

    # If there are no (valid) credentials available, or they are expired, initiate the login flow.
    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh the token if it's expired but a refresh token is available.
                creds.refresh(Request())
            else:
                # Start the interactive OAuth 2.0 flow to get new credentials.
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.GMAIL_API['credentials_file'], SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the newly obtained or refreshed credentials for the next run.
            with open(config.GMAIL_API['token_file'], 'w') as token:
                token.write(creds.to_json())
    except Exception as e:
        print(f"Error initializing Gmail service: {e}")
        print("Proceeding without Gmail service (mock mode).")
        return None

    # Build and return the Gmail API service object.
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    """
    Creates a MIMEText message formatted for the Gmail API.

    Args:
        sender (str): The email address of the sender.
        to (str): The email address of the receiver.
        subject (str): The subject line of the email.
        message_text (str): The plain text body of the email.

    Returns:
        dict: A dictionary containing the 'raw' base64url-encoded email message,
              suitable for the Gmail API's messages.send method.
    """
    # Create a MIMEText object for the email body.
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    # Encode the message into a base64url-safe string.
    raw_message_b64 = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message_b64}

def send_message(service, user_id: str, message: dict) -> dict or None:
    """
    Sends an email message through the Gmail API or simulates sending based on configuration.

    Args:
        service: Authorized Gmail API service instance.
        user_id (str): The user's email address, typically "me" for the authenticated user.
        message (dict): The message dictionary, expected to contain a 'raw' key with the
                        base64url-encoded email content.

    Returns:
        dict or None: The message ID of the sent email if successful, or a mock ID if simulated,
                      otherwise None if an error occurs during the API call or simulation.
    """
    if config.SIMULATE_EMAIL_SEND:
        try:
            # Decode the base64url-encoded raw message.
            raw_message = base64.urlsafe_b64decode(message['raw']).decode()
            # Parse the raw message into an email.message.Message object.
            msg = email.message_from_string(raw_message)

            # Extract email components for printing.
            sender = msg['from']
            recipient = msg['to']
            subject = msg['subject']
            body = msg.get_payload() # Get the email body.

            # Print the simulated email details.
            print("\n--- SIMULATING GMAIL SEND ---")
            print(f"From: {sender}")
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(f"Body: {body[:200]}...") # Truncate body to 200 characters for display.
            print("-----------------------------")
            # Return a mock message ID to simulate a successful API call.
            return {"id": "mock_message_id"}
        except Exception as e:
            print(f"An error occurred while simulating email send: {e}")
            return None
    else:
        try:
            # Send the email using the Gmail API.
            sent_message = service.users().messages().send(userId=user_id, body=message).execute()
            print(f"Message Id: {sent_message['id']} sent successfully.")
            return sent_message
        except Exception as e:
            print(f"An error occurred while sending the email: {e}")
            return None

# Example usage when the script is run directly.
if __name__ == '__main__':
    gmail_service = get_gmail_service()

    sender_email = config.SENDER_INFO["email"]
    recipient_email = "recipient@example.com" # Placeholder recipient for example.
    email_subject = "Test Email Simulation"
    email_body = "This is a test email sent via a mock Gmail API. This content will be printed to the console."

    email_message = create_message(sender_email, recipient_email, email_subject, email_body)

    # The user_id is 'me' for the authenticated user in a real scenario.
    send_message(gmail_service, "me", email_message)
