# AWS Permission-Based RAG System Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT SIDE                                    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         search_cli.py                                │   │
│  │  • User selects identity (Alice/Bob/Charlie)                         │   │
│  │  • Enters search query                                               │   │
│  │  • Chooses search mode (Simple/AI-Powered)                           │   │
│  └────────────────────────┬─────────────────────────────────────────────┘   │
│                           │                                                 │
│                           │ Calls search_functions.py                       │
│                           ▼                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    search_functions.py                               │   │
│  │  • get_user_permissions(cognito_user_id)                             │   │
│  │  • search_with_permissions(query, user_id, top_k)                    │   │
│  │  • search_and_generate(query, user_id, top_k)                        │   │
│  └────────────────────────┬─────────────────────────────────────────────┘   │
│                           │                                                 │
└───────────────────────────┼─────────────────────────────────────────────────┘
                            │
                            │ AWS SDK (boto3)
                            │
┌───────────────────────────┼──────────────────────────────────────────────────┐
│                           │              AWS CLOUD (us-east-2)               │
│                           ▼                                                  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │                    STEP 1: Get User Permissions                     │   │
│  │                                                                     │   │
│  │   ┌───────────────────────────────────────────────────────────┐     │   │
│  │   │  Aurora MySQL Cluster                                     │     │   │
│  │   │  rag-system-poc-aurora-cluster                            │     │   │
│  │   │  ┌─────────────────────────────────────────────────────┐  │     │   │
│  │   │  │  Database: rag_system                               │  │     │   │
│  │   │  │                                                     │  │     │   │
│  │   │  │  Table: permissions                                 │  │     │   │
│  │   │  │  ┌────────────────┬──────────────┬────────────┐     │  │     │   │
│  │   │  │  │ cognito_user_id│ document_id  │ permission │     │  │     │   │
│  │   │  │  ├────────────────┼──────────────┼────────────┤     │  │     │   │
│  │   │  │  │ alice-uuid     │ doc-001      │ read       │     │  │     │   │
│  │   │  │  │ alice-uuid     │ doc-002      │ read       │     │  │     │   │
│  │   │  │  │ ...            │ ...          │ ...        │     │  │     │   │
│  │   │  │  └────────────────┴──────────────┴────────────┘     │  │     │   │
│  │   │  │                                                     │  │     │   │
│  │   │  │  Table: documents                                   │  │     │   │
│  │   │  │  ┌────────────┬────────┬────────┬──────────────┐    │  │     │   │
│  │   │  │  │ document_id│ title  │ topic  │ s3_key       │    │  │     │   │
│  │   │  │  ├────────────┼────────┼────────┼──────────────┤    │  │     │   │
│  │   │  │  │ doc-001    │ Block..│ tech   │ s3vectors:// │    │  │     │   │
│  │   │  │  │ doc-002    │ Cloud..│ tech   │ s3vectors:// │    │  │     │   │
│  │   │  │  └────────────┴────────┴────────┴──────────────┘    │  │     │   │
│  │   │  └─────────────────────────────────────────────────┘   │  │     │
│  │   │                                                        │  │     │
│  │   │  Returns: Set of document IDs user can access          │  │     │
│  │   │  Example: {doc-001, doc-002, ..., doc-020}             │  │     │
│  │   └─────────────────────────────────────────────────────── ┘  │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                           │                                              │
│                           │ Document IDs                                 │
│                           ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              STEP 2: Vector Search with Permissions                  │   │
│  │                                                                       │   │
│  │   ┌───────────────────────────────────────────────────────────┐     │   │
│  │   │  Amazon Bedrock Knowledge Base                            │     │   │
│  │   │  ID: L8DUDPP5M4                                           │     │   │
│  │   │  Name: rag-permissions-poc-kb                             │     │   │
│  │   │                                                            │     │   │
│  │   │  Embedding Model: Amazon Titan Text Embeddings V2         │     │   │
│  │   │  Dimensions: 1024                                          │     │   │
│  │   │                                                            │     │   │
│  │   │  Query: "blockchain and cybersecurity"                    │     │   │
│  │   │  Filter: document_id IN [doc-001, doc-002, ..., doc-020] │     │   │
│  │   │  Top K: 3-5 results                                       │     │   │
│  │   └─────────────────────┬─────────────────────────────────────┘     │   │
│  │                         │                                             │   │
│  │                         │ Queries                                     │   │
│  │                         ▼                                             │   │
│  │   ┌───────────────────────────────────────────────────────────┐     │   │
│  │   │  S3 Vectors Storage                                       │     │   │
│  │   │  Bucket: rag-system-vectors                               │     │   │
│  │   │  Index: documents                                          │     │   │
│  │   │                                                            │     │   │
│  │   │  Vector Index Configuration:                              │     │   │
│  │   │  • Dimensions: 1024                                       │     │   │
│  │   │  • Similarity: Cosine                                     │     │   │
│  │   │  • Data Type: float32                                     │     │   │
│  │   │                                                            │     │   │
│  │   │  Stored Vectors:                                          │     │   │
│  │   │  ┌──────────────┬─────────────────┬──────────────────┐   │     │   │
│  │   │  │ document_id  │ vector (1024d)  │ metadata         │   │     │   │
│  │   │  ├──────────────┼─────────────────┼──────────────────┤   │     │   │
│  │   │  │ doc-001      │ [0.23, -0.45,...]│ {title, topic}  │   │     │   │
│  │   │  │ doc-002      │ [0.12, 0.89,...]│ {title, topic}   │   │     │   │
│  │   │  │ ...          │ ...             │ ...              │   │     │   │
│  │   │  └──────────────┴─────────────────┴──────────────────┘   │     │   │
│  │   │                                                            │     │   │
│  │   │  Returns: Top K matching vectors with scores              │     │   │
│  │   └───────────────────────────────────────────────────────────┘     │   │
│  │                                                                       │   │
│  │   Returns to client:                                                 │   │
│  │   • document_id: doc-004                                             │   │
│  │   • score: 0.8789                                                    │   │
│  │   • metadata: {title: "Blockchain...", topic: "technology"}          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
│                           │ Search Results                               │
│                           ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              STEP 3: Generate Response (AI Mode Only)                │   │
│  │                                                                       │   │
│  │   ┌───────────────────────────────────────────────────────────┐     │   │
│  │   │  Amazon Bedrock Runtime                                   │     │   │
│  │   │                                                            │     │   │
│  │   │  Model: Anthropic Claude Sonnet 4.5                       │     │   │
│  │   │  ID: us.anthropic.claude-sonnet-4-5-20250929-v1:0         │     │   │
│  │   │                                                            │     │   │
│  │   │  Input Prompt:                                            │     │   │
│  │   │  ┌────────────────────────────────────────────────────┐   │     │   │
│  │   │  │ You are a helpful assistant...                     │   │     │   │
│  │   │  │                                                     │   │     │   │
│  │   │  │ User has access to 20 documents total.             │   │     │   │
│  │   │  │ Below are the 3 most relevant results.             │   │     │   │
│  │   │  │                                                     │   │     │   │
│  │   │  │ Documents:                                          │   │     │   │
│  │   │  │ [Document 1 - doc-004: Blockchain Technology...]   │   │     │   │
│  │   │  │ {full document content}                            │   │     │   │
│  │   │  │                                                     │   │     │   │
│  │   │  │ [Document 2 - doc-003: Cybersecurity...]           │   │     │   │
│  │   │  │ {full document content}                            │   │     │   │
│  │   │  │                                                     │   │     │   │
│  │   │  │ User Question: "What is blockchain?"               │   │     │   │
│  │   │  └────────────────────────────────────────────────────┘   │     │   │
│  │   │                                                            │     │   │
│  │   │  Returns: Generated natural language response             │     │   │
│  │   └───────────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
└───────────────────────────┼──────────────────────────────────────────────────┘
                            │ Response
                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              CLIENT SIDE                                   │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                    Display Results to User                            │ │
