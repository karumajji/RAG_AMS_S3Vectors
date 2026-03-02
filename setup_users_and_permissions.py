#!/usr/bin/env python3
"""
Create test users in Cognito and permission records in Aurora
"""
import boto3
import pymysql
import json
import sys
import random

# AWS Configuration
COGNITO_USER_POOL_ID = 'us-east-2_FgJYtCR2r'
REGION = 'us-east-2'

# Database configuration
DB_HOST = 'ams-s3-demo-auroracluster-souvtks7ayal.cluster-ctjk2qgb238i.us-east-2.rds.amazonaws.com'
DB_USER = 'master'
DB_PASSWORD = 'Password1'
DB_NAME = 'rag_system'
DB_PORT = 3306

# Test users to create
TEST_USERS = [
    {
        "username": "alice@example.com",
        "email": "alice@example.com",
        "name": "Alice Smith",
        "password": "TempPass123!"
    },
    {
        "username": "bob@example.com",
        "email": "bob@example.com",
        "name": "Bob Johnson",
        "password": "TempPass123!"
    },
    {
        "username": "charlie@example.com",
        "email": "charlie@example.com",
        "name": "Charlie Brown",
        "password": "TempPass123!"
    }
]

def create_cognito_users():
    """Create test users in Cognito"""
    cognito_client = boto3.client('cognito-idp', region_name=REGION)
    
    print("\n" + "="*60)
    print("  Creating Cognito Users")
    print("="*60)
    
    created_users = []
    
    for user_data in TEST_USERS:
        username = user_data['username']
        email = user_data['email']
        name = user_data['name']
        password = user_data['password']
        
        try:
            # Create user
            response = cognito_client.admin_create_user(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'name', 'Value': name}
                ],
                TemporaryPassword=password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Get the user's sub (cognito_user_id)
            cognito_user_id = None
            for attr in response['User']['Attributes']:
                if attr['Name'] == 'sub':
                    cognito_user_id = attr['Value']
                    break
            
            # Set permanent password
            cognito_client.admin_set_user_password(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                Password=password,
                Permanent=True
            )
            
            print(f"✓ Created user: {username}")
            print(f"  Name: {name}")
            print(f"  Cognito User ID (sub): {cognito_user_id}")
            
            created_users.append({
                'username': username,
                'email': email,
                'name': name,
                'cognito_user_id': cognito_user_id,
                'password': password
            })
            
        except cognito_client.exceptions.UsernameExistsException:
            print(f"⊘ User already exists: {username}")
            
            # Get existing user's sub
            try:
                response = cognito_client.admin_get_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=username
                )
                
                cognito_user_id = None
                for attr in response['UserAttributes']:
                    if attr['Name'] == 'sub':
                        cognito_user_id = attr['Value']
                        break
                
                print(f"  Cognito User ID (sub): {cognito_user_id}")
                
                created_users.append({
                    'username': username,
                    'email': email,
                    'name': name,
                    'cognito_user_id': cognito_user_id,
                    'password': password
                })
            except Exception as e:
                print(f"  Error getting user info: {e}")
                
        except Exception as e:
            print(f"✗ Error creating user {username}: {e}")
    
    print(f"\n✓ Total users ready: {len(created_users)}")
    return created_users

def create_permissions(users):
    """Create permission records in Aurora database"""
    try:
        # Connect to database
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("  Creating Permission Records")
        print("="*60)
        
        # Get all document IDs
        cursor.execute("SELECT document_id FROM documents ORDER BY document_id")
        all_docs = [row[0] for row in cursor.fetchall()]
        print(f"\n✓ Found {len(all_docs)} documents in database")
        
        # Create varied permission patterns
        permission_patterns = {
            users[0]['cognito_user_id']: {
                'name': users[0]['name'],
                'docs': all_docs[:20]  # Alice: first 20 docs (tech + science)
            },
            users[1]['cognito_user_id']: {
                'name': users[1]['name'],
                'docs': all_docs[10:35]  # Bob: docs 11-35 (overlap with Alice, includes business)
            },
            users[2]['cognito_user_id']: {
                'name': users[2]['name'],
                'docs': all_docs[30:]  # Charlie: docs 31-50 (health + education)
            }
        }
        
        print("\nPermission distribution:")
        for user_id, pattern in permission_patterns.items():
            print(f"  {pattern['name']}: {len(pattern['docs'])} documents")
        
        print("\nInserting permissions...")
        print("-" * 60)
        
        inserted = 0
        skipped = 0
        
        for cognito_user_id, pattern in permission_patterns.items():
            user_name = pattern['name']
            
            for doc_id in pattern['docs']:
                try:
                    sql = """
                    INSERT INTO permissions (cognito_user_id, document_id, granted_at)
                    VALUES (%s, %s, NOW())
                    """
                    cursor.execute(sql, (cognito_user_id, doc_id))
                    inserted += 1
                    
                except pymysql.err.IntegrityError as e:
                    if 'Duplicate entry' in str(e):
                        skipped += 1
                    else:
                        raise
            
            print(f"✓ Created {len(pattern['docs'])} permissions for {user_name}")
        
        # Commit transaction
        conn.commit()
        
        print("-" * 60)
        print(f"\nPermission Summary:")
        print(f"  Inserted: {inserted}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {inserted + skipped}")
        
        # Verify permissions
        cursor.execute("SELECT COUNT(*) FROM permissions")
        count = cursor.fetchone()[0]
        print(f"\n✓ Total permissions in database: {count}")
        
        # Show permission breakdown
        print("\nPermission breakdown by user:")
        for user in users:
            cursor.execute(
                "SELECT COUNT(*) FROM permissions WHERE cognito_user_id = %s",
                (user['cognito_user_id'],)
            )
            count = cursor.fetchone()[0]
            print(f"  {user['name']}: {count} documents")
        
        cursor.close()
        conn.close()
        
        return inserted, skipped
        
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

def save_user_credentials(users):
    """Save user credentials to file for reference"""
    credentials = {
        'cognito_user_pool_id': COGNITO_USER_POOL_ID,
        'region': REGION,
        'users': users
    }
    
    with open('test_users.json', 'w', encoding='utf-8') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"\n✓ Saved user credentials to 'test_users.json'")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Setup Test Users and Permissions")
    print("="*60)
    
    # Create Cognito users
    users = create_cognito_users()
    
    if not users:
        print("\nError: No users were created")
        sys.exit(1)
    
    # Create permissions
    inserted, skipped = create_permissions(users)
    
    # Save credentials
    save_user_credentials(users)
    
    print("\n" + "="*60)
    print("  Setup Complete!")
    print("="*60)
    print("\nTest Users:")
    for user in users:
        print(f"\n  {user['name']} ({user['email']})")
        print(f"    Username: {user['username']}")
        print(f"    Password: {user['password']}")
        print(f"    Cognito User ID: {user['cognito_user_id']}")
    
    print("\n" + "="*60)
    print("\nTask 2 Complete! ✓")
    print("\nAll test data has been created:")
    print("  ✓ 50 documents with embeddings")
    print("  ✓ Embeddings uploaded to S3")
    print("  ✓ Document metadata in Aurora database")
    print("  ✓ 3 test users in Cognito")
    print("  ✓ Permission records with varied access patterns")

if __name__ == "__main__":
    main()
