# Design Document: AWS Permissions-Based RAG System (PoC)

## Overview

This is a proof-of-concept for a secure document retrieval system that combines Amazon Bedrock Knowledge Bases with permission-based access control. Users authenticate via AWS Cognito, search documents using Bedrock's managed RAG workflow, and only see results they have permission to access.

**Core Components**:
- **AWS Cognito**: User authentication and user IDs
- **Amazon Bedrock Knowledge Bases**: Fully managed RAG workflow (embedding, storage, retrieval)
- **S3 Vectors**: Cost-effective vector storage (managed by Bedrock)
- **Aurora MySQL**: Stores document metadata and user permissions
- **MCP Server**: Database access layer

**Key Flow**: User authenticates → submits query → Bedrock retrieves with permission filter → returns allowed results

## Architecture

### High-Level Flow

```
User → Cognito (auth) → Search Function → Bedrock Knowledge Base (with permission filter)
                              ↓                           ↓
                         MCP Server                  S3 Vectors
                              ↓                           ↓
                         Aurora MySQL              Vector Index
```

### Components

**AWS Cognito**:
- Authenticates users and provides user IDs
- No JWT validation in PoC (accept user_id directly)

**Search Function**:
- Accepts query text and cognito_user_id
- Queries Aurora via MCP for user's permitted document IDs
- Calls Bedrock Retrieve API with permission filter
- Returns filtered results

**Amazon Bedrock Knowledge Bases**:
- Fully managed RAG workflow
- Handles embedding generation automatically
- Stores vectors in S3 Vectors
- Provides Retrieve API with metadata filtering
- No manual embedding or vector search code needed

**MCP Server (aurora-db)**:
- Provides access to Aurora MySQL database
- Executes SQL queries for permissions
- No direct database connections in application code

**Aurora MySQL**:
- `documents` table: document metadata and S3 Vectors references
- `permissions` table: which users can access which documents

**S3 Vectors**:
- Stores document embeddings (managed by Bedrock)
- Vector bucket: `rag-system-vectors`
- Vector index: `documents`
- Metadata includes: title, topic, word_count, document_id

## Search Flow

1. User sends query with cognito_user_id
2. Search function queries Aurora via MCP for user's permitted document IDs
3. Search function calls Bedrock Retrieve API with:
   - Query text
   - Filter: `{'in': {'key': 'document_id', 'value': permitted_ids}}`
   - numberOfResults: top_k
4. Bedrock automatically:
   - Converts query to vector embedding
   - Searches S3 Vectors index
   - Filters by document_id metadata
   - Returns ranked results with scores
5. Search function returns results to user

## Data Models

### Database Schema

**documents table**:
```sql
CREATE TABLE documents (
  document_id VARCHAR(255) PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  s3_vector_key VARCHAR(500) NOT NULL,  -- Format: s3vectors://bucket/index/doc-id
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSON
);
```

**permissions table**:
```sql
CREATE TABLE permissions (
  permission_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cognito_user_id VARCHAR(255) NOT NULL,
  document_id VARCHAR(255) NOT NULL,
  granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
  UNIQUE KEY (cognito_user_id, document_id),
  INDEX (cognito_user_id)
);
```

**Note**: Only read permissions are supported. The search function has read-only access and cannot modify documents or permissions.

### S3 Vectors Metadata

Each vector in S3 Vectors includes metadata:
```json
{
  "document_id": "doc-001",
  "title": "Introduction to Machine Learning",
  "topic": "technology",
  "word_count": 69
}
```

### API Models

**SearchRequest**:
```json
{
  "query": "string",
  "cognito_user_id": "string",
  "top_k": 10
}
```

**SearchResponse**:
```json
{
  "results": [
    {
      "document_id": "string",
      "title": "string",
      "score": 0.95,
      "content": "string",
      "metadata": {}
    }
  ],
  "total": 10
}
```

## Key Implementation Details

### Bedrock Knowledge Base with S3 Vectors
- Bedrock automatically handles embedding generation and vector storage
- Uses S3 Vectors for cost-effective vector storage
- Retrieve API provides built-in metadata filtering
- No manual HNSW index management needed
- Sub-second query latency (100ms warm, <1s cold)

**Bedrock KB Benefits**:
- Fully managed RAG workflow
- No embedding code needed
- No vector search code needed
- Built-in chunking and retrieval
- Automatic index optimization
- Cost-effective with S3 Vectors

### Permission Filtering

