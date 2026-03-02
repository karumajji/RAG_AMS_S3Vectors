#!/usr/bin/env python3
"""
Create Bedrock Knowledge Base with existing S3 Vectors
Task 6: Create Bedrock Knowledge Base with S3 Vectors
"""
import boto3
import json
import time
import sys

# Configuration
REGION = 'us-east-2'
# Get AWS account ID dynamically
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']
VECTOR_BUCKET_NAME = f'ragvec-{ACCOUNT_ID}'
VECTOR_INDEX_NAME = 'documents'
KB_NAME = 'rag-permissions-poc-kb'
KB_DESCRIPTION = 'Permission-based RAG system PoC using S3 Vectors'
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'

def create_kb_service_role():
    """Create IAM role for Bedrock Knowledge Base"""
    print("\n" + "="*60)
    print("  Step 1: Create IAM Service Role for Knowledge Base")
    print("="*60)
    
    iam = boto3.client('iam', region_name=REGION)
    role_name = 'BedrockKBServiceRole-RAG-PoC'
    
    # Trust policy for Bedrock
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": boto3.client('sts').get_caller_identity()['Account']
                }
            }
        }]
    }
    
    try:
        # Try to get existing role
        response = iam.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"⊘ Role already exists: {role_name}")
        print(f"  ARN: {role_arn}")
        return role_arn
    except iam.exceptions.NoSuchEntityException:
        pass
    
    try:
        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Service role for Bedrock Knowledge Base with S3 Vectors'
        )
        role_arn = response['Role']['Arn']
        print(f"✓ Created role: {role_name}")
        print(f"  ARN: {role_arn}")
        
        # Attach policy for S3 Vectors access
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3vectors:QueryVectors",
                        "s3vectors:GetVectors",
                        "s3vectors:PutVectors",
                        "s3vectors:DeleteVectors",
                        "s3vectors:ListVectors"
                    ],
                    "Resource": f"arn:aws:s3vectors:{REGION}:*:bucket/{VECTOR_BUCKET_NAME}/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel"
                    ],
                    "Resource": f"arn:aws:bedrock:{REGION}::foundation-model/*"
                }
            ]
        }
        
        policy_name = f'{role_name}-Policy'
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"✓ Attached inline policy: {policy_name}")
        
        # Wait for role to propagate
        print("  Waiting for role to propagate...")
        time.sleep(10)
        
        return role_arn
        
    except Exception as e:
        print(f"✗ Error creating role: {e}")
        sys.exit(1)

def create_knowledge_base(role_arn):
    """Create Bedrock Knowledge Base"""
    print("\n" + "="*60)
    print("  Step 2: Create Bedrock Knowledge Base")
    print("="*60)
    
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    # Get AWS account ID
    account_id = boto3.client('sts').get_caller_identity()['Account']
    vector_bucket_arn = f'arn:aws:s3vectors:{REGION}:{account_id}:bucket/{VECTOR_BUCKET_NAME}'
    
    try:
        # Create Knowledge Base
        response = bedrock_agent.create_knowledge_base(
            name=KB_NAME,
            description=KB_DESCRIPTION,
            roleArn=role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f'arn:aws:bedrock:{REGION}::foundation-model/{EMBEDDING_MODEL}'
                }
            },
            storageConfiguration={
                'type': 'S3_VECTORS',
                's3VectorsConfiguration': {
                    'vectorBucketArn': vector_bucket_arn,
                    'indexName': VECTOR_INDEX_NAME
                }
            }
        )
        
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        kb_arn = response['knowledgeBase']['knowledgeBaseArn']
        status = response['knowledgeBase']['status']
        
        print(f"✓ Created Knowledge Base: {KB_NAME}")
        print(f"  ID: {kb_id}")
        print(f"  ARN: {kb_arn}")
        print(f"  Status: {status}")
        print(f"  Embedding Model: {EMBEDDING_MODEL}")
        print(f"  Vector Store: S3 Vectors ({VECTOR_BUCKET_NAME}/{VECTOR_INDEX_NAME})")
        
        return kb_id, kb_arn
        
    except Exception as e:
        print(f"✗ Error creating Knowledge Base: {e}")
        sys.exit(1)

