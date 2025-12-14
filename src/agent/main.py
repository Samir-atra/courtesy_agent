"""
Main module for the courtesy_server application.

This script orchestrates the process of reading contact information,
generating personalized content using an LLM, and then sending
the messages via Gmail or LinkedIn APIs (or simulating the send based on configuration).
It includes mechanisms for error handling and user confirmation for message sending.
"""

import csv
import os
import json
import time
import subprocess
import tempfile
import llm_generator, gmail_api #, linkedin_api     <---------- linkedin stuff
import config
from config import SENDER_INFO
from dotenv import load_dotenv

# Load environment variables from the .env file.
# This is important for configuration like LLM API keys and sender information.
load_dotenv()

def open_in_editor(content: str) -> str:
    """
    Opens the content in a text editor (defaulting to nano) and returns the edited content.
    """
    editor = os.environ.get('EDITOR', 'nano')
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".txt", delete=False) as tf:
        tf.write(content)
        tf_path = tf.name
        
    try:
        subprocess.call([editor, tf_path])
        with open(tf_path, 'r') as tf:
            return tf.read()
    except Exception as e:
        print(f"Error checking content in editor: {e}")
        return content
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)

def parse_draft(content: str) -> tuple[str, str]:
    """
    Parses the subject and body from the email draft.
    Expected format:
    Subject: <subject>
    
    <body>
    """
    lines = content.splitlines()
    subject = None
    body_lines = []
    reading_body = False
    
    for line in lines:
        if line.strip().startswith("#"):
            continue
        
        if not reading_body:
            if line.lstrip().lower().startswith("subject:"):
                # Extract subject, handle cases where user might leave space or not
                parts = line.split(":", 1)
                if len(parts) > 1:
                    subject = parts[1].strip()
                reading_body = True
                continue
            elif line.strip() == "":
                continue
        
        body_lines.append(line)
        
    return subject, "\n".join(body_lines).strip()


