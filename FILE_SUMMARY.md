# Project File Summary

## 📋 Documentation Files

### README.md
**Purpose**: Main project documentation  
**Used**: Entry point for understanding the entire system  
**Why**: Provides setup instructions, architecture overview, usage guide, and troubleshooting

### ARCHITECTURE_DIAGRAM.md
**Purpose**: Visual system architecture with ASCII diagrams  
**Used**: Understanding data flow and component interactions  
**Why**: Shows how client, AWS services, and data storage work together

### architecture-visual.md
**Purpose**: Mermaid diagrams for visual architecture  
**Used**: Creating presentation-ready architecture diagrams  
**Why**: Provides multiple diagram types (flowchart, sequence, ER) for different audiences

### CLI_USAGE.md
**Purpose**: Command-line interface usage guide  
**Used**: Learning how to interact with the search CLI  
**Why**: Documents user workflows, search modes, and example queries

### PROJECT_STRUCTURE.md
**Purpose**: File organization and project layout  
**Used**: Understanding where files are located  
**Why**: Helps developers navigate the codebase

### QUICKSTART.md
**Purpose**: Fast setup guide  
**Used**: Getting the system running quickly  
**Why**: Condensed version of README for experienced users

### DEMO_OUTPUT.md
**Purpose**: Example outputs and test results  
**Used**: Seeing what the system produces  
**Why**: Shows expected behavior and sample responses

### GITHUB_SETUP.md
**Purpose**: GitHub repository setup instructions  
**Used**: Publishing project to GitHub  
**Why**: Documents how to create repo, push code, and configure settings

### requirements.md
**Purpose**: Original requirements specification  
**Used**: Understanding project goals and constraints  
**Why**: Defines what the system should accomplish

### design.md
**Purpose**: Technical design decisions  
**Used**: Understanding why certain technologies were chosen  
**Why**: Documents architecture choices and trade-offs

---

## 🏗️ Infrastructure Files

### cloudformation-template.yaml
**Purpose**: AWS infrastructure as code  
**Used**: Deploying Aurora, Cognito, S3, IAM roles  
**Why**: Automates AWS resource creation with one command  
**Key Resources**:
- Aurora MySQL cluster
- Cognito User Pool
- S3 bucket (later replaced by S3 Vectors)
- IAM roles and policies

---

## 🗄️ Database Files

### init_database.sql
**Purpose**: Database schema definition  
**Used**: Creating tables in Aurora MySQL  
**Why**: Defines `documents` and `permissions` table structures  
**Tables**:
- `documents`: Stores document metadata (id, title, topic, s3_key)
- `permissions`: Maps users to documents (cognito_user_id, document_id)

### run_init_sql.py
**Purpose**: Execute SQL schema on Aurora  
**Used**: Setup phase - initializes database  
**Why**: Automates running init_database.sql against Aurora cluster  
**When**: Run once after CloudFormation stack is created

### mysql_shell.py
**Purpose**: Interactive MySQL shell  
**Used**: Manual database queries and debugging  
**Why**: Provides direct access to Aurora for troubleshooting  
**Usage**: `python mysql_shell.py` then enter SQL commands

---

## 📝 Data Generation Files

### generate_fake_documents.py
**Purpose**: Create 50 test documents  
**Used**: Setup phase - generates sample data  
**Why**: Creates realistic documents across 5 topics for testing  
**Output**: `fake_documents.json` (50 documents with content)  
**Topics**: Technology, Healthcare, Finance, Education, Environment

### fake_documents.json
**Purpose**: Stores generated document content  
**Used**: By search functions to load full document text  
**Why**: Provides actual content for Claude to generate answers from  
**Structure**: Array of 50 documents with id, title, content, metadata

### insert_documents.py
**Purpose**: Populate Aurora with document metadata  
**Used**: Setup phase - loads documents into database  
**Why**: Inserts records from fake_documents.json into `documents` table  
**When**: Run after generate_fake_documents.py

---

## 🔐 User & Permission Files

