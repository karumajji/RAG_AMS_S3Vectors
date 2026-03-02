# Requirements Document: AWS Permissions-Based RAG System

## Introduction

This document specifies the requirements for a secure document retrieval system that combines permissions-based access control with Retrieval-Augmented Generation (RAG) search capabilities. The system uses Amazon Aurora MySQL for permissions management and Amazon S3 for storing document vectors, ensuring that users can only access and search documents they have explicit permissions for.

## Glossary

- **System**: The AWS Permissions-Based RAG System
- **Aurora_DB**: Amazon Aurora MySQL database instance
- **Vector_Store**: Amazon S3 storage containing document embeddings
- **Cognito**: AWS Cognito service for user authentication and authorization
- **User**: An authenticated entity requesting document access
- **Document**: A text-based resource with associated vector embeddings
- **Permission**: An access control rule linking a User to a Document
- **RAG_Engine**: The retrieval-augmented generation search component
- **Vector_Embedding**: A numerical representation of document content for semantic search
- **Access_Filter**: Component that filters search results based on permissions
- **Orchestration_Agent**: AgentCore-based agent that coordinates retrieval operations
- **AgentCore**: The framework used to build the orchestration agent

## Requirements

### Requirement 1: User Authentication and Authorization

**User Story:** As a system administrator, I want to manage user identities and their document access permissions, so that I can control who can access which documents.

#### Acceptance Criteria

1. WHEN a User attempts to access the System, THE Cognito SHALL authenticate the User's identity
2. WHEN a User is authenticated, THE Cognito SHALL issue a JWT token containing the User's identity claims
3. WHEN a JWT token is received, THE System SHALL validate the token signature and expiration
4. WHEN a User is authenticated, THE Aurora_DB SHALL retrieve all Permission records associated with that User's Cognito user ID
5. THE Aurora_DB SHALL maintain Permission records linking Cognito user IDs to Document IDs with access levels
6. WHEN a Permission is created or modified, THE Aurora_DB SHALL validate that the Document exists

### Requirement 2: Document Storage and Vector Management

**User Story:** As a content manager, I want to store documents and their vector embeddings, so that they can be searched semantically while maintaining access control.

#### Acceptance Criteria

1. WHEN a Document is added to the System, THE System SHALL generate a Vector_Embedding for that Document using sentence-transformers/all-mpnet-base-v2 model
2. WHEN a Vector_Embedding is generated, THE System SHALL store it in the Vector_Store with a unique identifier in binary format (float32 little-endian)
3. THE Aurora_DB SHALL store Document metadata including document ID, title, storage location, and creation timestamp
4. WHEN a Document is stored, THE System SHALL create a reference linking the Document record in Aurora_DB to its Vector_Embedding in Vector_Store
5. THE System SHALL support Document content in text format with UTF-8 encoding
6. THE System SHALL support test data generation with at least 50 fake documents for development and testing purposes

### Requirement 3: Permission-Based Search

**User Story:** As a user, I want to search for documents using natural language queries, so that I can find relevant information from documents I have permission to access.

#### Acceptance Criteria

1. WHEN a User submits a search query, THE RAG_Engine SHALL convert the query into a Vector_Embedding
2. WHEN performing vector similarity search, THE RAG_Engine SHALL retrieve candidate Documents from the Vector_Store
3. WHEN candidate Documents are retrieved, THE Access_Filter SHALL remove Documents that the User does not have Permission to access
4. THE System SHALL return only Documents where the User has an active Permission record in Aurora_DB
5. WHEN search results are returned, THE System SHALL include Document metadata and relevance scores

### Requirement 4: Vector Similarity Search

**User Story:** As a user, I want the system to find semantically similar documents using fast approximate nearest neighbor search, so that I can discover relevant content even when exact keyword matches don't exist.

#### Acceptance Criteria

1. WHEN comparing vectors, THE RAG_Engine SHALL use HNSW (Hierarchical Navigable Small World) algorithm for approximate nearest neighbor search
2. THE RAG_Engine SHALL rank Documents by similarity score in descending order
3. WHEN multiple Documents have similar scores, THE System SHALL maintain consistent ordering based on Document ID
4. THE System SHALL support configurable similarity thresholds for filtering results
5. THE RAG_Engine SHALL return the top N most similar Documents where N is specified by the query parameters
6. THE HNSW index SHALL achieve >95% recall rate for approximate nearest neighbors

### Requirement 5: Access Control Enforcement

**User Story:** As a security officer, I want all document access to be validated against permissions, so that unauthorized users cannot access restricted documents.

#### Acceptance Criteria

1. WHEN a User requests a Document, THE System SHALL verify an active Permission exists in Aurora_DB before granting access
2. IF no Permission exists for a User-Document pair, THEN THE System SHALL deny access and return an authorization error
3. THE Access_Filter SHALL execute permission checks before returning any Document content or metadata
4. WHEN a Permission is revoked, THE System SHALL immediately prevent access to the associated Document
5. THE System SHALL log all access attempts including User ID, Document ID, timestamp, and access decision

### Requirement 6: Database Schema and Integrity

**User Story:** As a database administrator, I want a well-structured schema with referential integrity, so that the permissions data remains consistent and reliable.

