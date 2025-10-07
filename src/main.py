from . import llm_generator, gmail_api, linkedin_api

def get_contacts():
    """
    Returns a list of contacts.
    In a real application, this could be read from a file or another API.
    """
    contacts = [
        {"name": "Alice", "email": "alice@example.com", "platform": "gmail"},
        {"name": "Bob", "linkedin_urn": "urn:li:person:bob123", "platform": "linkedin"},
        {"name": "Charlie", "email": "charlie@example.com", "platform": "gmail"},
    ]
    return contacts

def main():
    """
    Main function to orchestrate the process of sending courtesy messages.
    """
    print("Starting the application...")

    # Get services (authentication)
    gmail_service = gmail_api.get_gmail_service()
    linkedin_token = linkedin_api.get_linkedin_service()

    # Get the list of contacts
    contacts = get_contacts()

    # Define the context for the messages
    message_context = "following up on our recent collaboration"

    for contact in contacts:
        recipient_name = contact["name"]

        # Generate personalized content
        content = llm_generator.generate_email_content(recipient_name, message_context)

        if contact["platform"] == "gmail":
            print(f"\nProcessing Gmail contact: {recipient_name}")
            subject, body = content.split('\n\n', 1) # Simple split for subject and body

            # Reformat subject from the generated content
            subject = subject.replace(f"Dear {recipient_name},", "").strip()

            message = gmail_api.create_message(
                "me", contact["email"], "Regarding our collaboration", body
            )
            gmail_api.send_message(gmail_service, "me", message)

        elif contact["platform"] == "linkedin":
            print(f"\nProcessing LinkedIn contact: {recipient_name}")
            linkedin_api.send_linkedin_message(
                linkedin_token, contact["linkedin_urn"], content
            )

    print("\nApplication finished.")

if __name__ == "__main__":
    main()