# System Design

Detailed design of backend and frontend components.

---

## Backend Architecture

### API Layer Structure

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN[main.py]
        MIDDLEWARE[CORS, Auth, Error Handlers]
    end

    subgraph "API Routers"
        AUTH_ROUTER[auth.py]
        WORKSPACE_ROUTER[workspaces.py]
        DOC_ROUTER[documents.py]
        CLAUSE_ROUTER[clauses.py]
        CONV_ROUTER[conversations.py]
        EXPORT_ROUTER[exports.py]
    end

    subgraph "Dependencies"
        AUTH_DEP[get_current_user]
        DB_DEP[get_db]
    end

    MAIN --> MIDDLEWARE
    MAIN --> AUTH_ROUTER
    MAIN --> WORKSPACE_ROUTER
    MAIN --> DOC_ROUTER
    MAIN --> CLAUSE_ROUTER
    MAIN --> CONV_ROUTER
    MAIN --> EXPORT_ROUTER

    AUTH_ROUTER --> AUTH_DEP
    WORKSPACE_ROUTER --> AUTH_DEP
    WORKSPACE_ROUTER --> DB_DEP
    DOC_ROUTER --> AUTH_DEP
    DOC_ROUTER --> DB_DEP
```

### Service Layer

| Service               | Purpose                               | Key Methods                                 |
| --------------------- | ------------------------------------- | ------------------------------------------- |
| **DocumentProcessor** | Parse PDF/DOCX, structure with LLM    | `process_pdf()`, `process_docx()`           |
| **ClauseExtractor**   | Extract clauses with risk analysis    | `extract_clauses_from_chunks()`             |
| **RAGPipeline**       | Semantic search and answer generation | `ask()`                                     |
| **VectorStore**       | Embedding storage and search          | `index_document_chunks()`, `search()`       |
| **EmbeddingService**  | Generate embeddings with caching      | `get_embedding()`, `get_embeddings_batch()` |

### Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Router
    participant D as Dependency
    participant S as Service
    participant DB as Database

    C->>M: HTTP Request
    M->>M: CORS check
    M->>M: Auth validation
    M->>R: Route to handler
    R->>D: get_current_user()
    D->>DB: Verify token
    D-->>R: User object
    R->>D: get_db()
    D-->>R: DB session
    R->>S: Call service method
    S->>DB: Query/update data
    S-->>R: Result
    R-->>C: JSON response
```

---

## Frontend Architecture

### Component Structure

```mermaid
graph TB
    subgraph "Pages (App Router)"
        HOME[page.tsx]
        DOCS[documents/page.tsx]
        CLAUSES[clauses/page.tsx]
        QA[qa/page.tsx]
    end

    subgraph "Components"
        LAYOUT[layout/]
        DOC_COMP[documents/]
        CLAUSE_COMP[clauses/]
        QA_COMP[qa/]
        UI[ui/]
    end

    subgraph "Contexts"
        AUTH_CTX[auth-context.tsx]
    end

    subgraph "Lib"
        API[api.ts]
    end

    HOME --> LAYOUT
    DOCS --> DOC_COMP
    CLAUSES --> CLAUSE_COMP
    QA --> QA_COMP

    DOC_COMP --> API
    CLAUSE_COMP --> API
    QA_COMP --> API

    LAYOUT --> AUTH_CTX
    AUTH_CTX --> API
```

### State Management

- **Auth Context**: Global authentication state
- **Local State**: React hooks for component state
- **API Client**: Centralized API calls with token management

### Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as Component
    participant CTX as Context
    participant API as API Client
    participant B as Backend

    U->>C: User action
    C->>CTX: Check auth
    CTX-->>C: Auth status
    C->>API: API call
    API->>API: Add token
    API->>B: HTTP request
    B-->>API: Response
    API-->>C: Data
    C->>C: Update state
    C-->>U: Render update
```

---

## Service Design Patterns

### 1. **Dependency Injection**

- FastAPI dependencies for database sessions
- Service instances created at module level
- Easy testing with mock dependencies

### 2. **Background Tasks**

- FastAPI `BackgroundTasks` for async processing
- Non-blocking document processing
- Status polling from frontend

### 3. **Caching Strategy**

- Multi-level caching (Redis + in-memory)
- TTL-based expiration
- Cache invalidation on updates

### 4. **Error Handling**

- Custom exception hierarchy
- Structured error responses
- Logging with context

---

## Database Design

### Connection Management

```python
# Connection pooling
engine = create_engine(
    database_url,
    pool_pre_ping=True,      # Verify connections
    pool_size=10,            # Base pool size
    max_overflow=20             # Additional connections
)
```

### Session Lifecycle

```mermaid
graph LR
    A[Request] --> B[get_db dependency]
    B --> C[Create session]
    C --> D[Use session]
    D --> E[Commit/rollback]
    E --> F[Close session]
```

---

## Vector Store Design

### Collection Structure

- **Naming**: `workspace_{workspace_id}`
- **Metadata**: `document_id`, `page_number`, `section_name`, `chunk_id`
- **Isolation**: Per-workspace collections

### Embedding Pipeline

```mermaid
graph LR
    A[Text Chunk] --> B{Check Cache}
    B -->|Hit| C[Return Cached]
    B -->|Miss| D[OpenAI API]
    D --> E[Store in Cache]
    E --> F[Return Embedding]
    C --> F
```

---

## API Design Patterns

### RESTful Endpoints

| Pattern | Example            | Method |
| ------- | ------------------ | ------ |
| List    | `/workspaces/`     | GET    |
| Get     | `/workspaces/{id}` | GET    |
| Create  | `/workspaces/`     | POST   |
| Update  | `/workspaces/{id}` | PATCH  |
| Delete  | `/workspaces/{id}` | DELETE |

### Response Format

```json
{
  "id": "uuid",
  "name": "string",
  "created_at": "iso8601",
  ...
}
```

### Error Format

```json
{
  "error": true,
  "error_code": "NOT_FOUND",
  "message": "User-friendly message",
  "details": {},
  "timestamp": "iso8601"
}
```

---

## Next Steps

- **[Data Flow](data-flow.md)** - Complete data flow diagrams
- **[Database Schema](database-schema.md)** - Entity relationships
- **[Vector Store](vector-store.md)** - Embedding architecture
