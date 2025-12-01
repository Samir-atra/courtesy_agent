import csv
import json
import llm_generator, gmail_api, linkedin_api
from config import SENDER_INFO
from dotenv import load_dotenv
load_dotenv()

def get_contacts(file_path="contact.csv"):
    """
    Reads a list of contacts from a CSV file.
    """
    contacts = []
    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                contacts.append(row)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    return contacts

def main(stop_on_error=True):
    """
    Main function to orchestrate the process of sending courtesy messages.
    """
    print("Starting the application...")

    # Get services (authentication)
    gmail_service = gmail_api.get_gmail_service()
    if gmail_service is None:
        print("Gmail service not available; Gmail contacts will be skipped.")
    linkedin_token = linkedin_api.get_linkedin_service()

    # Get the list of contacts
    contacts = get_contacts()

    # Define the context for the messages
    message_context =  os.getenv("MESSAGE_CONTEXT")

    for contact in contacts:
        recipient_name = contact["name"]

        try:
            # Generate personalized content
            content_json = llm_generator.generate_email_content(recipient_name, message_context)
            if not content_json:
                print(f"LLM returned empty response for {recipient_name}. Skipping.")
                if stop_on_error:
                    break
                else:
                    continue

            if contact["platform"] == "gmail":
                if gmail_service is None:
                    print(f"Skipping Gmail contact {recipient_name} because Gmail service is unavailable.")
                    continue
                print(f"\nProcessing Gmail contact: {recipient_name}")
                # Debug print the raw content
                print(f"Raw LLM response for {recipient_name}: {content_json}")
                # Attempt to parse JSON robustly
                def parse_json_response(text):
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        # Try to extract JSON substring
                        start = text.find('{')
                        end = text.rfind('}')
                        if start != -1 and end != -1:
                            try:
                                return json.loads(text[start:end+1])
                            except json.JSONDecodeError:
                                pass
                        raise
                try:
                    content = parse_json_response(content_json)
                    subject = content["subject"]
                    body = content["body"]
                except Exception as e:
                    print(f"Error parsing LLM response for {recipient_name}: {e}")
                    if stop_on_error:
                        break
                    else:
                        continue
                message = gmail_api.create_message(
                    SENDER_INFO["email"], contact["email"], subject, body
                )
                gmail_api.send_message(gmail_service, "me", message)

            elif contact["platform"] == "linkedin":
                print(f"\nProcessing LinkedIn contact: {recipient_name}")
                linkedin_api.send_linkedin_message(
                    linkedin_token, contact["linkedin_urn"], content_json
                )
        except Exception as e:
            print(f"An error occurred while processing contact {recipient_name}: {e}")
            if stop_on_error:
                print("Stopping execution due to an error.")
                break

    print("\nApplication finished.")

if __name__ == "__main__":
    # Set stop_on_error to False to continue processing contacts even if one fails
    main(stop_on_error=True)
