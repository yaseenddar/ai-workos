# System Workflows & Architecture

This document details the core end-to-end workflows of **AI WorkOS**, explaining how data flows between system components, how multi-tenant isolation is enforced, and how asynchronous tasks are processed.

---

## Table of Contents

1. [Tenant Onboarding & Authentication Workflow](#1-tenant-onboarding--authentication-workflow)
2. [Document Ingestion & Indexing Pipeline](#2-document-ingestion--indexing-pipeline)
3. [Retrieval-Augmented Generation (RAG) Workflow](#3-retrieval-augmented-generation-rag-workflow)
4. [Member Invitations & Role-Based Access Control](#4-member-invitations--role-based-access-control)

---

## 1. Tenant Onboarding & Authentication Workflow

AI WorkOS uses an organization-centric multi-tenant model. Every user belongs to one or more organizations with defined roles (`OWNER`, `ADMIN`, `MEMBER`).

### Sequence Flow

```
[ Client ]                [ API Router ]             [ Auth Service ]            [ PostgreSQL ]
    |                           |                           |                          |
    |--- POST /auth/register -->|                           |                          |
    |    (email, pass, org_name)|                           |                          |
    |                           |--- register_user(...) --->|                          |
    |                           |                           |--- Create User --------->|
    |                           |                           |--- Create Org ----------->|
    |                           |                           |--- Create Membership --->|
    |                           |<-- (user, org tuple) -----|    (Role: OWNER)         |
    |<-- 201 Created (IDs) -----|                           |                          |
    |                           |                           |                          |
    |--- POST /auth/login ----->|                           |                          |
    |    (email, password)      |                           |                          |
    |                           |--- login_user(...) ------>|                          |
    |                           |                           |--- Verify password ----->|
    |                           |<-- JWT Access/Refresh ----|                          |
    |<-- 200 OK (Tokens) -------|                           |                          |
```

### Step Details

1. **User Registration**:
   - Accepts user credentials and an initial organization name.
   - Hashes the password using Argon2 (`app.core.security.hash_password`).
   - Inserts records into `users` and `organizations` tables within a single database transaction.
   - Automatically assigns the registering user as the `OWNER` of the organization in the `memberships` join table.

2. **Authentication & Token Generation**:
   - Validates user credentials against PostgreSQL.
   - Signs JWT tokens (access token and refresh token) carrying `user_id` in the claim payload.

3. **Tenant Scoping on Subsequent Requests**:
   - Protected API requests include the JWT in the `Authorization: Bearer <token>` header.
   - FastAPI dependencies (`get_current_user`, `require_member`) parse the JWT, identify the requesting user, check organization membership, and attach the organization context to the request.

---

## 2. Document Ingestion & Indexing Pipeline

Document processing runs asynchronously via Celery workers to keep file upload endpoints fast and responsive.

### Architecture Flow

```
[ User ] -> [ API /upload ] -> [ MinIO Storage ] (PDF File Saved)
                                   |
                                   v
                             [ PostgreSQL ] (Status: UPLOADED)
                                   |
                                   v (Celery Task Triggered: documents.process)
                             [ Celery Worker ]
                                   |
                                   +--> Parse PDF (PyMuPDF)
                                   |
                                   +--> Text Chunking (Token-aware splitter)
                                   |
                                   +--> DB Persistence (document_chunks table)
                                   |
                                   +--> Embeddings (SentenceTransformers)
                                   |
                                   +--> Vector Indexing (Qdrant with org_id metadata)
                                   |
                                   v
                             [ PostgreSQL ] (Status: PROCESSED)
```

### Ingestion Steps

1. **File Upload & Validation**:
   - The `/documents/upload` endpoint validates file format (PDF) and size.
   - Uploads the raw binary file to MinIO under the object path `{organization_id}/documents/{document_uuid}.pdf`.
   - Creates a `Document` record in PostgreSQL with `status = UPLOADED`.

2. **Background Task Scheduling**:
   - Calls `process_document.delay(document_id)` to push a processing job onto the Redis Celery queue.

3. **Parsing & Chunking**:
   - Celery worker downloads the raw PDF from MinIO storage.
   - `PDFParser` extracts clean text content page-by-page using PyMuPDF.
   - `TextChunker` splits pages into semantic chunks based on token limits (measured via `tiktoken` / sentence transformer tokenizers).

4. **Persistence & Idempotency Check**:
   - Checks if chunks already exist for the document ID in PostgreSQL to ensure worker idempotency upon retries.
   - Saves `DocumentChunk` records containing page number, chunk index, text content, and token count.

5. **Embedding & Vector Storage**:
   - Computes dense vector embeddings for each chunk using `SentenceTransformerProvider` (`all-MiniLM-L6-v2`).
   - Indexes vectors into Qdrant containing payload metadata: `organization_id`, `document_id`, `chunk_id`, and page index.
   - Updates document status in PostgreSQL to `PROCESSED`.

---

## 3. Retrieval-Augmented Generation (RAG) Workflow

The RAG workflow answers natural language questions using documents indexed specifically under the user's active organization.

### Sequence Diagram

```
[ User Query ] 
      |
      v
[ POST /api/v1/rag/query ]
      |
      +---> 1. Authenticate JWT & extract organization_id
      |
      +---> 2. Generate embedding vector for query string
      |
      +---> 3. Query Qdrant (Filter: organization_id == request.org_id)
      |
      +---> 4. Apply Reranker (Cross-Encoder score optimization)
      |
      +---> 5. Build Context Window (Assemble top-K passages with metadata)
      |
      +---> 6. Format RAG Prompt & execute LLM generation (Google Gemini)
      |
      v
[ JSON Response: Answer + Attributed Sources (Doc ID, Page, Score) ]
```

### Detailed Pipeline Stages

1. **Organization Context Verification**:
   - The `require_member` FastAPI dependency ensures the user belongs to the target organization before querying any vector data.

2. **Multi-Tenant Vector Search**:
   - `RetrievalService` generates an embedding vector for the question text.
   - Queries Qdrant with a strict payload payload filter: `Filter(must=[FieldCondition(key="organization_id", match=MatchValue(value=org_id))])`.
   - Ensures zero cross-tenant data leakage.

3. **Candidate Reranking**:
   - Retrieved vector matches are passed to the reranking provider (Cross-Encoder model).
   - Reranks candidate passages based on semantic relevance to the query, discarding low-confidence results.

4. **Context Window Assembly**:
   - `ContextBuilder` aggregates top-ranked chunks into a structured prompt context block while enforcing maximum token constraints.

5. **LLM Generation & Source Attribution**:
   - RAG prompt template injects context and question into Google Gemini (`gemini-1.5-flash`).
   - Formats the response with structured citation details (document filename, page number, retrieval score).

---

## 4. Member Invitations & Role-Based Access Control

Organizations can invite team members and assign fine-grained permissions.

### Workflow

1. **Invitation Dispatch**:
   - An `OWNER` or `ADMIN` sends an invitation request (`POST /api/v1/invitations`).
   - System generates a secure invitation token associated with the target email and organization role.

2. **Acceptance & Joining**:
   - Invited user accepts via token URL.
   - System verifies token validity, checks expiration, creates a `Membership` record linking the user to the organization, and updates the invitation state.

3. **Permission Enforcement**:
   - API routes use granular authorization dependencies (`app.api.permissions`) to verify whether the requesting user's membership role satisfies the required action scope (e.g. document upload vs. document deletion vs. organization configuration).
