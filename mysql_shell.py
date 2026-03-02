#!/usr/bin/env python3
"""
Interactive MySQL Shell for Aurora Database
"""
import pymysql
import sys

# Database connection details
HOST = 'ams-s3-demo-auroracluster-souvtks7ayal.cluster-ctjk2qgb238i.us-east-2.rds.amazonaws.com'
USER = 'master'
PASSWORD = 'Password1'
DATABASE = 'rag_system'
PORT = 3306

def main():
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
        
        print(f"Connected to {DATABASE} database!")
        print("Type SQL queries (or 'exit' to quit):")
        print("-" * 50)
        
        while True:
            try:
                # Read query
                query = input("\nmysql> ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                
                if not query:
                    continue
                
                # Execute query
                cursor.execute(query)
                
                # Fetch results if it's a SELECT query
                if query.lower().startswith('select') or query.lower().startswith('show') or query.lower().startswith('describe'):
                    results = cursor.fetchall()
                    if results:
                        for row in results:
                            print(row)
                    else:
                        print("Empty set")
                else:
                    conn.commit()
                    print(f"Query OK, {cursor.rowcount} rows affected")
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")
        
        cursor.close()
        conn.close()
        print("\nBye!")
        
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