#### Acceptance Criteria

1. THE Aurora_DB SHALL maintain a Documents table with primary key on document_id
2. THE Aurora_DB SHALL maintain a Permissions table with cognito_user_id and document_id as foreign key references
3. THE Aurora_DB SHALL store cognito_user_id as a string field in the Permissions table
4. WHEN a Document is deleted, THE Aurora_DB SHALL handle cascading deletes or prevent deletion if Permissions exist
5. THE Aurora_DB SHALL enforce unique constraints on the combination of cognito_user_id and document_id in the Permissions table

### Requirement 7: S3 Vector Storage Operations

**User Story:** As a system operator, I want reliable storage and retrieval of vector embeddings, so that search functionality remains performant and available.

#### Acceptance Criteria

1. WHEN storing a Vector_Embedding, THE System SHALL write it to Vector_Store using the document_id as the object key
2. WHEN retrieving vectors, THE System SHALL read Vector_Embeddings from Vector_Store using document_id references
3. THE System SHALL store Vector_Embeddings in a binary format optimized for similarity computations
4. WHEN a Document is deleted, THE System SHALL remove the corresponding Vector_Embedding from Vector_Store
5. THE System SHALL handle S3 access errors gracefully and return appropriate error messages

### Requirement 8: Query Processing Pipeline

**User Story:** As a developer, I want a clear query processing pipeline, so that I can understand and maintain the search workflow.

#### Acceptance Criteria

1. WHEN a search query is received, THE System SHALL execute the following steps in order: authentication, query embedding, vector search, permission filtering, result ranking
2. THE System SHALL validate query parameters before processing
3. IF any pipeline stage fails, THEN THE System SHALL return an error and halt processing
4. THE System SHALL complete query processing within 5 seconds for queries returning up to 100 results
5. THE System SHALL support pagination for large result sets

### Requirement 9: AgentCore Orchestration

**User Story:** As a system architect, I want an intelligent agent to orchestrate retrieval operations using AWS MCP Server, so that the system can handle complex queries and coordinate multiple AWS services efficiently.

#### Acceptance Criteria

1. THE Orchestration_Agent SHALL be built using the AgentCore framework
2. WHEN a search request is received, THE Orchestration_Agent SHALL coordinate the query processing pipeline
3. THE Orchestration_Agent SHALL use AWS MCP Server to interact with Cognito, Aurora_DB, and Vector_Store
4. WHEN permission checks are required, THE Orchestration_Agent SHALL query Aurora_DB via AWS MCP Server with the authenticated User's Cognito user ID
5. WHEN vector search is required, THE Orchestration_Agent SHALL invoke the RAG_Engine with the query embedding
6. THE Orchestration_Agent SHALL aggregate results from multiple sources and apply permission filtering
7. WHEN errors occur in any component, THE Orchestration_Agent SHALL handle the error gracefully and return appropriate responses
8. THE Orchestration_Agent SHALL maintain state for multi-step retrieval operations
9. THE Orchestration_Agent SHALL have read-only access to AWS resources (no write operations permitted)

### Requirement 10: Permission Types and Granularity

**User Story:** As a system administrator, I want to define read permissions for document access, so that I can control who can view which documents.

#### Acceptance Criteria

1. THE Aurora_DB SHALL store permission records linking users to documents
2. THE System SHALL support "read" permission type for document access
3. WHEN checking permissions, THE System SHALL verify the User has read permission for the requested document
4. THE Aurora_DB SHALL enforce unique constraints on (cognito_user_id, document_id) pairs
5. THE Orchestration_Agent SHALL have read-only database access and cannot create, modify, or delete permissions

### Requirement 11: Error Handling and Logging

**User Story:** As a system operator, I want comprehensive error handling and logging, so that I can troubleshoot issues and monitor system health.

#### Acceptance Criteria

1. WHEN an authentication failure occurs, THE System SHALL log the failed attempt with Cognito user identifier and timestamp
2. WHEN a permission check fails, THE System SHALL return a 403 Forbidden error with a descriptive message
3. IF the Aurora_DB is unavailable, THEN THE System SHALL return a 503 Service Unavailable error
4. IF the Vector_Store is unavailable, THEN THE System SHALL return a 503 Service Unavailable error
5. THE System SHALL log all database queries that take longer than 1 second for performance monitoring
6. WHEN the Orchestration_Agent encounters an error, THE System SHALL log the error with full context including request ID and component name

### Requirement 12: Infrastructure Automation

**User Story:** As a DevOps engineer, I want to automate AWS infrastructure provisioning, so that I can quickly set up and tear down environments for development and testing.

#### Acceptance Criteria

1. THE System SHALL provide automation scripts to create AWS infrastructure resources (Aurora/RDS, S3, Cognito, IAM roles)
2. THE automation scripts SHALL use AWS CLI commands or AWS MCP Server to provision resources
3. WHEN infrastructure is provisioned, THE scripts SHALL configure database credentials (username: master, password: Password1)
4. THE scripts SHALL create and configure IAM roles with appropriate read-only permissions for the agent
5. THE scripts SHALL execute SQL schema creation for documents and permissions tables
6. THE automation SHALL be idempotent and handle existing resources gracefully
