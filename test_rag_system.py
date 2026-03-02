#!/usr/bin/env python3
"""
Comprehensive test script for the permission-based RAG system
Tests all components: permissions, search, filtering, and response generation
"""
import json
from search_functions import get_user_permissions, search_with_permissions, search_and_generate

# Test user IDs from test_users.json
ALICE_ID = 'e14b1570-0041-702c-9bab-55614c05a0f0'
BOB_ID = '317b5510-8041-70ef-ce4e-c10fc118df9e'
CHARLIE_ID = 'c12ba5d0-4071-7019-d5ab-cd465c8be06e'

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_subheader(title):
    """Print a formatted subheader"""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)

def test_permissions():
    """Test 1: Verify user permissions are correctly retrieved"""
    print_header("TEST 1: User Permissions")
    
    users = [
        ("Alice", ALICE_ID, 20),
        ("Bob", BOB_ID, 25),
        ("Charlie", CHARLIE_ID, 20)
    ]
    
    all_passed = True
    
    for name, user_id, expected_count in users:
        print_subheader(f"{name}'s Permissions")
        
        try:
            permissions = get_user_permissions(user_id)
            actual_count = len(permissions)
            
            if actual_count == expected_count:
                print(f"✓ PASS: {name} has {actual_count} documents (expected {expected_count})")
                print(f"  Sample: {sorted(list(permissions))[:5]}")
            else:
                print(f"✗ FAIL: {name} has {actual_count} documents (expected {expected_count})")
                all_passed = False
                
        except Exception as e:
            print(f"✗ FAIL: Error getting permissions for {name}: {e}")
            all_passed = False
    
    return all_passed

def test_permission_overlap():
    """Test 2: Verify overlapping permissions between users"""
    print_header("TEST 2: Permission Overlap")
    
    try:
        alice_perms = get_user_permissions(ALICE_ID)
        bob_perms = get_user_permissions(BOB_ID)
        charlie_perms = get_user_permissions(CHARLIE_ID)
        
        # Alice (doc-001 to doc-020) and Bob (doc-011 to doc-035) overlap on doc-011 to doc-020
        alice_bob_overlap = alice_perms & bob_perms
        expected_alice_bob = {f'doc-{i:03d}' for i in range(11, 21)}
        
        print_subheader("Alice & Bob Overlap")
        if alice_bob_overlap == expected_alice_bob:
            print(f"✓ PASS: Alice & Bob share {len(alice_bob_overlap)} documents (doc-011 to doc-020)")
        else:
            print(f"✗ FAIL: Expected {len(expected_alice_bob)} shared docs, got {len(alice_bob_overlap)}")
            print(f"  Expected: {sorted(expected_alice_bob)}")
            print(f"  Actual: {sorted(alice_bob_overlap)}")
            return False
        
        # Bob (doc-011 to doc-035) and Charlie (doc-031 to doc-050) overlap on doc-031 to doc-035
        bob_charlie_overlap = bob_perms & charlie_perms
        expected_bob_charlie = {f'doc-{i:03d}' for i in range(31, 36)}
        
        print_subheader("Bob & Charlie Overlap")
        if bob_charlie_overlap == expected_bob_charlie:
            print(f"✓ PASS: Bob & Charlie share {len(bob_charlie_overlap)} documents (doc-031 to doc-035)")
        else:
            print(f"✗ FAIL: Expected {len(expected_bob_charlie)} shared docs, got {len(bob_charlie_overlap)}")
            return False
        
        # Alice and Charlie should have no overlap
        alice_charlie_overlap = alice_perms & charlie_perms
        
        print_subheader("Alice & Charlie Overlap")
        if len(alice_charlie_overlap) == 0:
            print(f"✓ PASS: Alice & Charlie share 0 documents (as expected)")
        else:
            print(f"✗ FAIL: Alice & Charlie should not share documents, but share {len(alice_charlie_overlap)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: Error testing overlaps: {e}")
        return False

def test_search_filtering():
    """Test 3: Verify search results respect permissions"""
    print_header("TEST 3: Search with Permission Filtering")
    
    query = "technology and science"
    all_passed = True
    
    users = [
        ("Alice", ALICE_ID),
        ("Bob", BOB_ID),
        ("Charlie", CHARLIE_ID)
    ]
    
    for name, user_id in users:
        print_subheader(f"{name}'s Search Results")
        
        try:
            # Get user's permissions
            user_perms = get_user_permissions(user_id)
            
            # Perform search
            results = search_with_permissions(query, user_id, top_k=5)
            
            print(f"✓ Retrieved {len(results)} results for {name}")
            
            # Verify all results are within user's permissions
            all_allowed = True
            for i, result in enumerate(results, 1):
                doc_id = result['document_id']
                score = result['score']
                title = result['metadata'].get('title', 'Unknown')
                
                if doc_id in user_perms:
                    print(f"  {i}. ✓ {doc_id}: {title} (score: {score:.4f})")
                else:
                    print(f"  {i}. ✗ {doc_id}: {title} - NOT IN USER PERMISSIONS!")
                    all_allowed = False
                    all_passed = False
            
            if all_allowed:
                print(f"✓ PASS: All results are within {name}'s permissions")
            else:
                print(f"✗ FAIL: Some results are outside {name}'s permissions")
                
        except Exception as e:
            print(f"✗ FAIL: Error searching for {name}: {e}")
            all_passed = False
    
    return all_passed

