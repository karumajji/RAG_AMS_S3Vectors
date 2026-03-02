# CLI Demo Output

## User Selection Screen

```
======================================================================
  🔍 PERMISSION-BASED RAG SYSTEM
  Secure Document Search with Amazon Bedrock
======================================================================

📋 Available Users:
----------------------------------------------------------------------
  1. Alice Smith (alice@example.com)
     Access: 20 documents
     Topics: Science, Technology
  2. Bob Johnson (bob@example.com)
     Access: 25 documents
     Topics: Business, Health, Science
  3. Charlie Brown (charlie@example.com)
     Access: 20 documents
     Topics: Education, Health
----------------------------------------------------------------------

👤 Select user (1-3) or 'q' to quit: 1

✅ Logged in as: Alice Smith (alice@example.com)

📋 Alice Smith's Document Access:
----------------------------------------------------------------------
Total documents: 20
Document range: doc-001 to doc-020

📚 Available Topics:
  • Science: 10 documents
  • Technology: 10 documents

💡 Example Queries:
  • Science: "quantum physics", "neuroscience", "DNA research"
  • Technology: "blockchain", "cybersecurity", "artificial intelligence"
----------------------------------------------------------------------
```

## Search Options Menu

```
🔎 Search Options:
  1. Simple Search (returns document list)
  2. AI-Powered Search (generates answer with Claude Sonnet 4.5)
  3. Switch User
  4. Quit

Select option (1-4): 1
```

## Simple Search Example

```
💬 Enter your search query: blockchain and cybersecurity

🔍 Searching for: 'blockchain and cybersecurity'
👤 User: Alice Smith
----------------------------------------------------------------------

✅ Found 5 results:

1. 📄 Blockchain Technology Overview
   ID: doc-004 | Topic: technology | Score: 0.7822

2. 📄 Cybersecurity Best Practices
   ID: doc-003 | Topic: technology | Score: 0.6898

3. 📄 Edge Computing Explained
   ID: doc-010 | Topic: technology | Score: 0.5802

4. 📄 5G Network Technology
   ID: doc-008 | Topic: technology | Score: 0.5515

5. 📄 Quantum Computing Basics
   ID: doc-007 | Topic: technology | Score: 0.5477
```

## AI-Powered Search Example

```
Select option (1-4): 2

💬 Enter your question: What is blockchain technology?

🔍 Searching for: 'What is blockchain technology?'
👤 User: Alice Smith
🤖 Generating answer with Claude Sonnet 4.5...
----------------------------------------------------------------------

💡 Answer:

Based on Document 1, blockchain technology is a distributed database or 
ledger that is shared among the nodes of a computer network, storing 
information electronically in digital format.

Key characteristics of blockchain:
- It's particularly known for its role in cryptocurrency systems
- Maintains secure and decentralized transaction records
- Guarantees the fidelity and security of data records
- Generates trust without requiring a trusted third party

The key innovation of blockchain is its ability to guarantee the fidelity 
and security of a record of data while maintaining decentralization.

📚 Sources (3 documents):
  1. Blockchain Technology Overview (doc-004) - Score: 0.8789
  2. Nanotechnology Applications (doc-019) - Score: 0.5826
  3. Edge Computing Explained (doc-010) - Score: 0.5824
```

## User Switching Example

```
Select option (1-4): 3

======================================================================
📋 Available Users:
----------------------------------------------------------------------
  1. Alice Smith (alice@example.com)
     Access: 20 documents
     Topics: Science, Technology
  2. Bob Johnson (bob@example.com)
     Access: 25 documents
     Topics: Business, Health, Science
  3. Charlie Brown (charlie@example.com)
     Access: 20 documents
     Topics: Education, Health
----------------------------------------------------------------------

👤 Select user (1-3) or 'q' to quit: 2

✅ Switched to: Bob Johnson (bob@example.com)

📋 Bob Johnson's Document Access:
----------------------------------------------------------------------
Total documents: 25
Document range: doc-011 to doc-035

📚 Available Topics:
  • Business: 10 documents
  • Health: 5 documents
  • Science: 10 documents

💡 Example Queries:
  • Business: "entrepreneurship", "e-commerce", "business strategy"
  • Health: "nutrition", "mental health", "telemedicine"
  • Science: "quantum physics", "neuroscience", "DNA research"
----------------------------------------------------------------------
```

## Permission Filtering in Action

### Same Query, Different Users

**Query**: "technology and innovation"

**Alice's Results** (Technology + Science):
```
1. doc-019: Nanotechnology Applications (score: 0.6098)
2. doc-003: Cybersecurity Best Practices (score: 0.5712)
3. doc-005: Internet of Things Applications (score: 0.5699)
```

**Bob's Results** (Business + Health + Science):
```
1. doc-019: Nanotechnology Applications (score: 0.6098)
2. doc-027: E-commerce Trends (score: 0.6010)
3. doc-024: Entrepreneurship Guide (score: 0.5663)
```

**Charlie's Results** (Education + Health):
```
1. doc-042: Educational Technology (score: 0.6285)
2. doc-041: Online Learning Platforms (score: 0.5782)
3. doc-043: STEM Education Importance (score: 0.5629)
```

## Key Features Demonstrated

✅ **Topic-Based User Display**: Shows which topics each user can access
✅ **Example Queries**: Provides relevant query suggestions per topic
✅ **Permission Filtering**: Different users see different results
✅ **Relevance Scores**: High-quality semantic search (0.6-0.8 range)
✅ **AI Response Generation**: Claude Sonnet 4.5 synthesizes answers
✅ **Source Citations**: Shows which documents were used
✅ **User Switching**: Easy to compare results between users
