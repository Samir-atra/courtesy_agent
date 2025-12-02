#!/usr/bin/env python3
"""
Test script to demonstrate the optimized quota handling.
Shows timing for requests after quota exhaustion.
"""

import sys
import time
sys.path.insert(0, 'src/server')

import llm_generator

print("=" * 70)
print("QUOTA OPTIMIZATION TEST")
print("=" * 70)

# Test 1: Normal generation (simulate success)
print("\n1. First request (should succeed with API call):")
start = time.time()
result1 = llm_generator.generate_email_content("Test User 1", "testing")
elapsed1 = time.time() - start
print(f"   Time: {elapsed1:.2f} seconds")
print(f"   Subject: {eval(result1)['subject']}")

# Simulate quota exhaustion by setting the flag
print("\n2. Simulating quota exhaustion (setting global flag)...")
llm_generator._quota_exhausted = True

# Test 2: After quota exhaustion (should be instant)
print("\n3. Second request (after quota flag set - should be instant):")
start = time.time()
result2 = llm_generator.generate_email_content("Test User 2", "testing")
elapsed2 = time.time() - start
print(f"   Time: {elapsed2:.2f} seconds")
print(f"   Subject: {eval(result2)['subject']}")

# Test 3: Third request (should also be instant)
print("\n4. Third request (should also be instant):")
start = time.time()
result3 = llm_generator.generate_email_content("Test User 3", "testing")
elapsed3 = time.time() - start
print(f"   Time: {elapsed3:.2f} seconds") 
print(f"   Subject: {eval(result3)['subject']}")

print("\n" + "=" * 70)
print("RESULTS:")
print("=" * 70)
print(f"First request (API call):        {elapsed1:.2f} seconds")
print(f"After quota flag (fallback):     {elapsed2:.2f} seconds")
print(f"Subsequent (fallback):           {elapsed3:.2f} seconds")
print(f"\nSpeedup: {elapsed1/elapsed2:.0f}x faster for requests after quota exhaustion!")
print("=" * 70)
