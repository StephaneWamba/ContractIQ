# Project Structure

Codebase organization and key directories.

---

## Directory Structure

```
ContractIQ/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/                # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── workspaces.py
│   │   │   ├── documents.py
│   │   │   ├── clauses.py
│   │   │   ├── conversations.py
│   │   │   └── exports.py
│   │   ├── core/               # Core configuration
│   │   │   ├── config.py       # Settings
│   │   │   ├── database.py     # DB connection
│   │   │   ├── auth.py         # JWT auth
│   │   │   ├── cache.py        # Redis cache
│   │   │   ├── exceptions.py  # Custom exceptions
│   │   │   └── logging_config.py
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── document.py
│   │   │   ├── clause.py
│   │   │   └── conversation.py
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── workspace.py
│   │   │   ├── document.py
│   │   │   ├── clause.py
│   │   │   ├── conversation.py
│   │   │   └── errors.py
│   │   ├── services/           # Business logic
│   │   │   ├── document_processor.py
│   │   │   ├── clause_extractor.py
│   │   │   ├── rag_pipeline.py
│   │   │   ├── vector_store.py
│   │   │   ├── embedding_service.py
│   │   │   ├── clause_deduplicator.py
│   │   │   ├── evidence_pack_generator.py
│   │   │   └── export_service.py
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   │   └── versions/
│   ├── uploads/               # Uploaded files
│   ├── chroma_db/             # ChromaDB data
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                   # Next.js frontend
│   ├── app/                    # App Router
│   │   ├── page.tsx           # Home
│   │   ├── documents/
│   │   ├── clauses/
│   │   ├── qa/
│   │   ├── settings/
│   │   └── login/
│   ├── components/            # React components
│   │   ├── ui/                # shadcn/ui
│   │   ├── layout/
│   │   ├── documents/
│   │   ├── clauses/
│   │   ├── qa/
│   │   └── workspace/
│   ├── contexts/              # React contexts
│   │   └── auth-context.tsx
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   └── utils.ts
│   ├── public/                # Static assets
│   ├── package.json
│   └── next.config.ts
├── docs/                       # Documentation
│   ├── user-guide/
│   ├── architecture/
│   ├── api/
│   └── development/
├── docker-compose.yml
└── README.md
```

---

## Backend Structure

### API Layer (`src/api/`)

- **Purpose**: HTTP request handlers
- **Pattern**: One router per resource
- **Dependencies**: Auth, database session

### Core Layer (`src/core/`)

- **config.py**: Application settings (Pydantic Settings)
- **database.py**: SQLAlchemy engine and session
- **auth.py**: JWT token creation/validation
- **cache.py**: Redis caching service
- **exceptions.py**: Custom exception classes

### Models (`src/models/`)

- **Purpose**: SQLAlchemy ORM models
- **Pattern**: One model per table
- **Relationships**: Defined with `relationship()`

### Schemas (`src/schemas/`)

- **Purpose**: Pydantic models for request/response validation
- **Request**: Input validation
- **Response**: Output serialization

### Services (`src/services/`)

- **Purpose**: Business logic, external API calls
- **Pattern**: Stateless service classes
- **Dependencies**: Core config, external APIs

---

## Frontend Structure

### App Router (`app/`)

- **Purpose**: Next.js 13+ App Router pages
- **Pattern**: One directory per route
- **Layout**: Shared layout in `layout.tsx`

### Components (`components/`)

- **ui/**: Reusable UI components (shadcn/ui)
- **layout/**: Layout components (sidebar, nav)
- **documents/**: Document-specific components
- **clauses/**: Clause-specific components
- **qa/**: Q&A components

### Contexts (`contexts/`)

- **auth-context.tsx**: Global authentication state

### Lib (`lib/`)

- **api.ts**: Centralized API client
- **utils.ts**: Utility functions

---

## Key Files

### Backend

| File | Purpose |
|------|---------|
| `src/main.py` | FastAPI application entry point |
| `src/core/config.py` | Application configuration |
| `src/core/database.py` | Database connection |
| `pyproject.toml` | Python dependencies |

### Frontend

| File | Purpose |
|------|---------|
| `app/layout.tsx` | Root layout |
| `lib/api.ts` | API client |
| `contexts/auth-context.tsx` | Auth state management |
| `package.json` | Node dependencies |

---

## Naming Conventions

### Backend

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`

### Frontend

- **Files**: `kebab-case.tsx` or `camelCase.tsx`
- **Components**: `PascalCase`
- **Functions**: `camelCase()`
- **Constants**: `UPPER_SNAKE_CASE`

---

## Import Organization

### Backend

```python
# Standard library
from typing import List, Optional
from uuid import UUID

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local
from src.core.database import get_db
from src.models.user import User
```

### Frontend

```typescript
// React
import { useState, useEffect } from 'react';

// Next.js
import { useRouter } from 'next/navigation';

// Components
import { Button } from '@/components/ui/button';

// Lib
import { api } from '@/lib/api';
```

---

## Next Steps

- **[Contributing](contributing.md)** - Contribution guidelines
- **[Testing](testing.md)** - Testing guide

