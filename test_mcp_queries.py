#!/usr/bin/env python3
"""
Test MCP database queries to verify Task 3.2
"""
import pymysql

# Database configuration
HOST = 'ams-s3-demo-auroracluster-souvtks7ayal.cluster-ctjk2qgb238i.us-east-2.rds.amazonaws.com'
USER = 'master'
PASSWORD = 'Password1'
DATABASE = 'rag_system'
PORT = 3306

def test_mcp_queries():
    """Test various database queries that MCP will execute"""
    print("\n" + "="*60)
    print("  Test MCP Database Queries")
    print("="*60)
    
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
        
        print("\n✓ Connected to database")
        
        # Test 1: Count documents
        print("\n1. Count documents:")
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        print(f"   Result: {count} documents")
        
        # Test 2: Count permissions
        print("\n2. Count permissions:")
        cursor.execute("SELECT COUNT(*) FROM permissions")
        count = cursor.fetchone()[0]
        print(f"   Result: {count} permissions")
        
        # Test 3: Show tables
        print("\n3. Show tables:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # Test 4: Get permissions for a specific user (Alice)
        print("\n4. Get permissions for Alice (71dba540-5051-7063-4bbb-ae83e587a324):")
        cursor.execute("""
            SELECT document_id 
            FROM permissions 
            WHERE cognito_user_id = %s
            ORDER BY document_id
        """, ('71dba540-5051-7063-4bbb-ae83e587a324',))
        docs = cursor.fetchall()
        print(f"   Result: {len(docs)} documents")
        print(f"   Sample: {[doc[0] for doc in docs[:5]]}")
        
        # Test 5: Get document metadata
        print("\n5. Get document metadata (first 3):")
        cursor.execute("""
            SELECT document_id, title, s3_vector_key 
            FROM documents 
            LIMIT 3
        """)
        docs = cursor.fetchall()
        for doc_id, title, s3_key in docs:
            print(f"   - {doc_id}: {title}")
            print(f"     S3 Key: {s3_key}")
        
        # Test 6: Get permissions grouped by document
        print("\n6. Get permissions grouped by document (first 5):")
        cursor.execute("""
            SELECT document_id, GROUP_CONCAT(cognito_user_id) as users
            FROM permissions
            GROUP BY document_id
            LIMIT 5
        """)
        perms = cursor.fetchall()
        for doc_id, users in perms:
            user_count = len(users.split(','))
            print(f"   - {doc_id}: {user_count} users")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("  All MCP Query Tests Passed!")
        print("="*60)
        print("\n✓ Task 3.2 Complete: MCP database queries verified")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_mcp_queries()