**Database Query (via MCP)**:
```sql
-- Get user's permitted documents (read-only)
SELECT document_id 
FROM permissions 
WHERE cognito_user_id = ?;
```

**Bedrock Retrieve Filter**:
```python
# Filter results to only permitted documents
filter = {
    'in': {
        'key': 'document_id',
        'value': permitted_document_ids  # List from database query
    }
}
```

**Search Function Restrictions**:
- Read-only database access via MCP (SELECT queries only)
- Cannot create, update, or delete documents
- Cannot grant or revoke permissions
- Cannot modify S3 Vectors (managed by Bedrock)
- All write operations must be performed by separate admin tools

### Error Handling
- Invalid cognito_user_id → 400 Bad Request
- No permission for any documents → Empty results
- Database/Bedrock errors → 503 Service Unavailable
- Invalid request → 400 Bad Request
- Any write attempt → 403 Forbidden (enforced by MCP/database permissions)

## Testing Strategy

### Core Tests Needed

**Unit Tests**:
- Permission query logic via MCP
- Filter construction for Bedrock Retrieve API
- Result parsing and formatting

**Integration Tests**:
- End-to-end search flow with permissions
- Bedrock KB retrieval with filters
- Permission filtering accuracy

**Security Tests**:
- Cannot access documents without permission
- Permission revocation takes immediate effect
- Search function cannot perform write operations
- Different users see different results

**Bedrock KB Tests**:
- Verify retrieval accuracy
- Test metadata filtering
- Validate permission-based filtering

## Implementation Notes

### Technology Choices
- **Language**: Python (for rapid prototyping)
- **RAG Framework**: Amazon Bedrock Knowledge Bases (fully managed)
- **Vector Storage**: S3 Vectors (managed by Bedrock)
- **Embedding Model**: Bedrock handles automatically (e.g., amazon.titan-embed-text-v2:0)
- **Database**: Aurora MySQL
- **Database Access**: MCP Server (aurora-db)
- **AWS Integration**: boto3 for Bedrock API calls

### AWS MCP Server Setup

**Installation**:
```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": ["-y", "@aws/mcp-server-aws"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "default"
      }
    }
  }
}
```

**IAM Configuration**:
- Agent uses IAM role with read-only permissions
- AWS MCP Server handles authentication via IAM

**Available Operations via MCP**:
- S3: GetObject, ListBucket (read HNSW index and vectors)
- RDS/Aurora: Execute SELECT queries (read permissions and documents)
- Cognito: ValidateToken, GetUser (authenticate users)

### HNSW Index Management
- **Initial Build**: Load all vectors from S3 via MCP, build HNSW index, save to disk (admin operation)
- **Index Storage**: Store serialized HNSW index in S3 for persistence
- **Startup**: Agent loads pre-built index from S3 via MCP into memory (read-only)
- **Updates**: New documents require admin tools to rebuild/update index
- **Index File**: `hnsw_index.bin` stored alongside vectors in S3
- **Agent Access**: Read-only access to index file via MCP, cannot modify or rebuild

### Database Access Control (PoC)
- **Database Credentials**: 
  - Username: `master`
  - Password: `Password1`
  - Host: Aurora/RDS endpoint
  - Database: `rag_system`
- **Connection via MCP**: Agent uses AWS MCP Server to execute SQL queries
- **Note**: For PoC simplicity, using single master user. In production, create separate read-only user for agent.

### S3 Access Control
- **Agent IAM Role**: Read-only access to vector bucket
  ```json
  {
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": ["arn:aws:s3:::document-vectors/*"]
  }
  ```
- **Admin IAM Role**: Full access for document ingestion and index updates
- **Access via MCP**: All S3 operations go through AWS MCP Server

### Simplifications for PoC
- Single HNSW index for all documents (no sharding)
- Admin tools handle all write operations (document ingestion, permission management, index rebuilds)
- Agent is strictly read-only, all AWS operations via MCP Server
- AWS MCP Server handles authentication and API calls
- Basic error handling (no circuit breakers or retry logic initially)
- No caching layer
- No pagination (return top-K only)

### Future Enhancements (Post-PoC)
- Incremental HNSW index updates (still via admin tools)
- Index sharding for horizontal scaling
- Multiple permission levels (if needed)
- Caching layer for permissions and frequent queries
- Batch processing for document ingestion
- Monitoring and observability via CloudWatch (accessible through MCP)
- A/B testing different HNSW parameters for optimal recall/speed tradeoff
- Use AWS MCP Server Agent SOPs for complex multi-step workflows
