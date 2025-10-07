import os
from . import config

def generate_email_content(recipient_name, context):
    """
    Generates a personalized email content using an LLM.

    Args:
        recipient_name (str): The name of the recipient.
        context (str): The context or reason for the email.

    Returns:
        str: The generated email content.
    """
    # In a real implementation, this function would call an LLM API.
    # For now, it returns a template-based message.

    prompt = f"Write a courteous and professional email to {recipient_name} regarding {context}."

    # Placeholder for LLM API call
    # api_key = config.LLM_API["api_key"]
    # model = config.LLM_API["model"]
    # response = llm.generate(prompt, api_key=api_key, model=model)
    # email_body = response.text

    email_body = f"Dear {recipient_name},\n\nI hope this email finds you well.\n\nThis is a message regarding {context}.\n\nPlease let me know if you have any questions.\n\nBest regards,\n{config.SENDER_INFO['name']}"

    return email_body

if __name__ == '__main__':
    # Example usage
    recipient = "John Doe"
    email_context = "our recent meeting"
    generated_email = generate_email_content(recipient, email_context)
    print("Generated Email:")
    print(generated_email)