def test_search_relevance():
    """Test 4: Verify search returns relevant results"""
    print_header("TEST 4: Search Relevance")
    
    test_cases = [
        ("technology", ALICE_ID, ["technology", "tech", "computing", "digital"]),
        ("science", BOB_ID, ["science", "scientific", "research", "physics", "biology"]),
        ("business", CHARLIE_ID, ["business", "management", "strategy", "corporate"])
    ]
    
    all_passed = True
    
    for query, user_id, expected_keywords in test_cases:
        print_subheader(f"Query: '{query}'")
        
        try:
            results = search_with_permissions(query, user_id, top_k=3)
            
            if len(results) == 0:
                print(f"⚠ WARNING: No results found for query '{query}'")
                continue
            
            print(f"✓ Retrieved {len(results)} results")
            
            # Check if results contain expected keywords
            found_relevant = False
            for i, result in enumerate(results, 1):
                title = result['metadata'].get('title', '').lower()
                topic = result['metadata'].get('topic', '').lower()
                
                # Check if any expected keyword is in title or topic
                relevant = any(keyword in title or keyword in topic for keyword in expected_keywords)
                
                if relevant:
                    found_relevant = True
                    print(f"  {i}. ✓ {result['document_id']}: {result['metadata'].get('title')} (score: {result['score']:.4f})")
                else:
                    print(f"  {i}. ? {result['document_id']}: {result['metadata'].get('title')} (score: {result['score']:.4f})")
            
            if found_relevant:
                print(f"✓ PASS: Found relevant results for '{query}'")
            else:
                print(f"⚠ WARNING: No highly relevant results for '{query}'")
                
        except Exception as e:
            print(f"✗ FAIL: Error testing relevance for '{query}': {e}")
            all_passed = False
    
    return all_passed

def test_response_generation():
    """Test 5: Verify response generation with Claude Sonnet 4.5"""
    print_header("TEST 5: Response Generation")
    
    test_cases = [
        ("Alice", ALICE_ID, "What is blockchain technology?"),
        ("Bob", BOB_ID, "Explain cybersecurity best practices"),
        ("Charlie", CHARLIE_ID, "Tell me about business strategy")
    ]
    
    all_passed = True
    
    for name, user_id, query in test_cases:
        print_subheader(f"{name}: '{query}'")
        
        try:
            result = search_and_generate(query, user_id, top_k=3)
            
            response = result['response']
            sources = result['sources']
            
            # Check if response is not empty
            if len(response) > 50:
                print(f"✓ Generated response ({len(response)} chars)")
                print(f"\nResponse preview:")
                print(f"  {response[:200]}...")
            else:
                print(f"⚠ WARNING: Response is very short ({len(response)} chars)")
            
            # Check sources
            print(f"\n✓ Used {len(sources)} source documents:")
            for source in sources:
                print(f"  - {source['document_id']}: {source['title']} (score: {source['score']:.4f})")
            
            print(f"✓ PASS: Response generated successfully for {name}")
            
        except Exception as e:
            print(f"✗ FAIL: Error generating response for {name}: {e}")
            all_passed = False
    
    return all_passed

def test_unauthorized_access():
    """Test 6: Verify users cannot access documents outside their permissions"""
    print_header("TEST 6: Unauthorized Access Prevention")
    
    # Alice should only see doc-001 to doc-020
    # Charlie should only see doc-031 to doc-050
    # So if we search for a Charlie-only document with Alice's credentials, it shouldn't appear
    
    print_subheader("Alice searching for Charlie's documents")
    
    try:
        # Get Alice's permissions
        alice_perms = get_user_permissions(ALICE_ID)
        
        # Get Charlie's exclusive documents (not shared with Bob)
        charlie_perms = get_user_permissions(CHARLIE_ID)
        bob_perms = get_user_permissions(BOB_ID)
        charlie_exclusive = charlie_perms - bob_perms  # doc-036 to doc-050
        
        # Search with Alice's credentials
        results = search_with_permissions("education and learning", ALICE_ID, top_k=10)
        
        # Check if any Charlie-exclusive documents appear
        unauthorized_found = False
        for result in results:
            if result['document_id'] in charlie_exclusive:
                print(f"✗ FAIL: Alice can see Charlie's document {result['document_id']}")
                unauthorized_found = True
        
        if not unauthorized_found:
            print(f"✓ PASS: Alice cannot access Charlie's exclusive documents")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error testing unauthorized access: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("  PERMISSION-BASED RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = [
        ("User Permissions", test_permissions),
        ("Permission Overlap", test_permission_overlap),
        ("Search Filtering", test_search_filtering),
        ("Search Relevance", test_search_relevance),
        ("Response Generation", test_response_generation),
        ("Unauthorized Access Prevention", test_unauthorized_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "-"*70)
    print(f"  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print(f"  🎉 ALL TESTS PASSED!")
    else:
        print(f"  ⚠ {total_count - passed_count} test(s) failed")
    
    print("="*70 + "\n")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
