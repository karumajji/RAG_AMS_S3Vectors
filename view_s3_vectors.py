#!/usr/bin/env python3
"""
View S3 Vector embeddings using boto3
"""
import boto3
import json
import sys

REGION = 'us-east-2'
# Get AWS account ID dynamically
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']
BUCKET = f'ragvec-{ACCOUNT_ID}'
INDEX = 'documents'

def list_vectors():
    """List all vectors in the index"""
    print(f"\n{'='*70}")
    print(f"  S3 Vectors - List All Vectors")
    print(f"{'='*70}")
    print(f"Bucket: {BUCKET}")
    print(f"Index: {INDEX}")
    print(f"Region: {REGION}\n")
    
    try:
        s3vectors = boto3.client('s3vectors', region_name=REGION)
        
        response = s3vectors.list_vectors(
            vectorBucketName=BUCKET,
            indexName=INDEX
        )
        
        vectors = response.get('vectors', [])
        print(f"✓ Found {len(vectors)} vectors\n")
        
        for i, vec in enumerate(vectors[:10], 1):  # Show first 10
            print(f"{i}. {vec}")
        
        if len(vectors) > 10:
            print(f"\n... and {len(vectors) - 10} more vectors")
        
        return vectors
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def get_vector(doc_id):
    """Get a specific vector by document ID"""
    print(f"\n{'='*70}")
    print(f"  S3 Vectors - Get Vector: {doc_id}")
    print(f"{'='*70}\n")
    
    try:
        s3vectors = boto3.client('s3vectors', region_name=REGION)
        
        response = s3vectors.get_vectors(
            vectorBucketName=BUCKET,
            indexName=INDEX,
            keys=[doc_id],
            returnMetadata=True
        )
        
        if response.get('vectors'):
            vec = response['vectors'][0]
            print(f"Document ID: {vec['key']}")
            print(f"\nMetadata:")
            for key, value in vec.get('metadata', {}).items():
                print(f"  {key}: {value}")
            
            vector_data = vec['data']['float32']
            print(f"\nVector:")
            print(f"  Dimensions: {len(vector_data)}")
            print(f"  First 10 values: {vector_data[:10]}")
            print(f"  Last 10 values: {vector_data[-10:]}")
            
            return vec
        else:
            print(f"✗ Vector not found: {doc_id}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def describe_index():
    """Describe the vector index"""
    print(f"\n{'='*70}")
    print(f"  S3 Vectors - Index Information")
    print(f"{'='*70}\n")
    
    try:
        s3vectors = boto3.client('s3vectors', region_name=REGION)
        
        response = s3vectors.describe_vector_index(
            bucketName=BUCKET,
            indexName=INDEX
        )
        
        print(f"Index Name: {response.get('indexName', 'N/A')}")
        print(f"Dimension: {response.get('dimension', 'N/A')}")
        print(f"Distance Metric: {response.get('distanceMetric', 'N/A')}")
        print(f"Status: {response.get('status', 'N/A')}")
        print(f"Vector Count: {response.get('vectorCount', 'N/A')}")
        
        return response
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def query_similar(doc_id, top_k=5):
    """Find similar vectors to a given document"""
    print(f"\n{'='*70}")
    print(f"  S3 Vectors - Find Similar to: {doc_id}")
    print(f"{'='*70}\n")
    
    try:
        s3vectors = boto3.client('s3vectors', region_name=REGION)
        
        # First get the vector for the document
        get_response = s3vectors.get_vectors(
            vectorBucketName=BUCKET,
            indexName=INDEX,
            keys=[doc_id]
        )
        
        if not get_response.get('vectors'):
            print(f"✗ Document not found: {doc_id}")
            return []
        
        query_vector = get_response['vectors'][0]['data']['float32']
        
        # Now query for similar vectors
        response = s3vectors.query_vectors(
            vectorBucketName=BUCKET,
            indexName=INDEX,
            queryVector={'float32': query_vector},
            topK=top_k,
            returnDistance=True,
            returnMetadata=True
        )
        
        results = response.get('vectors', [])
        print(f"✓ Found {len(results)} similar vectors:\n")
        
        for i, result in enumerate(results, 1):
            key = result.get('key', 'unknown')
            distance = result.get('distance', 'N/A')
            metadata = result.get('metadata', {})
            title = metadata.get('title', 'No title')
            
            print(f"{i}. {key}")
            print(f"   Title: {title}")
            print(f"   Distance: {distance}")
            print()
        
        return results
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python view_s3_vectors.py list              # List all vectors")
        print("  python view_s3_vectors.py info              # Show index info")
        print("  python view_s3_vectors.py get <doc-id>      # Get specific vector")
        print("  python view_s3_vectors.py similar <doc-id>  # Find similar vectors")
        print("\nExamples:")
        print("  python view_s3_vectors.py list")
        print("  python view_s3_vectors.py get doc-001")
        print("  python view_s3_vectors.py similar doc-001")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_vectors()
    elif command == 'info':
        describe_index()
    elif command == 'get' and len(sys.argv) >= 3:
        doc_id = sys.argv[2]
        get_vector(doc_id)
    elif command == 'similar' and len(sys.argv) >= 3:
        doc_id = sys.argv[2]
        top_k = int(sys.argv[3]) if len(sys.argv) >= 4 else 5
        query_similar(doc_id, top_k)
    else:
        print("✗ Invalid command or missing arguments")
        sys.exit(1)
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