│  │                                                                        │ │
│  │  Simple Search Mode:                                                  │ │
│  │  ✅ Found 3 results:                                                  │ │
│  │  1. 📄 Blockchain Technology Overview                                │ │
│  │     ID: doc-004 | Topic: technology | Score: 0.8789                  │ │
│  │                                                                        │ │
│  │  AI-Powered Mode:                                                     │ │
│  │  💡 Answer:                                                           │ │
│  │  Blockchain technology is a distributed database...                  │ │
│  │                                                                        │ │
│  │  📊 Access Summary:                                                   │ │
│  │  • Total accessible documents: 20                                     │ │
│  │  • Documents used for this answer: 3                                  │ │
│  │                                                                        │ │
│  │  📚 Sources:                                                          │ │
│  │  1. Blockchain Technology Overview (doc-004) - Score: 0.8789         │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Summary

### Simple Search Flow
1. **User Input** → CLI captures user selection and query
2. **Permission Check** → Query Aurora MySQL for user's document IDs
3. **Vector Search** → Bedrock KB searches S3 Vectors with permission filter
4. **Display Results** → Show document list with scores

### AI-Powered Search Flow
1. **User Input** → CLI captures user selection and question
2. **Permission Check** → Query Aurora MySQL for user's document IDs
3. **Vector Search** → Bedrock KB searches S3 Vectors with permission filter
4. **Load Content** → Retrieve full document text from fake_documents.json
5. **Generate Response** → Claude Sonnet 4.5 generates answer from documents
6. **Display Answer** → Show generated response with sources

## Key Components

### Client Side
- **search_cli.py**: Interactive CLI interface
- **search_functions.py**: Core search and generation logic
- **fake_documents.json**: Full document content (50 documents)
- **test_users.json**: Test user credentials

### AWS Infrastructure
- **Aurora MySQL**: Stores permissions and document metadata
- **S3 Vectors**: Stores 1024-dimensional embeddings
- **Bedrock Knowledge Base**: Orchestrates vector search
- **Bedrock Runtime**: Runs Claude Sonnet 4.5 for response generation

### Security Model
- Permissions enforced at query time via document_id filter
- No direct access to S3 Vectors without permission check
- Each user sees only their authorized documents
