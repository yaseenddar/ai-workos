# AI WorkOS

AI WorkOS is a multi-tenant enterprise knowledge base and automation backend built with FastAPI, Qdrant, PostgreSQL, MinIO, and Google Gemini. It enables organizations to upload private documents, index vector embeddings, manage team access permissions, and execute retrieval-augmented generation (RAG) queries with contextual isolation per organization.

---

## Key Features

- **Multi-Tenancy & RBAC**: Organization-level isolation, user authentication (JWT), invitation system, and role-based access control.
- **Document Processing**: PDF parsing, token-aware document chunking, and secure object storage via MinIO.
- **Vector Search & RAG**: Dense vector indexing with Qdrant, embedding generation using SentenceTransformers, reranking pipeline, and answer generation via Google Gemini.
- **Production Infrastructure**: Asynchronous FastAPI service architecture backed by PostgreSQL, Redis, and Alembic database migrations.

---

## Architecture Overview

```
                      +--------------------+
                      | Client Application |
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      |    FastAPI API     |
                      +----+----+----+-----+
                           |    |    |
           +---------------+    |    +---------------+
           |                    |                    |
           v                    v                    v
  +------------------+ +------------------+ +------------------+
  |    PostgreSQL    | |      Redis       | |  MinIO (Storage) |
  | (Users/Orgs/Meta)| |  (Cache/Queue)  | | (Raw Documents) |
  +------------------+ +------------------+ +------------------+
                                |
                                v
                      +--------------------+
                      |   Vector Engine    |
                      | (Qdrant Vector DB) |
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      |    LLM Gateway     |
                      |  (Google Gemini)   |
                      +--------------------+
```

---

## Tech Stack

- **Backend Framework**: Python 3.12, FastAPI, Uvicorn
- **Database & Storage**: PostgreSQL 17, SQLAlchemy, Alembic, MinIO S3
- **Vector DB & AI Engine**: Qdrant, SentenceTransformers, Tiktoken, Google Gemini API
- **Caching & Async**: Redis
- **Containerization**: Docker, Docker Compose

---

## Getting Started

### Prerequisites

Make sure you have the following installed on your machine:
- Python 3.12+
- Docker & Docker Compose
- `pip` or your preferred Python environment manager

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-workos.git
cd ai-workos
```

### 2. Configure Environment Variables

Copy the sample environment file and update variables as needed (specifically `GEMINI_API_KEY`):

```bash
cp .env.example .env
```

### 3. Start Infrastructure Services

Spin up PostgreSQL, MinIO, Redis, and Qdrant containers:

```bash
docker-compose up -d
```

Verify that all containers are running properly:

```bash
docker-compose ps
```

### 4. Install Dependencies

Create a virtual environment and install backend packages:

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Run Database Migrations

Apply Alembic migrations to set up the relational schema:

```bash
cd backend
alembic upgrade head
```

### 6. Start the Backend API

Launch the FastAPI application:

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`. You can test endpoints interactively via the OpenAPI Swagger docs at `http://localhost:8000/docs`.

---

## Environment Variables

| Variable | Description | Default / Example |
|---|---|---|
| `APP_NAME` | Name of the application | `AI WorkOS` |
| `ENVIRONMENT` | Runtime mode (`development` / `production`) | `development` |
| `DATABASE_URL` | PostgreSQL database connection string | `postgresql://postgres:yaseen@localhost:5432/ai_workos` |
| `REDIS_URL` | Redis instance URL | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `your_jwt_secret_key` |
| `MINIO_ENDPOINT` | MinIO server URL | `localhost:9000` |
| `QDRANT_URL` | Qdrant vector database URL | `http://localhost:6333` |
| `EMBEDDING_MODEL` | HuggingFace model for embeddings | `all-MiniLM-L6-v2` |
| `GEMINI_API_KEY` | API key for Google Gemini | `your_gemini_api_key` |
| `GEMINI_MODEL` | Gemini LLM model identifier | `gemini-1.5-flash` |

---

## Core API Endpoints

### Authentication & Tenant Management
- `POST /api/v1/auth/register` - Register a new user and organization.
- `POST /api/v1/auth/login` - Authenticate and obtain JWT access token.
- `GET /api/v1/organization` - Fetch current organization context.
- `POST /api/v1/invitations` - Send membership invitations to users.

### Document Management & RAG
- `POST /api/v1/documents/upload` - Upload PDF documents to MinIO & trigger chunking/embedding indexing.
- `POST /api/v1/rag/query` - Perform context-grounded RAG query over organization documents using Gemini LLM.

---

## Repository Structure

```
ai-workos/
├── backend/
│   ├── app/
│   │   ├── ai/            # Parser, token counter, and chunker modules
│   │   ├── api/           # Router & v1 endpoint controllers
│   │   ├── core/          # App config, JWT token, security utilities
│   │   ├── db/            # Database sessions, models & Alembic migrations
│   │   ├── embeddings/    # Embedding generation services
│   │   ├── llm/           # Gemini LLM provider integration
│   │   └── rag/           # Retrieval, context builder, and RAG service
│   ├── alembic.ini        # Alembic migration configuration
│   └── Dockerfile
├── docker-compose.yml     # Local infrastructure services
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## License

This project is licensed under the MIT License.