### setup_users_and_permissions.py
**Purpose**: Create test users in Cognito and set permissions  
**Used**: Setup phase - creates Alice, Bob, Charlie  
**Why**: Establishes user identities and document access rules  
**Creates**:
- 3 Cognito users with passwords
- Permission records in Aurora
- test_users.json with user IDs

### test_users.json
**Purpose**: Stores Cognito user IDs and credentials  
**Used**: By CLI and test scripts to authenticate users  
**Why**: Maps user names to Cognito UUIDs for permission lookups  
**Users**:
- Alice: 20 docs (doc-001 to doc-020)
- Bob: 25 docs (doc-011 to doc-035)
- Charlie: 20 docs (doc-031 to doc-050)

---

## 🧮 Embedding Files

### embeddings/ (directory)
**Purpose**: Stores 50 binary embedding files  
**Used**: Uploaded to S3 Vectors  
**Why**: Contains 1024-dimensional vectors for each document  
**Files**: doc-001.bin through doc-050.bin  
**Format**: Binary float32 arrays (1024 dimensions each)

### embedding_manifest.json
**Purpose**: Metadata about embeddings  
**Used**: Tracking embedding generation details  
**Why**: Documents which model created embeddings and when  
**Info**: Model name, dimensions, generation timestamp

### upload_to_vector_bucket.py
**Purpose**: Upload embeddings to S3 Vectors  
**Used**: Setup phase - populates vector storage  
**Why**: Transfers local embeddings to AWS S3 Vectors with metadata  
**Process**:
1. Reads .bin files from embeddings/
2. Uploads to S3 Vectors bucket
3. Attaches document metadata to each vector

---

## 🧠 Bedrock Knowledge Base Files

### create_bedrock_kb.py
**Purpose**: Create and configure Bedrock Knowledge Base  
**Used**: Setup phase - creates KB pointing to S3 Vectors  
**Why**: Sets up the vector search engine with Titan embeddings  
**Configuration**:
- Links to S3 Vectors bucket
- Configures Titan Text Embeddings V2
- Sets up 1024-dimensional vector search
- Returns KB ID for use in search_functions.py

---

## 🔍 Search & Query Files

### search_functions.py
**Purpose**: Core search logic and AI generation  
**Used**: By search_cli.py and test scripts  
**Why**: Implements permission-filtered vector search and Claude integration  
**Functions**:
- `get_user_pawsermissions()`: Queries Aurora for user's doc IDs
- `search_with_permissions()`: Bedrock KB search with filters
- `search_and_generate()`: Full RAG pipeline with Claude
**Dependencies**: boto3, pymysql, fake_documents.json

### search_cli.py
**Purpose**: Interactive command-line interface  
**Used**: Main user interface for the system  
**Why**: Provides friendly way to test searches as different users  
**Features**:
- User selection menu
- Simple search mode (returns doc list)
- AI-powered mode (generates answers)
- User switching without restart

### demo_cli.py
**Purpose**: Automated demo script  
**Used**: Demonstrating system capabilities  
**Why**: Runs pre-scripted queries to showcase features  
**Scenarios**: Shows different users, queries, and permission filtering

---

## 🧪 Test Files

### test_rag_system.py
**Purpose**: Comprehensive system tests  
**Used**: Validating entire RAG pipeline  
**Why**: Ensures permissions, search, and generation work correctly  
**Tests**:
- User permission counts
- Permission overlap (Bob shares docs with Alice & Charlie)
- Search result filtering
- Claude response generation
- Unauthorized access prevention

### test_document_count.py
**Purpose**: Test document count accuracy  
**Used**: Validating total accessible document reporting  
**Why**: Ensures Claude knows user's total doc count vs. retrieved count  
**Validates**: Fixed bug where Claude reported wrong total

### test_mcp_queries.py
**Purpose**: Test MCP (Model Context Protocol) integration  
**Used**: If using MCP server for database access  
**Why**: Validates alternative database access method  
**Note**: Optional - project uses direct pymysql by default

