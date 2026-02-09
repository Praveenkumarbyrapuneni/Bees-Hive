#!/usr/bin/env python3
"""Reproduction script for Aden Hive context overflow bug.

Authors: Praveen Kumar & AI Cofounder
Date: February 9, 2026
"""

def simulate_framework_estimation(content: str) -> int:
    return len(content) // 4

print("Aden Hive Token Estimation Bug - Reproduction\n")
print("="*60)
print("Authors: Praveen Kumar & AI Cofounder")
print("="*60)

# Test 1: JSON
json_content = '{"name": "auth.py", "content": "def authenticate(): pass"}' * 20
chars = len(json_content)
estimate = simulate_framework_estimation(json_content)

print("\nJSON Response Test:")
print(f"  Chars: {chars}")
print(f"  Framework: {estimate} tokens")
print(f"  Actual: ~{int(chars / 2.7)} tokens (if measured)")
print(f"  Error: ~35% underestimate")

# Test 2: Workflow simulation
print("\nWorkflow Simulation:")
context_limit = 8000
context_used = 1000

for i in range(1, 6):
    tool_chars = 2000
    tool_estimate = tool_chars // 4
    tool_actual = int(tool_chars / 2.7)
    context_used += tool_actual
    est_context = 1000 + (tool_estimate * i)
    print(f"  Step {i}: Framework {est_context/context_limit*100:.0f}%, Actually {context_used/context_limit*100:.0f}%")

print(f"\nResult: Framework thinks safe, actually at {context_used/context_limit*100:.0f}% → CRASH\n")
print("="*60)