def wait_for_kb_ready(kb_id):
    """Wait for Knowledge Base to be ready"""
    print("\n" + "="*60)
    print("  Step 3: Wait for Knowledge Base to be Ready")
    print("="*60)
    
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = bedrock_agent.get_knowledge_base(
                knowledgeBaseId=kb_id
            )
            
            status = response['knowledgeBase']['status']
            print(f"  Attempt {attempt + 1}/{max_attempts}: Status = {status}")
            
            if status == 'ACTIVE':
                print(f"\n✓ Knowledge Base is ACTIVE")
                return True
            elif status == 'FAILED':
                print(f"\n✗ Knowledge Base creation FAILED")
                return False
            
            time.sleep(10)
            attempt += 1
            
        except Exception as e:
            print(f"✗ Error checking status: {e}")
            return False
    
    print(f"\n⚠ Timeout waiting for Knowledge Base to be ready")
    return False

def test_kb_retrieval(kb_id):
    """Test Knowledge Base retrieval"""
    print("\n" + "="*60)
    print("  Step 4: Test Knowledge Base Retrieval")
    print("="*60)
    
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    # Test 1: Simple query without filter
    print("\nTest 1: Query without filter")
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={
                'text': 'machine learning and artificial intelligence'
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        
        results = response.get('retrievalResults', [])
        print(f"✓ Retrieved {len(results)} results")
        
        if results:
            print("\nTop result:")
            result = results[0]
            print(f"  Score: {result.get('score', 'N/A')}")
            content = result.get('content', {}).get('text', 'No content')
            print(f"  Content: {content[:100]}...")
            metadata = result.get('metadata', {})
            print(f"  Metadata keys: {list(metadata.keys())}")
        
    except Exception as e:
        print(f"✗ Query failed: {e}")
        return False
    
    # Test 2: Query with permission filter (Alice's user ID)
    print("\nTest 2: Query with permission filter (Alice)")
    alice_id = '71dba540-5051-7063-4bbb-ae83e587a324'
    
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={
                'text': 'machine learning'
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5,
                    'filter': {
                        'in': {
                            'key': 'allowed_users',
                            'value': [alice_id]
                        }
                    }
                }
            }
        )
        
        results = response.get('retrievalResults', [])
        print(f"✓ Retrieved {len(results)} results with filter")
        
        if results:
            print("\nFiltered results:")
            for i, result in enumerate(results[:3], 1):
                metadata = result.get('metadata', {})
                doc_id = metadata.get('document_id', 'unknown')
                print(f"  {i}. {doc_id} (score: {result.get('score', 'N/A')})")
        
    except Exception as e:
        print(f"✗ Filtered query failed: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Create Bedrock Knowledge Base with S3 Vectors")
    print("="*60)
    print(f"\nKnowledge Base Name: {KB_NAME}")
    print(f"Vector Bucket: {VECTOR_BUCKET_NAME}")
    print(f"Vector Index: {VECTOR_INDEX_NAME}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Region: {REGION}")
    
    # Step 1: Create IAM role
    role_arn = create_kb_service_role()
    
    # Step 2: Create Knowledge Base
    kb_id, kb_arn = create_knowledge_base(role_arn)
    
    # Step 3: Wait for KB to be ready
    if not wait_for_kb_ready(kb_id):
        print("\n✗ Knowledge Base did not become ready")
        sys.exit(1)
    
    # Step 4: Test retrieval
    if test_kb_retrieval(kb_id):
        print("\n" + "="*60)
        print("  Knowledge Base Creation Complete!")
        print("="*60)
        print(f"\n✓ Knowledge Base ID: {kb_id}")
        print(f"✓ Knowledge Base ARN: {kb_arn}")
        print("\nYou can now use the Retrieve API with permission filters!")
        print("="*60 + "\n")
    else:
        print("\n⚠ Knowledge Base created but testing failed")
        print(f"Knowledge Base ID: {kb_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()
