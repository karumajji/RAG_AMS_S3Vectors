#!/usr/bin/env python3
"""
Demo script showing the CLI interface in action
This simulates user interactions for demonstration purposes
"""
import json
from search_functions import search_with_permissions, search_and_generate, get_user_permissions

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_subheader(title):
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)

def demo_user_selection():
    """Demo: Show available users"""
    print_header("🔍 PERMISSION-BASED RAG SYSTEM DEMO")
    
    with open('test_users.json', 'r') as f:
        data = json.load(f)
        users = data['users']
    
    print("\n📋 Available Users:")
    print_subheader("User List")
    
    for i, user in enumerate(users, 1):
        name = user['name']
        email = user['email']
        user_id = user['cognito_user_id']
        
        perms = get_user_permissions(user_id)
        doc_count = len(perms)
        
        print(f"  {i}. {name} ({email})")
        print(f"     Access to {doc_count} documents")
        print(f"     Document range: {sorted(list(perms))[:3]} ... {sorted(list(perms))[-3:]}")
    
    return users

def demo_simple_search(user, query):
    """Demo: Simple search"""
    print_subheader(f"Simple Search Demo - {user['name']}")
    print(f"\n💬 Query: '{query}'")
    print(f"👤 User: {user['name']}")
    
    results = search_with_permissions(query, user['cognito_user_id'], top_k=5)
    
    print(f"\n✅ Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        doc_id = result['document_id']
        score = result['score']
        title = result['metadata'].get('title', 'Untitled')
        topic = result['metadata'].get('topic', 'unknown')
        
        print(f"{i}. 📄 {title}")
        print(f"   ID: {doc_id} | Topic: {topic} | Score: {score:.4f}")

def demo_ai_search(user, query):
    """Demo: AI-powered search"""
    print_subheader(f"AI-Powered Search Demo - {user['name']}")
    print(f"\n💬 Question: '{query}'")
    print(f"👤 User: {user['name']}")
    print(f"🤖 Generating answer with Claude Sonnet 4.5...")
    
    result = search_and_generate(query, user['cognito_user_id'], top_k=3)
    
    response = result['response']
    sources = result['sources']
    
    print(f"\n💡 Answer:\n")
    print(response)
    
    print(f"\n📚 Sources ({len(sources)} documents):")
    for i, source in enumerate(sources, 1):
        doc_id = source['document_id']
        title = source['title']
        score = source['score']
        print(f"  {i}. {title} ({doc_id}) - Score: {score:.4f}")

def demo_permission_differences():
    """Demo: Show how different users see different results"""
    print_header("Permission-Based Filtering Demo")
    
    with open('test_users.json', 'r') as f:
        data = json.load(f)
        users = data['users']
    
    query = "technology and innovation"
    
    print(f"\n🔍 Same query for all users: '{query}'")
    
    for user in users:
        print_subheader(f"{user['name']}'s Results")
        
        results = search_with_permissions(query, user['cognito_user_id'], top_k=3)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            doc_id = result['document_id']
            title = result['metadata'].get('title', 'Untitled')
            score = result['score']
            print(f"  {i}. {doc_id}: {title} (score: {score:.4f})")

def main():
    """Run all demos"""
    print_header("CLI INTERFACE DEMONSTRATION")
    print("\nThis demo shows the capabilities of the RAG system CLI")
    
    # Demo 1: User selection
    users = demo_user_selection()
    
    # Demo 2: Simple search with Alice
    alice = users[0]
    demo_simple_search(alice, "blockchain and cybersecurity")
    
    # Demo 3: AI search with Bob
    bob = users[1]
    demo_ai_search(bob, "What is quantum computing?")
    
    # Demo 4: Permission differences
    demo_permission_differences()
    
    print_header("Demo Complete")
    print("\n✅ To use the interactive CLI, run: python3 search_cli.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
