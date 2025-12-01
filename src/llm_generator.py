import json
from dotenv import load_dotenv
load_dotenv()
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    genai = None
import config

if genai is not None:
    # Configure the generative AI model
    genai.configure(api_key=config.LLM_API["api_key"])
    model = genai.GenerativeModel(config.LLM_API["model"])
else:
    # Fallback: no AI model available
    model = None

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
    prompt = os.getenv("LLM_PROMPT")

    if model is None:
        # Simple fallback content
        fallback = {
            "subject": f"Hello {recipient_name}",
            "body": f"Dear {recipient_name},\n\n{context}\n\nBest regards,\n{config.SENDER_INFO['name']}"
        }
        return json.dumps(fallback)
    else:
        try:
            response = model.generate_content(prompt)
            # If the response is empty or not a string, fallback
            if not response or not getattr(response, 'text', None):
                raise ValueError('Empty response from LLM')
            return response.text
        except Exception as e:
            # Log the error and return fallback content
            print(f"LLM generation error: {e}. Using fallback content.")
            fallback = {
                "subject": f"Hello {recipient_name}",
                "body": f"Dear {recipient_name},\n\n{context}\n\nBest regards,\n{config.SENDER_INFO['name']}"
            }
            return json.dumps(fallback)

if __name__ == '__main__':
    # Example usage
    recipient = "Jane Doe"
    email_context = "our scheduled meeting for next week"
    generated_email = generate_email_content(recipient, email_context)
    if generated_email:
        print("Generated Email:")
        print(generated_email)
