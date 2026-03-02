# Permission-Based RAG System with AWS Bedrock

A proof-of-concept implementation of a Retrieval-Augmented Generation (RAG) system that enforces document-level permissions using AWS services.

## Overview

This system demonstrates how to build a secure RAG application where:
- Users can only search and access documents they have permission to view
- Vector embeddings are stored in AWS S3 Vectors
- Search is powered by Amazon Bedrock Knowledge Bases
- Responses are generated using Anthropic Claude Sonnet 4.5
- Permissions are managed in Aurora MySQL database

## Architecture

See [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) for detailed system architecture and data flow.

### Key Components

- **Aurora MySQL**: Stores document metadata and user permissions
- **S3 Vectors**: Stores 1024-dimensional vector embeddings
- **Bedrock Knowledge Base**: Orchestrates vector search with permission filtering
- **Bedrock Runtime**: Runs Claude Sonnet 4.5 for response generation
- **Python CLI**: Interactive interface for querying the system

## Prerequisites

- AWS Account with appropriate permissions
- Python 3.9 or higher
- AWS CLI configured
- Access to the following AWS services:
  - Amazon Aurora MySQL
  - Amazon S3 Vectors
  - Amazon Bedrock (with Claude Sonnet 4.5 and Titan Embeddings V2 access)
  - AWS Cognito (optional, for user management)

## Setup Instructions

### Step 1: Clone and Setup Python Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd AuroraS3VectorProject

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install boto3 pymysql
```

### Step 2: Deploy AWS Infrastructure

```bash
# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name rag-system-poc \
  --template-body file://cloudformation-template.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-2

# Wait for stack creation to complete (takes ~10-15 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name rag-system-poc \
  --region us-east-2

# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name rag-system-poc \
  --region us-east-2 \
  --query 'Stacks[0].Outputs'
```

**Important**: Save the following outputs:
- `AuroraClusterEndpoint`: Database endpoint
- `CognitoUserPoolId`: User pool ID
- `S3BucketName`: S3 bucket name (will be deleted later)

### Step 3: Initialize Database

```bash
# Update database connection in run_init_sql.py with your Aurora endpoint
# Then run:
python run_init_sql.py
```

This creates:
- `documents` table: Stores document metadata
- `permissions` table: Stores user-document access mappings

### Step 4: Generate Test Documents and Embeddings

```bash
# Generate 50 fake documents across 5 topics
python3 generate_fake_documents.py

# Generate embeddings using Amazon Titan Text Embeddings V2
python3 regenerate_embeddings_titan.py
```

This creates:
- `fake_documents.json`: 50 documents with content
- `embeddings/`: 50 binary embedding files (1024 dimensions each)

### Step 5: Insert Documents into Database

```bash
python3 insert_documents.py
```

This populates the `documents` table with metadata for all 50 documents.

### Step 6: Create Test Users and Permissions

```bash
python3 setup_users_and_permissions.py
```

This creates three test users in Cognito and their permission records:
- **Alice** (alice@example.com): Access to 20 documents (doc-001 to doc-020)
- **Bob** (bob@example.com): Access to 25 documents (doc-011 to doc-035)
- **Charlie** (charlie@example.com): Access to 20 documents (doc-031 to doc-050)

All users have password: `TempPassxxx!`

The script also saves user IDs to `test_users.json`.

### Step 7: Upload Embeddings to S3 Vectors

```bash
python3 upload_to_vector_bucket.py
```

aws s3vectors get-vectors --vector-bucket-name ragvec-963553578223 --index-name documents --keys doc-001 doc-002 doc-003 --return-metadata --region us-east-2

This script:
- Uploads all 50 embeddings to S3 Vectors (bucket created by CloudFormation)
- Updates database records with S3 Vectors references
- Adds permission metadata to each vector

### Step 8: Create Bedrock Knowledge Base

```bash
python3 create_bedrock_kb.py
```

This creates a Bedrock Knowledge Base configured with:
- Amazon Titan Text Embeddings V2 (1024 dimensions)
- S3 Vectors storage backend
- Knowledge Base ID will be displayed (save this)

**Important**: Update `KB_ID` in `search_functions.py` with your Knowledge Base ID.

### Step 9: Test the System

```bash
# Run comprehensive test suite
python3 test_rag_system.py

# Test document count functionality
python3 test_document_count.py

