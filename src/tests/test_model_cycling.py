#!/usr/bin/env python3
"""
Test script to demonstrate the intelligent model cycling with 60s quota reset.
This simulates quota exhaustion and shows how the system cycles through models.
"""

import sys
import time
sys.path.insert(0, 'src/server')

import llm_generator

print("=" * 80)
print("INTELLIGENT MODEL CYCLING TEST (60-second quota reset)")
print("=" * 80)
print("\nThis test simulates what happens when models hit quota limits.")
print("The system will:")
print("  1. Try each model in sequence")
print("  2. Track which models hit quota and when")
print("  3. Skip models in cooldown (<60s since quota hit)")
print("  4. Retry models after 60s cooldown")
print("  5. Cycle through available models efficiently")
print("=" * 80)

# Simulate quota hits by manually setting timestamps
current = time.time()

print("\n1. Simulating quota hit on gemini-2.5-flash (just now)")
llm_generator._model_quota_timestamps["gemini-2.5-flash"] = current

print("2. Simulating quota hit on gemini-2.5-flash-lite (25 seconds ago)")
llm_generator._model_quota_timestamps["gemini-2.5-flash-lite"] = current - 25

print("3. Simulating quota hit on gemini-2.0-flash (65 seconds ago - should be available)")
llm_generator._model_quota_timestamps["gemini-2.0-flash"] = current - 65

print("\n" + "=" * 80)
print("ATTEMPTING TO GENERATE EMAIL")
print("=" * 80)
print("\nExpected behavior:")
print("  - Skip gemini-2.5-flash (in cooldown)")
print("  - Skip gemini-2.5-flash-lite (in cooldown)")
print("  - Try gemini-2.0-flash (cooldown expired) ✓")
print("\n" + "-" * 80)

result = llm_generator.generate_email_content("Test User", "testing model cycling")

print("\n" + "=" * 80)
print("RESULT:")
print("=" * 80)
import json
try:
    parsed = json.loads(result)
    print(f"Subject: {parsed['subject']}")
    print(f"Body preview: {parsed['body'][:100]}...")
except:
    print(f"Result: {result[:200]}...")

print("\n" + "=" * 80)
print("Current cooldown status:")
print("=" * 80)
for model_name, timestamp in llm_generator._model_quota_timestamps.items():
    time_since = time.time() - timestamp
    if time_since < llm_generator.QUOTA_RESET_SECONDS:
        remaining = int(llm_generator.QUOTA_RESET_SECONDS - time_since)
        print(f"  {model_name}: IN COOLDOWN ({remaining}s remaining)")
    else:
        print(f"  {model_name}: AVAILABLE (cooldown expired)")

print("\n" + "=" * 80)
print("KEY BENEFITS:")
print("=" * 80)
print("✓ Models are tracked individually with cooldown timers")
print("✓ System automatically skips models in cooldown")
print("✓ After 60s, models become available again")
print("✓ With 3 models, you get ~3x the request capacity")
print("✓ Minimal delays - only waits when ALL models are in cooldown")
print("=" * 80)