def get_contacts(file_path: str = "connect_hub_contacts_2025-12-14.csv") -> list[dict]:
    """
    Reads a list of contacts from a specified CSV file (Connect Hub format).

    Args:
        file_path (str): The path to the CSV file. Defaults to "connect_hub_contacts_2025-12-14.csv".

    Returns:
        list[dict]: A list of dictionaries with normalized keys (name, email, platform, etc.).
    """
    contacts = []
    try:
        # Construct the full path relative to the current working directory
        full_file_path = os.path.join(os.getcwd(), file_path)
        with open(full_file_path, "r", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Extract fields from the new CSV schema
                prefix = row.get("Prefix", "").strip()
                first_name = row.get("First Name", "").strip()
                last_name = row.get("Last Name", "").strip()
                
                # Construct the full name (e.g. "Prof. David Malan")
                name_parts = [p for p in [prefix, first_name, last_name] if p]
                full_name = " ".join(name_parts)
                
                # Map Group to platform (and normalize to lowercase as expected by logic)
                platform = row.get("Group", "").strip().lower()
                email = row.get("Email", "").strip()
                
                # Create the contact dictionary expected by the main loop
                contact = {
                    "name": full_name,
                    "email": email,
                    "platform": platform,
                    # Store original fields if needed later
                    "prefix": prefix,
                    "first_name": first_name,
                    "last_name": last_name,
                    "linkedin_urn": row.get("linkedin_urn", "") # Placeholder if missing
                }
                contacts.append(contact)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    return contacts

def main(stop_on_error: bool = True):
    """
    Main function to orchestrate the process of generating and simulating courtesy messages.

    This function initializes API services, retrieves contact data, iterates through
    each contact to generate personalized content using an LLM, and then simulates
    sending these messages via either Gmail or LinkedIn, based on the contact's platform.
    It includes a user confirmation step before simulating email sends and handles errors
    based on the `stop_on_error` flag.

    Args:
        stop_on_error (bool): If True, the application will halt execution upon encountering
                              an error during contact processing. If False, it will log the
                              error and attempt to continue with the next contact.
    """
    print("Starting the courtesy server application...")

    # --- Service Initialization ---
    # Attempt to get Gmail API service. If libraries are missing, it will be None.
    gmail_service = gmail_api.get_gmail_service()
    if gmail_service is None:
        print("Gmail service not available; Gmail contacts will be skipped or mocked.")
    # Get a mock LinkedIn API token.
    # linkedin_token = linkedin_api.get_linkedin_service()                                <------ linkedin stuff

    # Retrieve the list of contacts from the specified CSV file.
    contacts = get_contacts()

    # Get the global message context from environment variables.
    message_context = os.getenv("MESSAGE_CONTEXT")
    if not message_context:
        print("Warning: MESSAGE_CONTEXT environment variable is not set. Using default.")
        message_context = "sending a courtesy message"

    # Get the start index from environment variables.
    try:
        start_index = int(os.getenv("START_CONTACT_INDEX", "0"))
    except ValueError:
        print("Warning: START_CONTACT_INDEX is not a valid integer. Defaulting to 0.")
        start_index = 0
    
    if start_index > 0:
        print(f"Skipping the first {start_index} contacts as per START_CONTACT_INDEX.")

    # --- Contact Processing Loop ---
    # Iterate through each contact to generate and send messages (or simulate sending).
    for i, contact in enumerate(contacts):
        if i < start_index:
            continue
            
        recipient_name = contact["name"]

        try:
            # Generate personalized content for the current recipient using the LLM.
            content_json = llm_generator.generate_email_content(recipient_name, message_context)
            if not content_json:
                print(f"LLM returned empty response for {recipient_name}. Skipping this contact.")
                # Optional: Add a delay here to avoid hitting API quotas in rapid succession.
                # time.sleep(10)
                if stop_on_error:
                    break # Stop if an LLM generation error occurs and stop_on_error is True.
                else:
                    continue # Continue to the next contact if stop_on_error is False.

            # --- Platform-Specific Message Handling ---
            if contact["platform"] == "gmail":
                # Process Gmail contacts.
                print(f"\nProcessing Gmail contact: {recipient_name}")
                # Debug print the raw content received from the LLM.
                print(f"Raw LLM response for {recipient_name}: {content_json}")

                # Helper function to robustly parse JSON from LLM responses.
                def parse_json_response(text):
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        # Attempt to extract JSON substring if direct parsing fails.
                        start = text.find('{')
                        end = text.rfind('}')
                        if start != -1 and end != -1:
                            try:
                                return json.loads(text[start:end+1])
                            except json.JSONDecodeError:
                                pass # If substring parsing also fails, re-raise original error.
                        raise # Re-raise the original decoding error.
                try:
                    # Parse the LLM-generated JSON content.
                    content = parse_json_response(content_json)
                    subject = content["subject"]
                    body = content["body"]
                except Exception as e:
                    print(f"Error parsing LLM response for {recipient_name}: {e}. Skipping this contact.")
                    if stop_on_error:
                        break # Stop if JSON parsing fails and stop_on_error is True.
                    else:
                        continue # Continue to the next contact if stop_on_error is False.

                # Prepare the draft content for the editor.
                draft_content = f"# Instructions: Review and edit the email below.\n# Lines starting with '#' are ignored.\n# Ensure the Subject line remains.\n\nSubject: {subject}\n\n{body}"
                
                print(f"Opening draft for {recipient_name} in text editor...")
                # Open the draft in the editor.
                edited_content = open_in_editor(draft_content)
                
                # Parse the edited content.
                new_subject, new_body = parse_draft(edited_content)
                
                if new_subject:
                    subject = new_subject
                else:
                    print("Warning: Could not parse 'Subject:' line. Using original subject.")
                
                if new_body:
                    body = new_body
                else:
                    print("Warning: Body appears empty after edit.")

                # Display the final email content to the console.
                print(f"\n--- Final Email Content for {recipient_name} ---")
                print(f"Subject: {subject}")
                print(f"Body:\n{body}\n-----------------------------------")

                # User confirmation for sending the email.
                confirm = input("Do you want to send this email? (y/n): ").strip().lower()
                if confirm == 'y':
                    # If user confirms, send the email via Gmail API (or simulate sending).
                    if gmail_service:
                        message = gmail_api.create_message(
                            SENDER_INFO["email"], contact["email"], subject, body
                        )
                        gmail_api.send_message(gmail_service, "me", message)
                        if config.SIMULATE_EMAIL_SEND:
                            print(f"Email processing simulated for {recipient_name}.")
                        else:
                            print(f"Email sent for {recipient_name}.")
                        # Optional: Add a delay to avoid hitting Gmail API quotas in a real scenario.
                        # time.sleep(5)
                    else:
                         print(f"Gmail service unavailable. Simulating send to {recipient_name}.")
                else:
                    print(f"Skipped processing email for {recipient_name}.")

            elif contact["platform"] == "linkedin":
                # Process LinkedIn contacts.
                print(f"\nProcessing LinkedIn contact: {recipient_name}")
                # Simulate sending the LinkedIn message.
                linkedin_api.send_linkedin_message(
                    linkedin_token, contact["linkedin_urn"], content_json
                )
                # Optional: Add a delay to avoid hitting LinkedIn API quotas in a real scenario.
                # time.sleep(5)
        except Exception as e:
            # Catch any unexpected errors during contact processing.
            print(f"An unexpected error occurred while processing contact {recipient_name}: {e}")
            if stop_on_error:
                print("Stopping execution due to an error as stop_on_error is True.")
                break
        
        # Add a rate limiting delay between processing each contact.
        print("Waiting 5 seconds before processing next contact...")
        time.sleep(5)

    print("\nApplication finished.")

# Entry point of the script.
if __name__ == "__main__":
    # Run the main application logic. Set stop_on_error to True to enable stopping
    # on the first error encountered, which is suitable when user confirmation is active.
    main(stop_on_error=True)