# Test MCP connection (optional)
python3 test_mcp_queries.py
```

All tests should pass.

### Step 10: Use the CLI Interface

```bash
python3 search_cli.py
```

The CLI provides:
- User selection with permission summary
- Simple search mode (returns document list)
- AI-powered search mode (generates answers with Claude)
- User switching without restarting

See [CLI_USAGE.md](CLI_USAGE.md) for detailed usage instructions.

## Configuration

### Database Configuration

Update these values in `search_functions.py`:

```python
DB_HOST = 'your-aurora-endpoint.rds.amazonaws.com'
DB_PORT = 3306
DB_NAME = 'rag_system'
DB_USER = 'master'
DB_PASSWORD = 'Passxxxxx'  # Change in production!
```

### AWS Region

All scripts use `us-east-2` by default. To change:

```python
REGION = 'us-east-2'  # Update in search_functions.py
```

### Bedrock Models

Current configuration:
- **Embedding Model**: `amazon.titan-embed-text-v2:0` (1024 dimensions)
- **LLM Model**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

To change models, update:
1. `regenerate_embeddings_titan.py` - for embedding model
2. `create_bedrock_kb.py` - for KB embedding model
3. `search_functions.py` - for LLM model

## Project Structure

```
AuroraS3VectorProject/
├── README.md                          # This file
├── ARCHITECTURE_DIAGRAM.md            # System architecture
├── CLI_USAGE.md                       # CLI usage guide
├── requirements.md                    # Requirements specification
├── design.md                          # Design document
├── cloudformation-template.yaml       # AWS infrastructure template
├── init_database.sql                  # Database schema
├── run_init_sql.py                    # Database initialization
├── setup_users_and_permissions.py     # Create Cognito users
├── generate_fake_documents.py         # Generate test documents
├── regenerate_embeddings_titan.py     # Generate embeddings
├── upload_to_vector_bucket.py         # Upload to S3 Vectors
├── create_bedrock_kb.py               # Create Knowledge Base
├── insert_documents.py                # Populate database
├── search_functions.py                # Core search logic
├── search_cli.py                      # Interactive CLI
├── test_rag_system.py                 # Comprehensive tests
├── test_document_count.py             # Document count tests
├── fake_documents.json                # Generated documents
├── test_users.json                    # Test user credentials
└── embeddings/                        # Vector embeddings (50 files)
```

## How It Works

### Permission Enforcement

1. User selects their identity in the CLI
2. System queries Aurora MySQL for user's permitted document IDs
3. Vector search includes permission filter: `document_id IN [permitted_ids]`
4. Only matching documents within user's permissions are returned

### Search Flow

**Simple Search:**
1. Get user permissions from database
2. Query Bedrock KB with document_id filter
3. Return top K matching documents with scores

**AI-Powered Search:**
1. Get user permissions from database
2. Query Bedrock KB with document_id filter
3. Load full document content from `fake_documents.json`
4. Send documents + query to Claude Sonnet 4.5
5. Return generated answer with source citations

### Key Features

- **Permission Filtering**: Enforced at query time via Bedrock KB filters
- **Vector Search**: Cosine similarity on 1024-dimensional embeddings
- **Response Generation**: Claude Sonnet 4.5 with document context
- **Total Count Tracking**: Users see both total accessible docs and retrieved results
- **Overlap Handling**: Users can have overlapping permissions (e.g., Bob overlaps with both Alice and Charlie)

## Testing

### Test Coverage

- **User Permissions**: Verify correct document counts per user
- **Permission Overlap**: Test shared document access
- **Search Filtering**: Ensure users only see permitted documents
- **Search Relevance**: Validate vector search quality
- **Response Generation**: Test Claude's answer generation
- **Unauthorized Access**: Verify permission enforcement

### Running Tests

```bash
# All tests
python test_rag_system.py

# Document count specific
python test_document_count.py

# MCP connection (if configured)
python test_mcp_queries.py
```

## Cost Considerations

This PoC incurs AWS costs:

- **Aurora MySQL**: ~$0.10/hour (db.r8g.large)
- **S3 Vectors**: Storage + query costs
- **Bedrock KB**: Query costs
- **Bedrock Runtime**: Per-token costs for Claude Sonnet 4.5
- **Cognito**: Free tier covers test usage

**Estimated cost**: $5-10/day for active development

### Cost Optimization

To minimize costs:
1. Stop Aurora cluster when not in use
2. Delete S3 Vectors bucket after testing
3. Delete CloudFormation stack when done
4. Use smaller Aurora instance (db.t4g.medium)

## Cleanup

To remove all resources:

```bash
# Delete Bedrock Knowledge Base
aws bedrock-agent delete-knowledge-base \
  --knowledge-base-id <your-kb-id> \
  --region us-east-2

# Delete S3 Vectors bucket (replace 319165777908 with your AWS account ID)
aws s3vectors delete-vector-index \
  --bucket-name ragvec-319165777908 \
  --index-name documents \
  --region us-east-2

aws s3vectors delete-vector-bucket \
  --bucket-name ragvec-319165777908 \
  --region us-east-2

# Delete CloudFormation stack (includes Aurora, Cognito, IAM roles)
aws cloudformation delete-stack \
  --stack-name rag-system-poc \
  --region us-east-2
```

## Troubleshooting

### Database Connection Issues

```bash
# Test database connectivity
python mysql_shell.py
```

### Bedrock Access Issues

Ensure your AWS account has:
- Bedrock model access enabled (Claude Sonnet 4.5, Titan Embeddings V2)
- Appropriate IAM permissions for Bedrock services

### Vector Search Returns No Results

1. Verify embeddings were uploaded: Check S3 Vectors console
2. Verify KB is active: `aws bedrock-agent get-knowledge-base --knowledge-base-id <id>`
3. Check permission data: Query `permissions` table in Aurora

### Claude Returns Wrong Document Count

This was fixed in the latest version. Ensure you're using the updated `search_functions.py` that includes total document count in the prompt.

## Security Notes

⚠️ **This is a PoC - NOT production-ready**

For production use:
- Use AWS Secrets Manager for database credentials
- Implement proper JWT validation for Cognito tokens
- Add TLS/SSL for database connections
- Use VPC endpoints for AWS services
- Implement rate limiting and input validation
- Add comprehensive logging and monitoring
- Use parameter store for configuration
- Implement proper error handling
- Add authentication middleware
- Use read replicas for Aurora

## Acknowledgments

For issues or questions:
1. Check [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) for system design
2. Review [CLI_USAGE.md](CLI_USAGE.md) for usage examples
3. Run test suite to verify setup

## Acknowledgments

- Built with Amazon Bedrock, Aurora MySQL, and S3 Vectors
- Uses Anthropic Claude Sonnet 4.5 for response generation
- Uses Amazon Titan Text Embeddings V2 for vector embeddings
