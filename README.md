# ContractIQ

Document Intelligence & RAG Platform for Contract Review

A unified platform that combines contract clause extraction with semantic search across multiple documents. Users can review contracts, extract key clauses, identify risks, and ask questions across document sets with citations and evidence packs.

## Features

- **Contract Review & Clause Extraction**: Extract 10-15 common clause types (Termination, Liability, IP, Payment, etc.)
- **Multi-Document Q&A**: Ask questions across multiple documents with citations
- **Evidence Packs**: Generate PDF bundles with highlighted excerpts
- **Workspace Isolation**: Separate document sets per workspace

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL
- PyMuPDF + Unstructured.io (document processing)
- LangGraph (RAG pipeline)
- ChromaDB (vector store)
- spaCy (clause extraction)

### Infrastructure
- Docker & Docker Compose
- uv (package management)

## Setup

See [backend/README.md](backend/README.md) for detailed setup instructions.

Quick start:
```bash
cd backend
docker-compose up -d
```

## Project Structure

```
ContractIQ/
├── backend/          # FastAPI backend
├── private/          # Private documentation (gitignored)
└── README.md
```

## License

Private repository

