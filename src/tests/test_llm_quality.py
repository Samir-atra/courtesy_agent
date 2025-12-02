#!/usr/bin/env python3
"""
Test script to verify LLM output quality for different recipients.
This tests the email generation without actually sending emails.
"""

import sys
sys.path.insert(0, 'src/server')

import llm_generator
from config import SENDER_INFO
import os
from dotenv import load_dotenv

load_dotenv()

# Test recipients
test_recipients = [
    "Prof. David Malan",
    "Mr. François Chollet", 
    "Monica",
    "Prof. Leshem"
]

message_context = os.getenv("MESSAGE_CONTEXT", "merry christmas")

print("=" * 60)
print("LLM OUTPUT QUALITY VERIFICATION TEST")
print("=" * 60)
print(f"Context: {message_context}")
print(f"Sender: {SENDER_INFO['name']}")
print("=" * 60)

for recipient in test_recipients:
    print(f"\n{'='*60}")
    print(f"Testing recipient: {recipient}")
    print('='*60)
    
    content = llm_generator.generate_email_content(recipient, message_context)
    print(f"\nGenerated content:\n{content}\n")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
