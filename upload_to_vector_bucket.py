#!/usr/bin/env python3
"""
Upload embeddings from local files to S3 Vector bucket
"""
import boto3
import json
import numpy as np
import sys
import os
from botocore.exceptions import ClientError

# Configuration
REGION = 'us-east-2'
# Get AWS account ID dynamically
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']
VECTOR_BUCKET_NAME = f'ragvec-{ACCOUNT_ID}'
VECTOR_INDEX_NAME = 'documents'
EMBEDDINGS_DIR = 'embeddings'
DIMENSION = 1024  # Titan Text Embeddings V2 dimension

def list_local_embeddings():
    """List all embedding files in local directory"""
    print("\n" + "="*60)
    print("  Step 1: List Local Embeddings")
    print("="*60)
    
    if not os.path.exists(EMBEDDINGS_DIR):
        print(f"✗ Embeddings directory not found: {EMBEDDINGS_DIR}")
        print("Please run generate_fake_documents.py and regenerate_embeddings_titan.py first")
        return []
    
    embedding_files = [f for f in os.listdir(EMBEDDINGS_DIR) if f.endswith('.bin')]
    embedding_files.sort()
    
    print(f"✓ Found {len(embedding_files)} embedding files in {EMBEDDINGS_DIR}/")
    return embedding_files

def load_document_metadata():
    """Load document metadata from JSON file"""
    print("\n" + "="*60)
    print("  Step 2: Load Document Metadata")
    print("="*60)
    
    try:
        with open('fake_documents.json', 'r') as f:
            documents = json.load(f)
        
        # Create lookup dict by document_id
        metadata_lookup = {}
        for doc in documents:
            metadata_lookup[doc['document_id']] = {
                'title': doc['title'],
                'topic': doc['metadata']['topic'],
                'word_count': doc['metadata']['word_count'],
                'document_id': doc['document_id']
            }
        
        print(f"✓ Loaded metadata for {len(metadata_lookup)} documents")
        return metadata_lookup
    except Exception as e:
        print(f"✗ Error loading document metadata: {e}")
        print("Please run generate_fake_documents.py first")
        return {}

def upload_embeddings(embedding_files, metadata_lookup):
    """Upload embeddings from local files to S3 Vector bucket"""
    print("\n" + "="*60)
    print("  Step 3: Upload Embeddings to S3 Vectors")
    print("="*60)
    
    s3vectors = boto3.client('s3vectors', region_name=REGION)
    
    uploaded = 0
    failed = 0
    
    for filename in embedding_files:
        # Extract document_id from filename (e.g., "doc-001.bin" -> "doc-001")
        doc_id = filename.replace('.bin', '')
        filepath = os.path.join(EMBEDDINGS_DIR, filename)
        
        try:
            # Load vector from local file
            with open(filepath, 'rb') as f:
                vector_bytes = f.read()
            
            # Parse as float32 array
            vector = np.frombuffer(vector_bytes, dtype=np.float32)
            
            if len(vector) != DIMENSION:
                print(f"✗ Skipping {doc_id}: wrong dimension ({len(vector)} != {DIMENSION})")
                failed += 1
                continue
            
            # Get metadata
            metadata = metadata_lookup.get(doc_id, {})
            
            # Upload to S3 Vector bucket
            s3vectors.put_vectors(
                vectorBucketName=VECTOR_BUCKET_NAME,
                indexName=VECTOR_INDEX_NAME,
                vectors=[{
                    'key': doc_id,
                    'data': {'float32': vector.tolist()},
                    'metadata': metadata
                }]
            )
            
            title = metadata.get('title', 'No title')
            print(f"✓ Uploaded: {doc_id} - {title[:50]}...")
            uploaded += 1
            
        except Exception as e:
            print(f"✗ Failed to upload {doc_id}: {e}")
            failed += 1
    
    print("\n" + "-"*60)
    print(f"Upload Summary:")
    print(f"  Uploaded: {uploaded}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(embedding_files)}")
    
    return uploaded, failed

def test_vector_query():
    """Test querying the vector index"""
    print("\n" + "="*60)
    print("  Step 4: Test Vector Query")
    print("="*60)
    
    s3vectors = boto3.client('s3vectors', region_name=REGION)
    
    try:
        # Create a simple test query vector (all zeros for testing)
        test_vector = [0.0] * DIMENSION
        
        response = s3vectors.query_vectors(
            vectorBucketName=VECTOR_BUCKET_NAME,
            indexName=VECTOR_INDEX_NAME,
            queryVector={'float32': test_vector},
            topK=5,
            returnDistance=True,
            returnMetadata=True
        )
        
        print(f"✓ Query successful! Returned {len(response.get('vectors', []))} results")
        
        if response.get('vectors'):
            print("\nTop 5 results:")
            for i, result in enumerate(response['vectors'][:5], 1):
                key = result.get('key', 'unknown')
                distance = result.get('distance', 'N/A')
                metadata = result.get('metadata', {})
                title = metadata.get('title', 'No title')
                print(f"  {i}. {key}: {title[:50]} (distance: {distance})")
        
        return True
    except Exception as e:
        print(f"✗ Query test failed: {e}")
        return False

def main():
    """Main upload function"""
    print("\n" + "="*60)
    print("  Upload Embeddings to S3 Vector Bucket")
    print("="*60)
    print(f"\nSource: Local directory '{EMBEDDINGS_DIR}/'")
    print(f"Destination: Vector bucket '{VECTOR_BUCKET_NAME}' / Index '{VECTOR_INDEX_NAME}'")
    print(f"Region: {REGION}")
    print(f"Dimension: {DIMENSION}")
    
    # Step 1: List local embeddings
    embedding_files = list_local_embeddings()
    if not embedding_files:
        print("\n✗ No embedding files found")
        sys.exit(1)
    
    # Step 2: Load document metadata
    metadata_lookup = load_document_metadata()
    if not metadata_lookup:
        print("\n✗ No document metadata found")
        sys.exit(1)
    
    # Step 3: Upload embeddings
    uploaded, failed = upload_embeddings(embedding_files, metadata_lookup)
    
    if uploaded == 0:
        print("\n✗ No embeddings were uploaded")
        sys.exit(1)
    
    # Step 4: Test query
    test_vector_query()
    
    print("\n" + "="*60)
    print("  Upload Complete!")
    print("="*60)
    print(f"\n✓ Successfully uploaded {uploaded} embeddings to S3 Vector bucket")
    print(f"\nVector bucket: {VECTOR_BUCKET_NAME}")
    print(f"Vector index: {VECTOR_INDEX_NAME}")
    print(f"Dimension: {DIMENSION}")
    print(f"Distance metric: COSINE")
    print("\nYou can now create a Bedrock Knowledge Base using this vector store!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
