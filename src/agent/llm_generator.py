"""
Module for generating personalized content using a Large Language Model (LLM).

This module integrates with the Google Generative AI (Gemini) API to create
email and message content based on provided recipient and context information.
It includes robust error handling with retry mechanisms for API quota limits
and automatic failover between multiple models.
"""

import json
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file. This is crucial for securely
# accessing API keys and other sensitive configuration.
load_dotenv()

# Attempt to import the Google Generative AI library.
try:
    import google.generativeai as genai
except ImportError:
    # If the library is not found, set genai to None to enable fallback behavior.
    genai = None
    print("Warning: Google Generative AI library not found. LLM features will be mocked.")

import config

# Configure the generative AI API key if the library was successfully imported.
if genai is not None:
    # Configure API key globally for all model instances.
    genai.configure(api_key=config.LLM_API["api_key"])

# Per-model quota tracking
# Stores the timestamp when each model last hit quota limits
# Format: {"model_name": timestamp}
_model_quota_timestamps = {}
QUOTA_RESET_SECONDS = 60  # Time in seconds before quota resets for a model

def generate_email_content(recipient_name: str, context: str) -> str:
    """
    Generates personalized email or message content using the configured LLM.

    The function constructs a detailed prompt incorporating recipient information,
    context, and sender details. It expects the LLM to return a JSON object
    with 'subject' and 'body' keys. It also implements a retry mechanism
    with exponential backoff for API quota errors, and automatically switches
    to alternative models from the configured list when quota is exhausted.

    Args:
        recipient_name (str): The name of the intended recipient for the content.
        context (str): The contextual information or reason for generating the message.

    Returns:
        str: The generated content as a JSON string, containing 'subject' and 'body'.
             Returns fallback content as a JSON string if the LLM is unavailable or
             if API calls fail after retries.
    """
    # Construct the prompt using a base prompt from environment variables
    # and dynamic data for personalization.
    base_prompt = os.getenv("LLM_PROMPT", "Draft a professional email.")
    full_prompt = (
        f"{base_prompt}\n\n"
        f"Recipient Name: {recipient_name}\n"
        f"Context: {context}\n"
        f"Sender Name: {config.SENDER_INFO['name']}\n\n"
        "IMPORTANT: Return ONLY a raw JSON object with keys 'subject' and 'body'. "
        "Do not include any markdown formatting (like ```json), explanations, or templates. "
        "The 'body' should be the ready-to-send email content."
    )

    # If the LLM library is not available (e.g., library not installed), return fallback content.
    if genai is None:
        # Simple, generic fallback content to ensure the application doesn't crash.
        fallback = {
            "subject": f"Hello {recipient_name}",
            "body": f"Dear {recipient_name},\n\n{context}\n\nBest regards,\n{config.SENDER_INFO['name']}"
        }
        return json.dumps(fallback)
    
    # Get the list of models from config. If it's a single string, convert to list.
    model_list = config.LLM_API["model"]
    if isinstance(model_list, str):
        model_list = [model_list]
    
    global _model_quota_timestamps
    
    max_retries_per_model = 1  # Only 1 retry per model since we can cycle back later
    initial_retry_delay = 2  # Short delay for retry
    
    # Maximum number of full cycles through all models before giving up
    max_cycles = 3
    
    for cycle in range(max_cycles):
        if cycle > 0:
            print(f"\n--- Starting cycle {cycle + 1}/{max_cycles} through models ---")
        
        models_tried_this_cycle = 0
        models_in_cooldown = 0
        
        # Iterate through each model in the list.
        for model_index, model_name in enumerate(model_list):
            # Check if this model is in cooldown period
            current_time = time.time()
            if model_name in _model_quota_timestamps:
                time_since_quota = current_time - _model_quota_timestamps[model_name]
                if time_since_quota < QUOTA_RESET_SECONDS:
                    # Model is still in cooldown
                    cooldown_remaining = int(QUOTA_RESET_SECONDS - time_since_quota)
                    print(f"Model {model_name} in cooldown ({cooldown_remaining}s remaining). Skipping.")
                    models_in_cooldown += 1
                    continue
                else:
                    # Cooldown expired, remove from tracking
                    print(f"Model {model_name} cooldown expired. Retrying.")
                    del _model_quota_timestamps[model_name]
            
            print(f"Attempting to use model: {model_name}")
            models_tried_this_cycle += 1
            
            # Create a GenerativeModel instance for this specific model.
            try:
                model = genai.GenerativeModel(model_name)
            except Exception as e:
                print(f"Error initializing model {model_name}: {e}")
                continue  # Skip to next model if initialization fails.
            
            # Try generating content with this model.
            for attempt in range(max_retries_per_model):
                try:
                    # Make the API call to generate content.
                    response = model.generate_content(full_prompt)
                    # Check if the response is empty or lacks the expected 'text' attribute.
                    if not response or not getattr(response, 'text', None):
                        raise ValueError('Empty response from LLM')
                    # Success! Return the generated text content.
                    print(f"✓ Successfully generated content using {model_name}")
                    return response.text
                except Exception as e:
                    error_str = str(e)
                    # Check for common quota-related errors.
                    if "429" in error_str or "ResourceExhausted" in error_str or "Quota" in error_str:
                        # Record the quota hit timestamp for this model
                        _model_quota_timestamps[model_name] = current_time
                        print(f"✗ Quota exceeded for {model_name}. Marked for {QUOTA_RESET_SECONDS}s cooldown.")
                        
                        # Don't retry on quota error - move to next model immediately
                        break
                    else:
                        # If it's not a quota error, log it and try next model.
                        print(f"Error with model {model_name}: {e}. Trying next model...")
                        break
        
        # After trying all models in this cycle
        if models_tried_this_cycle == 0 and models_in_cooldown == len(model_list):
            # All models are in cooldown. Calculate minimum wait time.
            min_wait = QUOTA_RESET_SECONDS
            for model_name, timestamp in _model_quota_timestamps.items():
                time_remaining = QUOTA_RESET_SECONDS - (current_time - timestamp)
                if time_remaining < min_wait:
                    min_wait = time_remaining
            
            if cycle < max_cycles - 1:
                # Wait for the first model to come out of cooldown
                wait_time = int(min_wait) + 1
                print(f"\nAll models in cooldown. Waiting {wait_time}s for quota reset...")
                time.sleep(wait_time)
                continue
            else:
                # Last cycle and all models exhausted
                print(f"\nAll models exhausted on final cycle.")
                break
        
        # If we tried at least one model but all failed, continue to next cycle
        if models_tried_this_cycle > 0:
            if cycle < max_cycles - 1:
                # Brief pause before next cycle
                print(f"\nAll available models tried. Pausing 3s before next cycle...")
                time.sleep(3)
    
    # If all attempts failed, return fallback content.
    print(f"\n⚠ All models failed after {max_cycles} cycles. Using fallback content.")
    fallback = {
        "subject": f"Hello {recipient_name}",
        "body": f"Dear {recipient_name},\n\n{context}\n\nBest regards,\n{config.SENDER_INFO['name']}"
    }
    return json.dumps(fallback)

# Example usage when the script is run directly.
if __name__ == '__main__':
    # Define example recipient and context for demonstration.
    recipient = "Jane Doe"
    email_context = "our scheduled meeting for next week"
    # Generate email content using the function.
    generated_email = generate_email_content(recipient, email_context)
    if generated_email:
        print("\nGenerated Email:")
        print(generated_email)
