-- Initialize Database Schema for RAG System
-- Run this script after the CloudFormation stack is deployed

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    s3_vector_key VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    permission_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cognito_user_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
    UNIQUE KEY (cognito_user_id, document_id),
    INDEX (cognito_user_id)
);

-- Verify tables were created
SHOW TABLES;
