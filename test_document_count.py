#!/usr/bin/env python3
"""
Test to verify document count issue is fixed
"""
from search_functions import search_and_generate, get_user_permissions

# Test users (from test_users.json)
alice_id = '71dba540-5051-7063-4bbb-ae83e587a324'
bob_id = 'e1aba5d0-50f1-7021-fbb0-bf3dcc255c35'
charlie_id = 'e1cb3560-8021-7095-a683-5d70c7ca4580'

print("\n" + "="*60)
print("  Testing Document Count Issue - FIXED")
print("="*60)

# Get actual permissions
print("\nActual permissions from database:")
alice_perms = get_user_permissions(alice_id)
bob_perms = get_user_permissions(bob_id)
charlie_perms = get_user_permissions(charlie_id)

print(f"Alice: {len(alice_perms)} documents")
print(f"Bob: {len(bob_perms)} documents")
print(f"Charlie: {len(charlie_perms)} documents")

# Test 1: Alice asking about document count
print("\n" + "-"*60)
print("TEST 1: Alice asking about document count")
print("-"*60)

query = "How many documents do I have access to?"
result = search_and_generate(query, alice_id, top_k=5)

print(f"\nClaude's response:\n{result['response']}")
print(f"\nNumber of sources provided to Claude: {len(result['sources'])}")
print(f"Total accessible reported: {result.get('total_accessible', 'NOT FOUND')}")
print(f"Actual number of documents Alice has access to: {len(alice_perms)}")

if result.get('total_accessible') == len(alice_perms):
    print("✅ PASS: Correct total count reported")
else:
    print("❌ FAIL: Incorrect total count")

# Test 2: Bob asking about document count
print("\n" + "-"*60)
print("TEST 2: Bob asking about document count")
print("-"*60)

result = search_and_generate(query, bob_id, top_k=3)

print(f"\nClaude's response:\n{result['response']}")
print(f"\nTotal accessible reported: {result.get('total_accessible', 'NOT FOUND')}")
print(f"Actual number of documents Bob has access to: {len(bob_perms)}")

if result.get('total_accessible') == len(bob_perms):
    print("✅ PASS: Correct total count reported")
else:
    print("❌ FAIL: Incorrect total count")

# Test 3: Charlie asking about document count
print("\n" + "-"*60)
print("TEST 3: Charlie asking about document count")
print("-"*60)

result = search_and_generate(query, charlie_id, top_k=5)

print(f"\nClaude's response:\n{result['response']}")
print(f"\nTotal accessible reported: {result.get('total_accessible', 'NOT FOUND')}")
print(f"Actual number of documents Charlie has access to: {len(charlie_perms)}")

if result.get('total_accessible') == len(charlie_perms):
    print("✅ PASS: Correct total count reported")
else:
    print("❌ FAIL: Incorrect total count")

# Test 4: Verify Claude understands the difference between total and retrieved
print("\n" + "-"*60)
print("TEST 4: Claude understanding total vs retrieved documents")
print("-"*60)

query = "How many documents were used to answer my previous question?"
result = search_and_generate(query, alice_id, top_k=3)

print(f"\nClaude's response:\n{result['response']}")
print(f"\nDocuments retrieved for this query: {len(result['sources'])}")
print(f"Total accessible: {result.get('total_accessible', 'NOT FOUND')}")

print("\n" + "="*60)
print("  All Tests Complete")
print("="*60)