---

## 📦 Configuration Files

### requirements.txt
**Purpose**: Python package dependencies  
**Used**: Installing required libraries  
**Why**: Ensures consistent environment across setups  
**Packages**:
- boto3: AWS SDK
- pymysql: MySQL database driver
- numpy: Vector operations

### .gitignore
**Purpose**: Exclude files from Git  
**Used**: Keeping sensitive data out of version control  
**Why**: Prevents committing credentials, virtual env, cache files  
**Excludes**:
- .venv/
- *.pyc
- test_users.json
- .DS_Store

---

## 📊 File Usage Flow

### Setup Phase (Run Once)
```
1. cloudformation-template.yaml     → Deploy AWS infrastructure
2. run_init_sql.py                  → Create database schema
3. generate_fake_documents.py       → Generate test documents
4. insert_documents.py              → Populate database
5. setup_users_and_permissions.py   → Create users & permissions
6. upload_to_vector_bucket.py       → Upload embeddings to S3 Vectors
7. create_bedrock_kb.py             → Create Knowledge Base
```

### Runtime Phase (Repeated Use)
```
1. search_cli.py                    → User interface
   ↓
2. search_functions.py              → Core logic
   ↓
3. Aurora MySQL                     → Get permissions
   ↓
4. Bedrock KB + S3 Vectors          → Vector search
   ↓
5. fake_documents.json              → Load content
   ↓
6. Claude Sonnet 4.5                → Generate answer
   ↓
7. Display to user
```

### Testing Phase
```
1. test_rag_system.py               → Full system validation
2. test_document_count.py           → Count accuracy
3. test_mcp_queries.py              → MCP integration (optional)
```

### Debugging Phase
```
1. mysql_shell.py                   → Query database directly
2. demo_cli.py                      → Run automated demos
```

---

## 🎯 Key File Relationships

### Data Pipeline
```
generate_fake_documents.py
  ↓ creates
fake_documents.json
  ↓ read by
insert_documents.py → Aurora MySQL
  ↓ also read by
upload_to_vector_bucket.py → S3 Vectors
  ↓ indexed by
create_bedrock_kb.py → Bedrock KB
  ↓ queried by
search_functions.py
  ↓ used by
search_cli.py
```

### Permission Flow
```
setup_users_and_permissions.py
  ↓ creates
Cognito Users + test_users.json
  ↓ and
Aurora permissions table
  ↓ queried by
search_functions.py
  ↓ filters
Bedrock KB search results
```

### Configuration Chain
```
cloudformation-template.yaml
  ↓ creates
Aurora endpoint, Cognito pool, S3 bucket
  ↓ used by
All Python scripts (hardcoded or from outputs)
  ↓ connects to
AWS services
```

---

## 💡 Quick Reference

**Want to...**
- **Set up the system?** → Follow README.md, run setup scripts in order
- **Understand architecture?** → Read ARCHITECTURE_DIAGRAM.md
- **Use the system?** → Run search_cli.py
- **Test everything?** → Run test_rag_system.py
- **Debug database?** → Use mysql_shell.py
- **See examples?** → Check DEMO_OUTPUT.md or run demo_cli.py
- **Modify permissions?** → Edit setup_users_and_permissions.py and re-run
- **Add documents?** → Edit generate_fake_documents.py, regenerate, re-upload
- **Change AWS config?** → Update cloudformation-template.yaml and redeploy

---

## 🔧 Files You'll Modify Most

1. **search_functions.py** - Update KB_ID, DB credentials, LLM model
2. **setup_users_and_permissions.py** - Change user permissions
3. **generate_fake_documents.py** - Add/modify test documents
4. **cloudformation-template.yaml** - Adjust AWS resources

## 📁 Files You'll Never Touch

1. **fake_documents.json** - Auto-generated
2. **test_users.json** - Auto-generated
3. **embeddings/*.bin** - Auto-generated
4. **embedding_manifest.json** - Auto-generated

