# Quick Start Guide

Get the Permission-Based RAG system running in ~30 minutes.

## Prerequisites Checklist

- [ ] AWS Account with admin access
- [ ] AWS CLI installed and configured
- [ ] Python 3.9+ installed
- [ ] Bedrock model access enabled (Claude Sonnet 4.5, Titan Embeddings V2)

## Quick Setup (10 Commands)

```bash
# 1. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Deploy AWS infrastructure (~10 min)
aws cloudformation create-stack \
  --stack-name rag-system-poc \
  --template-body file://cloudformation-template.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-2

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name rag-system-poc \
  --region us-east-2

# 3. Initialize database
python run_init_sql.py

# 4. Generate test data (documents and embeddings)
python generate_fake_documents.py

# 5. Insert documents into database
python insert_documents.py

# 6. Create test users and permissions
python setup_users_and_permissions.py

# 7. Upload embeddings to S3 Vectors (bucket created by CloudFormation)
python upload_to_vector_bucket.py

# 8. Create Knowledge Base
python create_bedrock_kb.py
# IMPORTANT: Copy the Knowledge Base ID from output

# 9. Update search_functions.py with your KB ID
# Edit line 11: KB_ID = 'YOUR_KB_ID_HERE'

# 10. Test the system
python test_rag_system.py
```

## Run the CLI

```bash
python search_cli.py
```

## Test Users

- **Alice**: alice@example.com (20 documents: Technology, Science)
- **Bob**: bob@example.com (25 documents: Science, Business, Health)
- **Charlie**: charlie@example.com (20 documents: Health, Education)

Password for all: `TempPass123!`

## Common Issues

### "ExpiredToken" Error
```bash
# Refresh AWS credentials
aws sts get-caller-identity
```

### "Access Denied" to Bedrock
Enable model access in AWS Console:
1. Go to Bedrock console
2. Click "Model access"
3. Enable Claude Sonnet 4.5 and Titan Embeddings V2

### Database Connection Failed
Check Aurora endpoint in CloudFormation outputs:
```bash
aws cloudformation describe-stacks \
  --stack-name rag-system-poc \
  --query 'Stacks[0].Outputs[?OutputKey==`AuroraClusterEndpoint`].OutputValue' \
  --output text
```

Update `DB_HOST` in `search_functions.py` with this endpoint.

### No Search Results
1. Verify embeddings uploaded: Check S3 Vectors console
2. Verify KB is active: Check Bedrock console
3. Check permissions: `python test_mcp_queries.py`

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Review [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) for system design
- Check [CLI_USAGE.md](CLI_USAGE.md) for usage examples

## Cleanup

```bash
# Delete everything (replace 319165777908 with your AWS account ID)
aws bedrock-agent delete-knowledge-base --knowledge-base-id <your-kb-id> --region us-east-2
aws s3vectors delete-vector-index --bucket-name ragvec-319165777908 --index-name documents --region us-east-2
aws s3vectors delete-vector-bucket --bucket-name ragvec-319165777908 --region us-east-2
aws cloudformation delete-stack --stack-name rag-system-poc --region us-east-2
```

## Cost Estimate

- **Setup**: ~$0.50 (one-time)
- **Running**: ~$0.10-0.50/hour
- **Daily (active use)**: ~$5-10

Stop Aurora cluster when not in use to save costs.
