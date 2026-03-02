#!/usr/bin/env python3
"""
Simple CLI interface for the permission-based RAG system
Allows users to search documents based on their permissions
"""
import json
import sys
from search_functions import search_with_permissions, search_and_generate, get_user_permissions

# Load test users
def load_test_users():
    """Load test users from test_users.json"""
    try:
        with open('test_users.json', 'r') as f:
            data = json.load(f)
            return data['users']
    except Exception as e:
        print(f"Error loading test users: {e}")
        sys.exit(1)

def display_banner():
    """Display welcome banner"""
    print("\n" + "="*70)
    print("  🔍 PERMISSION-BASED RAG SYSTEM")
    print("  Secure Document Search with Amazon Bedrock")
    print("="*70)

def display_users(users):
    """Display available users"""
    # Load all documents to get topics
    try:
        with open('fake_documents.json', 'r') as f:
            all_docs = json.load(f)
    except:
        all_docs = []
    
    print("\n📋 Available Users:")
    print("-" * 70)
    for i, user in enumerate(users, 1):
        name = user['name']
        email = user['email']
        user_id = user['cognito_user_id']
        
        # Get permission count and topics
        try:
            perms = get_user_permissions(user_id)
            doc_count = len(perms)
            
            # Count topics
            topic_counts = {}
            for doc in all_docs:
                if doc['document_id'] in perms:
                    topic = doc['metadata']['topic']
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            topics_str = ", ".join([f"{t.capitalize()}" for t in sorted(topic_counts.keys())])
        except:
            doc_count = "?"
            topics_str = "Unknown"
        
        print(f"  {i}. {name} ({email})")
        print(f"     Access: {doc_count} documents")
        print(f"     Topics: {topics_str}")
    print("-" * 70)

def select_user(users):
    """Prompt user to select a user"""
    while True:
        try:
            choice = input("\n👤 Select user (1-3) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(users):
                return users[choice_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(users)}")
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def display_search_options():
    """Display search options"""
    print("\n🔎 Search Options:")
    print("  1. Simple Search (returns document list)")
    print("  2. AI-Powered Search (generates answer with Claude Sonnet 4.5)")
    print("  3. Switch User")
    print("  4. Quit")

def get_search_option():
    """Get search option from user"""
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("❌ Please enter 1, 2, 3, or 4")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def perform_simple_search(user):
    """Perform simple search and display results"""
    query = input("\n💬 Enter your search query: ").strip()
    
    if not query:
        print("❌ Query cannot be empty")
        return
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"👤 User: {user['name']}")
    print("-" * 70)
    
    try:
        results = search_with_permissions(query, user['cognito_user_id'], top_k=5)
        
        if not results:
            print("❌ No results found. Try a different query.")
            return
        
        print(f"\n✅ Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            doc_id = result['document_id']
            score = result['score']
            title = result['metadata'].get('title', 'Untitled')
            topic = result['metadata'].get('topic', 'unknown')
            
            print(f"{i}. 📄 {title}")
            print(f"   ID: {doc_id} | Topic: {topic} | Score: {score:.4f}")
            print()
        
    except Exception as e:
        print(f"❌ Error performing search: {e}")

def perform_ai_search(user):
    """Perform AI-powered search with response generation"""
    query = input("\n💬 Enter your question: ").strip()
    
    if not query:
        print("❌ Question cannot be empty")
        return
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"👤 User: {user['name']}")
    print(f"🤖 Generating answer with Claude Sonnet 4.5...")
    print("-" * 70)
    
    try:
        result = search_and_generate(query, user['cognito_user_id'], top_k=3)
        
        response = result['response']
        sources = result['sources']
        total_accessible = result.get('total_accessible', '?')
        
        print(f"\n💡 Answer:\n")
        print(response)
        
        print(f"\n📊 Access Summary:")
        print(f"  • Total accessible documents: {total_accessible}")
        print(f"  • Documents used for this answer: {len(sources)}")
        
        if sources:
            print(f"\n📚 Sources:")
            for i, source in enumerate(sources, 1):
                doc_id = source['document_id']
                title = source['title']
                score = source['score']
                print(f"  {i}. {title} ({doc_id}) - Score: {score:.4f}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error generating response: {e}")

def show_user_permissions(user):
    """Show detailed permissions for current user"""
    try:
        # Load all documents to get topics
        with open('fake_documents.json', 'r') as f:
            all_docs = json.load(f)
        
        # Get user's permissions
        perms = get_user_permissions(user['cognito_user_id'])
        sorted_perms = sorted(list(perms))
        
        # Count topics for user's documents
        topic_counts = {}
        for doc in all_docs:
            if doc['document_id'] in perms:
                topic = doc['metadata']['topic']
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        print(f"\n📋 {user['name']}'s Document Access:")
        print("-" * 70)
        print(f"Total documents: {len(sorted_perms)}")
        print(f"Document range: {sorted_perms[0]} to {sorted_perms[-1]}")
        
        print(f"\n📚 Available Topics:")
        for topic, count in sorted(topic_counts.items()):
            print(f"  • {topic.capitalize()}: {count} documents")
        
        print(f"\n💡 Example Queries:")
        example_queries = {
            'technology': '"blockchain", "cybersecurity", "artificial intelligence"',
            'science': '"quantum physics", "neuroscience", "DNA research"',
            'business': '"entrepreneurship", "e-commerce", "business strategy"',
            'health': '"nutrition", "mental health", "telemedicine"',
            'education': '"online learning", "STEM education", "assessment"'
        }
        
        for topic in sorted(topic_counts.keys()):
            if topic in example_queries:
                print(f"  • {topic.capitalize()}: {example_queries[topic]}")
        
        print("-" * 70)
    except Exception as e:
        print(f"❌ Error loading permissions: {e}")

def main():
    """Main CLI loop"""
    # Load users
    users = load_test_users()
    
    # Display banner
    display_banner()
    
    # Display available users
    display_users(users)
    
    # Select initial user
    current_user = select_user(users)
    if not current_user:
        print("\n👋 Goodbye!")
        return
    
    print(f"\n✅ Logged in as: {current_user['name']} ({current_user['email']})")
    show_user_permissions(current_user)
    
    # Main loop
    while True:
        try:
            display_search_options()
            option = get_search_option()
            
            if option == '1':
                perform_simple_search(current_user)
            
            elif option == '2':
                perform_ai_search(current_user)
            
            elif option == '3':
                print("\n" + "="*70)
                display_users(users)
                new_user = select_user(users)
                if new_user:
                    current_user = new_user
                    print(f"\n✅ Switched to: {current_user['name']} ({current_user['email']})")
                    show_user_permissions(current_user)
            
            elif option == '4':
                print("\n👋 Thank you for using the RAG system. Goodbye!")
                break
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
