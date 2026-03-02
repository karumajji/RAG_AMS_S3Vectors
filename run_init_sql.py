#!/usr/bin/env python3
"""
Run SQL initialization script against Aurora MySQL database
"""
import pymysql
import sys

# Database connection details
DB_HOST = "ams-s3-demo-auroracluster-souvtks7ayal.cluster-ctjk2qgb238i.us-east-2.rds.amazonaws.com"
DB_USER = "master"
DB_PASSWORD = "Password1"
DB_NAME = "rag_system"
DB_PORT = 3306

def run_init_sql():
    """Execute the initialization SQL script"""
    try:
        print(f"Connecting to {DB_HOST}...")
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            connect_timeout=30
        )
        
        print("Connected successfully!")
        cursor = connection.cursor()
        
        # Create documents table
        print("\nCreating documents table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                s3_vector_key VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
        """)
        print("✓ Documents table created")
        
        # Create permissions table
        print("\nCreating permissions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                cognito_user_id VARCHAR(255) NOT NULL,
                document_id VARCHAR(255) NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
                UNIQUE KEY (cognito_user_id, document_id),
                INDEX (cognito_user_id)
            )
        """)
        print("✓ Permissions table created")
        
        connection.commit()
        
        # Verify tables
        print("\nVerifying tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n✓ Database initialization completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(run_init_sql())
