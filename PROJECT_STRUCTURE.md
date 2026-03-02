# Project Structure

This document describes the final project structure for the Permission-Based RAG System PoC.

## Directory Layout

```
AuroraS3VectorProject/
├── Documentation/
│   ├── README.md                          # Main documentation
│   ├── QUICKSTART.md                      # Fast setup guide
│   ├── ARCHITECTURE_DIAGRAM.md            # System architecture
│   ├── CLI_USAGE.md                       # CLI usage guide
│   ├── DEMO_OUTPUT.md                     # Example CLI output
│   ├── design.md                          # Design document
│   ├── requirements.md                    # Requirements specification
│   └── PROJECT_STRUCTURE.md               # This file
│
├── Infrastructure/
│   └── cloudformation-template.yaml       # AWS infrastructure template
│
├── Database/
│   ├── init_database.sql                  # Database schema
│   └── run_init_sql.py                    # Database initialization script
│
├── Setup Scripts/
│   ├── setup_users_and_permissions.py     # Create Cognito users
│   ├── generate_fake_documents.py         # Generate test documents and embeddings
│   ├── upload_to_vector_bucket.py         # Upload to S3 Vectors
│   ├── create_bedrock_kb.py               # Create Knowledge Base
│   └── insert_documents.py                # Populate database
│
├── Core Application/
│   ├── search_functions.py                # Core search logic
│   ├── search_cli.py                      # Interactive CLI
│   └── demo_cli.py                        # Automated demo script
│
├── Testing/
│   ├── test_rag_system.py                 # Comprehensive test suite
│   ├── test_document_count.py             # Document count tests
│   └── test_mcp_queries.py                # MCP connection tests (optional)
│
├── Utilities/
│   └── mysql_shell.py                     # Database shell utility
│
├── Configuration/
│   ├── requirements.txt                   # Python dependencies
│   └── .gitignore                         # Git ignore rules
│
└── Generated Data/ (not in repo)
    ├── fake_documents.json                # Generated test documents
    ├── test_users.json                    # Test user credentials
    └── embeddings/                        # Vector embeddings (50 files)
```

## File Descriptions

### Documentation (6 files)

| File | Purpose |
|------|---------|
| README.md | Complete setup guide and documentation |
| QUICKSTART.md | Fast 30-minute setup guide |
| ARCHITECTURE_DIAGRAM.md | System architecture and data flow |
| CLI_USAGE.md | CLI interface usage examples |
| DEMO_OUTPUT.md | Example CLI session output |
| design.md | Technical design document |
| requirements.md | Requirements specification |

### Infrastructure (1 file)

| File | Purpose |
|------|---------|
| cloudformation-template.yaml | Creates Aurora, Cognito, IAM roles, VPC |

### Database (2 files)

| File | Purpose |
|------|---------|
| init_database.sql | SQL schema for documents and permissions tables |
| run_init_sql.py | Executes SQL initialization |

### Setup Scripts (6 files)

Run these in order during setup:

| Order | File | Purpose |
|-------|------|---------|
| 1 | setup_users_and_permissions.py | Creates 3 test users in Cognito |
| 2 | generate_fake_documents.py | Generates 50 test documents and 1024-dim embeddings |
| 3 | upload_to_vector_bucket.py | Uploads embeddings to S3 Vectors |
| 4 | create_bedrock_kb.py | Creates Bedrock Knowledge Base |
| 5 | insert_documents.py | Populates database with metadata |

### Core Application (3 files)

| File | Purpose |
|------|---------|
| search_functions.py | Core search and generation logic |
| search_cli.py | Interactive CLI for end users |
| demo_cli.py | Automated demo script |

### Testing (3 files)

| File | Purpose |
|------|---------|
| test_rag_system.py | 6 comprehensive tests (permissions, search, generation) |
| test_document_count.py | Verifies document count accuracy |
| test_mcp_queries.py | Tests MCP database connection (optional) |

### Utilities (1 file)

| File | Purpose |
|------|---------|
| mysql_shell.py | Interactive MySQL shell for debugging |

### Configuration (2 files)

| File | Purpose |
|------|---------|
| requirements.txt | Python dependencies (boto3, pymysql) |
| .gitignore | Excludes credentials, generated data, cache |

## Setup Workflow

```
1. Deploy Infrastructure
   └─> cloudformation-template.yaml

2. Initialize Database
   └─> run_init_sql.py (uses init_database.sql)

3. Create Test Data
   ├─> setup_users_and_permissions.py
   ├─> generate_fake_documents.py
   └─> regenerate_embeddings_titan.py

4. Setup Vector Storage
   ├─> Create S3 Vectors bucket (AWS CLI)
   ├─> upload_to_vector_bucket.py
   └─> create_bedrock_kb.py

5. Populate Database
   └─> insert_documents.py

6. Test System
   ├─> test_rag_system.py
   └─> test_document_count.py

7. Use Application
   └─> search_cli.py
```

## Removed Files

The following files were removed as they were intermediate development scripts:

- `add_permissions_to_vectors.py` - Merged into upload_to_vector_bucket.py
- `delete_old_s3_bucket.py` - One-time migration script
- `embedding_manifest.json` - Generated file
- `FIX_DOCUMENT_COUNT.md` - Internal development note
- `regenerate_embeddings_cohere.py` - Replaced by Titan version
- `setup_aws_infrastructure.py` - Replaced by CloudFormation
- `sg-rule.json` - Handled by CloudFormation
- `tasks.md` - Replaced by tasks-poc.md in specs
- `test_kb_filter.py` - Merged into test_rag_system.py
- `test_mcp_connection.py` - Redundant with test_mcp_queries.py
- `test_s3_vectors_query.py` - Merged into test_rag_system.py
- `update_database_for_s3vectors.py` - Merged into upload_to_vector_bucket.py
- `update_vector_metadata.py` - Merged into upload_to_vector_bucket.py
- `upload_to_s3.py` - Replaced by upload_to_vector_bucket.py

## Total File Count

- **Documentation**: 6 files
- **Infrastructure**: 1 file
- **Database**: 2 files
- **Setup Scripts**: 6 files
- **Core Application**: 3 files
- **Testing**: 3 files
- **Utilities**: 1 file
- **Configuration**: 2 files

**Total**: 24 files (clean, production-ready)

## Generated Files (Not in Repo)

These files are generated during setup and excluded by .gitignore:

- `fake_documents.json` - 50 test documents
- `test_users.json` - User credentials
- `embeddings/*.bin` - 50 embedding files

## Next Steps

1. Review README.md for complete setup instructions
2. Follow QUICKSTART.md for fast setup
3. Run tests to verify installation
4. Use search_cli.py to interact with the system
