# RAG System CLI Usage Guide

## Overview

The CLI provides an interactive interface to search documents using the permission-based RAG system with Amazon Bedrock.

## Features

- 👤 **User Selection**: Choose from 3 test users (Alice, Bob, Charlie)
- 🔍 **Simple Search**: Get a list of relevant documents with scores
- 🤖 **AI-Powered Search**: Get AI-generated answers using Claude Sonnet 4.5
- 🔒 **Permission Filtering**: Only see documents you have access to
- 🔄 **User Switching**: Switch between users to see different results

## Quick Start

### Run the Interactive CLI

```bash
cd justlim/AuroraS3VectorProject
python3 search_cli.py
```

### Run the Demo

```bash
python3 demo_cli.py
```

## Available Users

| User | Email | Documents | Range |
|------|-------|-----------|-------|
| Alice Smith | alice@example.com | 20 docs | doc-001 to doc-020 |
| Bob Johnson | bob@example.com | 25 docs | doc-011 to doc-035 |
| Charlie Brown | charlie@example.com | 20 docs | doc-031 to doc-050 |

**Note**: Bob's access overlaps with both Alice (doc-011 to doc-020) and Charlie (doc-031 to doc-035).

## Usage Examples

### Example 1: Simple Search

```
Select user: 1 (Alice)
Select option: 1 (Simple Search)
Enter query: "blockchain and cybersecurity"

Results:
1. Blockchain Technology Overview (score: 0.78)
2. Cybersecurity Best Practices (score: 0.69)
3. Edge Computing Explained (score: 0.58)
```

### Example 2: AI-Powered Search

```
Select user: 2 (Bob)
Select option: 2 (AI-Powered Search)
Enter question: "What is blockchain technology?"

Answer:
Blockchain is a distributed database shared among computer network nodes...
[Full AI-generated response]

Sources:
1. Blockchain Technology Overview (doc-004) - Score: 0.88
2. Nanotechnology Applications (doc-019) - Score: 0.58
```

### Example 3: Permission Differences

Search for "technology" as different users:

**Alice's Results:**
- Nanotechnology Applications
- Cybersecurity Best Practices
- Internet of Things Applications

**Bob's Results:**
- Nanotechnology Applications (shared with Alice)
- E-commerce Trends
- Entrepreneurship Guide

**Charlie's Results:**
- Educational Technology
- Online Learning Platforms
- STEM Education Importance

## Search Tips

### Good Queries

✅ **Specific topics**: "blockchain technology", "quantum computing"
✅ **Concepts**: "cybersecurity best practices", "machine learning"
✅ **Questions**: "What is nanotechnology?", "How does 5G work?"

### Less Effective Queries

❌ **Too broad**: "technology", "science"
❌ **Single words**: "computer", "health"
❌ **Unrelated topics**: Queries about topics not in the document set

## Document Topics

The system contains 50 documents across 5 topics:

- **Technology** (10 docs): Blockchain, AI, IoT, Cybersecurity, etc.
- **Science** (10 docs): Quantum Physics, Neuroscience, DNA, etc.
- **Business** (10 docs): Entrepreneurship, E-commerce, Analytics, etc.
- **Health** (10 docs): Nutrition, Mental Health, Telemedicine, etc.
- **Education** (10 docs): Online Learning, STEM, Assessment, etc.

## Technical Details

### How It Works

1. **User Selection**: Choose a user (loads their permissions from database)
2. **Query Input**: Enter your search query
3. **Permission Filtering**: System retrieves user's allowed document IDs
4. **Vector Search**: Bedrock KB searches S3 Vectors with permission filter
5. **Response Generation** (AI mode): Claude Sonnet 4.5 generates answer
6. **Results Display**: Shows documents with relevance scores

### Architecture

```
User Input
    ↓
Database Query (get permissions)
    ↓
Bedrock Knowledge Base
    ↓
S3 Vectors (filtered search)
    ↓
Claude Sonnet 4.5 (AI mode only)
    ↓
Results Display
```

### Models Used

- **Embedding Model**: Amazon Titan Text Embeddings V2 (1024 dimensions)
- **LLM Model**: Anthropic Claude Sonnet 4.5
- **Vector Store**: S3 Vectors (cosine similarity)

## Troubleshooting

### No Results Found

- Try a different query
- Check if the topic exists in the document set
- Verify the user has access to relevant documents

### Error Connecting to Database

- Ensure Aurora database is running
- Check database credentials in `search_functions.py`
- Verify network connectivity

### Bedrock API Errors

- Check AWS credentials are valid
- Ensure Bedrock Knowledge Base is active
- Verify region is set to us-east-2

## Files

- `search_cli.py` - Interactive CLI interface
- `demo_cli.py` - Automated demo script
- `search_functions.py` - Core search functions
- `test_users.json` - Test user credentials
- `test_rag_system.py` - Comprehensive test suite

## Next Steps

- Try different queries with different users
- Compare results between users to see permission filtering
- Use AI mode for complex questions requiring synthesis
- Run the test suite to validate system functionality
