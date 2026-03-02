#!/usr/bin/env python3
"""
Insert document metadata into Aurora database
"""
import pymysql
import json
import sys

# Database configuration
HOST = 'ams-s3-demo-auroracluster-souvtks7ayal.cluster-ctjk2qgb238i.us-east-2.rds.amazonaws.com'
USER = 'master'
PASSWORD = 'Passwordxxxx'
DATABASE = 'rag_system'
PORT = 3306

def load_documents():
    """Load documents from JSON file"""
    try:
        with open('fake_documents.json', 'r', encoding='utf-8') as f:
            documents = json.load(f)
        print(f"✓ Loaded {len(documents)} documents from fake_documents.json")
        return documents
    except FileNotFoundError:
        print("Error: fake_documents.json not found")
        print("Please run generate_fake_documents.py first")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading documents: {e}")
        sys.exit(1)

def insert_documents(documents):
    """Insert documents into Aurora database"""
    try:
        # Connect to database
        conn = pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            port=PORT,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        print(f"\n✓ Connected to database: {DATABASE}")
        print(f"Inserting {len(documents)} documents...")
        print("-" * 60)
        
        # Insert each document
        inserted = 0
        skipped = 0
        
        for doc in documents:
            document_id = doc['document_id']
            title = doc['title']
            s3_vector_key = f"vectors/{document_id}.bin"
            created_at = doc['created_at']
            metadata = json.dumps(doc['metadata'])
            
            try:
                # Insert document
                sql = """
                INSERT INTO documents (document_id, title, s3_vector_key, created_at, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (document_id, title, s3_vector_key, created_at, metadata))
                print(f"✓ Inserted: {document_id} - {title}")
                inserted += 1
                
            except pymysql.err.IntegrityError as e:
                if 'Duplicate entry' in str(e):
                    print(f"⊘ Skipped: {document_id} - already exists")
                    skipped += 1
                else:
                    raise
        
        # Commit transaction
        conn.commit()
        
        print("-" * 60)
        print(f"\nInsertion Summary:")
        print(f"  Inserted: {inserted}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {len(documents)}")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        print(f"\n✓ Total documents in database: {count}")
        
        cursor.close()
        conn.close()
        
        return inserted, skipped
        
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Insert Documents into Aurora Database")
    print("="*60)
    
    # Load documents
    documents = load_documents()
    
    # Insert documents
    inserted, skipped = insert_documents(documents)
    
    print("\n" + "="*60)
    print("  Insertion Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Create test users in Cognito")
    print("  2. Create permission records in database")

if __name__ == "__main__":
    main()
