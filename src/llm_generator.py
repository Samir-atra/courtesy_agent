import json
import google.generativeai as genai
from . import config

# Configure the generative AI model
genai.configure(api_key=config.LLM_API["api_key"])
model = genai.GenerativeModel(config.LLM_API["model"])

def generate_email_content(recipient_name, context):
    """
    Generates a personalized email content using the Gemini LLM.

    Args:
        recipient_name (str): The name of the recipient.
        context (str): The context or reason for the email.

    Returns:
        str: The generated email content as a JSON string.
    """
    # This prompt instructs the LLM to return a JSON object with "subject" and "body" keys.
    prompt = f"Write a formal and courteous email to {recipient_name} regarding {context}. " \
             f"Sign the email from {config.SENDER_INFO['name']}. " \
             'Return the email as a JSON object with two keys: "subject" and "body".'

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred while generating email content: {e}")
        return None

if __name__ == '__main__':
    # Example usage
    recipient = "Jane Doe"
    email_context = "our scheduled meeting for next week"
    generated_email = generate_email_content(recipient, email_context)
    if generated_email:
        print("Generated Email:")
        print(generated_email)
