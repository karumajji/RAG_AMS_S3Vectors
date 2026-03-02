#!/usr/bin/env python3
"""
Search functions using Bedrock Knowledge Base with permission filtering
Task 7: Implement search functions using Bedrock KB
"""
import boto3
import json
from typing import Set, List, Dict, Any

# Configuration
REGION = 'us-east-2'
KB_ID = 'TZGI0VIKPU'
LLM_MODEL = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'

# Database configuration (for direct connection - not using MCP in this module)
DB_HOST = 'ams-s3-demo-auroracluster-souvtks7ayal.cluster-ctjk2qgb238i.us-east-2.rds.amazonaws.com'
DB_PORT = 3306
DB_NAME = 'rag_system'
DB_USER = 'master'
DB_PASSWORD = 'Passwordxxx'


def get_user_permissions(cognito_user_id: str) -> Set[str]:
    """
    Get list of document IDs that a user has permission to access.
    
    Args:
        cognito_user_id: The Cognito user ID
        
    Returns:
        Set of document IDs the user can access
    """
    import pymysql
    
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    cursor = conn.cursor()
    cursor.execute(
        "SELECT document_id FROM permissions WHERE cognito_user_id = %s",
        (cognito_user_id,)
    )
    
    rows = cursor.fetchall()
    document_ids = {row[0] for row in rows}
    
    cursor.close()
    conn.close()
    
    return document_ids


def search_with_permissions(
    query: str,
    cognito_user_id: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Search documents using Bedrock Knowledge Base with permission filtering.
    
    Args:
        query: The search query text
        cognito_user_id: The Cognito user ID
        top_k: Maximum number of results to return
        
    Returns:
        List of search results with scores and metadata
    """
    # Step 1: Get user's permitted document IDs
    permitted_doc_ids = get_user_permissions(cognito_user_id)
    
    if not permitted_doc_ids:
        print(f"User {cognito_user_id} has no document permissions")
        return []
    
    print(f"User has access to {len(permitted_doc_ids)} documents")
    
    # Step 2: Query Bedrock Knowledge Base with document_id filter
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = bedrock_runtime.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': top_k,
                'filter': {
                    'in': {
                        'key': 'document_id',
                        'value': list(permitted_doc_ids)
                    }
                }
            }
        }
    )
    
    # Step 3: Format results
    results = []
    for item in response.get('retrievalResults', []):
        results.append({
            'score': item.get('score', 0.0),
            'content': item.get('content', {}).get('text', ''),
            'metadata': item.get('metadata', {}),
            'document_id': item.get('metadata', {}).get('document_id', 'unknown')
        })
    
    return results


def search_and_generate(
    query: str,
    cognito_user_id: str,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Search documents and generate a response using Claude Sonnet 4.5.
    
    Args:
        query: The search query text
        cognito_user_id: The Cognito user ID
        top_k: Maximum number of results to retrieve
        
    Returns:
        Dictionary with generated response and source documents
    """
    # Step 1: Get total permission count
    permitted_doc_ids = get_user_permissions(cognito_user_id)
    total_accessible_docs = len(permitted_doc_ids)
    
    # Step 2: Retrieve relevant documents
    search_results = search_with_permissions(query, cognito_user_id, top_k)
    
    if not search_results:
        return {
            'response': f'I could not find any documents relevant to your query. You have access to {total_accessible_docs} documents in total.',
            'sources': [],
            'total_accessible': total_accessible_docs
        }
    
    # Step 3: Load document content from fake_documents.json
    with open('fake_documents.json', 'r') as f:
        all_documents = json.load(f)
    
    # Create lookup by document_id
    doc_lookup = {doc['document_id']: doc for doc in all_documents}
    
    # Step 4: Build context from search results with actual content
    context_parts = []
    for i, result in enumerate(search_results, 1):
        doc_id = result['document_id']
        doc = doc_lookup.get(doc_id)
        
        if doc:
            title = doc['title']
            content = doc['content']
            context_parts.append(f"[Document {i} - {doc_id}: {title}]\n{content}\n")
        else:
            # Fallback to KB content if document not found
            content = result['content']
            context_parts.append(f"[Document {i} - {doc_id}]\n{content}\n")
    
    context = "\n".join(context_parts)
    
    # Step 5: Generate response using Claude Sonnet 4.5
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)
    
    prompt = f"""You are a helpful assistant. Answer the user's question based on the provided documents.

IMPORTANT: The user has access to {total_accessible_docs} documents in total. The documents below are the {len(search_results)} most relevant results for their query.

Documents:
{context}

User Question: {query}

Please provide a clear and concise answer based on the documents above. If the user asks about how many documents they have access to, remember they have access to {total_accessible_docs} documents total, not just the {len(search_results)} shown here. If the documents don't contain enough information to answer the question, say so."""
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=LLM_MODEL,
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    generated_text = response_body['content'][0]['text']
    
    # Step 6: Return response with sources
    return {
        'response': generated_text,
        'sources': [
            {
                'document_id': r['document_id'],
                'score': r['score'],
                'title': r['metadata'].get('title', 'Untitled')
            }
            for r in search_results
        ],
        'total_accessible': total_accessible_docs
    }


def get_documents(doc_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get document metadata from database (optional enrichment).
    
    Args:
        doc_ids: List of document IDs
        
    Returns:
        List of document metadata dictionaries
    """
    import pymysql
    
    if not doc_ids:
        return []
    
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    cursor = conn.cursor()
    
    # Build query with placeholders
    placeholders = ','.join(['%s'] * len(doc_ids))
    query = f"SELECT document_id, title, s3_key FROM documents WHERE document_id IN ({placeholders})"
    
    cursor.execute(query, doc_ids)
    rows = cursor.fetchall()
    
    documents = []
    for row in rows:
        documents.append({
            'document_id': row[0],
            'title': row[1],
            's3_key': row[2]
        })
    
    cursor.close()
    conn.close()
    
    return documents


# Example usage
if __name__ == "__main__":
    # Test with Alice's user ID
    alice_id = '71dba540-5051-7063-4bbb-ae83e587a324'
    
    print("\n" + "="*60)
    print("  Test Search Functions")
    print("="*60)
    
    # Test 1: Get permissions
    print(f"\nTest 1: Get permissions for Alice")
    permissions = get_user_permissions(alice_id)
    print(f"✓ Alice has access to {len(permissions)} documents")
    print(f"  Sample: {list(permissions)[:5]}")
    
    # Test 2: Search with permissions
    print(f"\nTest 2: Search with permissions")
    query = "blockchain and cybersecurity"
    results = search_with_permissions(query, alice_id, top_k=3)
    print(f"✓ Found {len(results)} results")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['document_id']} (score: {result['score']:.4f})")
        print(f"     {result['metadata'].get('title', 'No title')}")
        print(f"     Content preview: {result['content'][:100]}...")

    
    # Test 3: Search and generate
    print(f"\nTest 3: Search and generate response")
    result = search_and_generate(query, alice_id, top_k=3)
    print(f"✓ Generated response:")
    print(f"\n{result['response']}\n")
    print(f"Sources:")
    for source in result['sources']:
        print(f"  - {source['document_id']}: {source['title']} (score: {source['score']:.4f})")
    
    print("\n" + "="*60)
