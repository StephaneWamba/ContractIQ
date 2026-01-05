# Data Flow

Complete data flow diagrams for key operations.

---

## Document Processing Flow

### End-to-End Flow

```mermaid
graph TB
    A[User Uploads File] --> B[API: POST /documents/upload]
    B --> C[Save to Disk]
    C --> D[Create DB Record: status=uploaded]
    D --> E[Return Document ID]
    E --> F[Background Task Starts]
    F --> G[DocumentProcessor.process_pdf/docx]
    G --> H[Extract Text: PyMuPDF/python-docx]
    H --> I[LLM Structure Document]
    I --> J[Create Semantic Chunks]
    J --> K[Extract Coordinates]
    K --> L[VectorStore.index_document_chunks]
    L --> M[Generate Embeddings]
    M --> N[Store in ChromaDB]
    N --> O[Update DB: status=processed]
    O --> P[Invalidate Cache]
```

### Processing Details

| Step                | Component           | Output                            |
| ------------------- | ------------------- | --------------------------------- |
| **Text Extraction** | PyMuPDF/python-docx | Raw text + coordinates            |
| **Structuring**     | OpenAI GPT-4o-mini  | Sections, chunks, metadata        |
| **Chunking**        | DocumentProcessor   | Semantic chunks with page numbers |
| **Embedding**       | EmbeddingService    | Vector embeddings (1536 dim)      |
| **Indexing**        | VectorStore         | ChromaDB collection entries       |

---

## Clause Extraction Flow

```mermaid
graph TB
    A[User: Extract Clauses] --> B[API: POST /documents/{id}/extract-clauses]
    B --> C[Get Document from DB]
    C --> D[Get Chunks from Vector Store]
    D --> E[ClauseExtractor.extract_clauses_from_chunks]
    E --> F[Batch Processing: 5 chunks/batch]
    F --> G[LLM: Extract Clauses]
    G --> H[Risk Analysis]
    H --> I[ClauseDeduplicator: Remove Duplicates]
    I --> J[Save to Database]
    J --> K[Return Clauses]
```

### Extraction Process

1. **Retrieve Chunks**: Get all chunks for document from ChromaDB
2. **Batch Processing**: Process 5 chunks at a time (token limits)
3. **LLM Extraction**: Structured output with Instructor
4. **Risk Analysis**: Score (0-100), flags, reasoning
5. **Deduplication**: Remove similar clauses
6. **Storage**: Save to PostgreSQL

---

## RAG Query Flow

### Complete RAG Pipeline

```mermaid
graph TB
    A[User Question] --> B[API: POST /conversations/{id}/ask]
    B --> C[RAGPipeline.ask]
    C --> D[Retrieve Node]
    D --> E[EmbeddingService: Query Embedding]
    E --> F[VectorStore.search]
    F --> G[ChromaDB: Similarity Search]
    G --> H[Filter by Similarity Threshold]
    H --> I[Top 5 Chunks]
    I --> J[Generate Node]
    J --> K[Build Context from Chunks]
    K --> L[LLM: Generate Answer]
    L --> M[Extract Citations]
    M --> N[Save Message to DB]
    N --> O[Return Answer + Citations]
```

### Retrieval Details

| Step                 | Description                     | Output            |
| -------------------- | ------------------------------- | ----------------- |
| **Query Embedding**  | Generate embedding for question | 1536-dim vector   |
| **Vector Search**    | Cosine similarity search        | Ranked chunks     |
| **Filtering**        | Remove low-similarity (< -0.3)  | Top 5 chunks      |
| **Context Building** | Format chunks with metadata     | Formatted context |

### Generation Details

| Step                    | Description                  | Output             |
| ----------------------- | ---------------------------- | ------------------ |
| **Context Assembly**    | Combine chunks with metadata | Source list        |
| **Prompt Building**     | System + user prompts        | LLM prompts        |
| **Structured Output**   | Instructor validation        | Answer + citations |
| **Citation Validation** | Ensure valid source numbers  | Filtered citations |

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant DB as Database

    U->>F: Login (email, password)
    F->>A: POST /auth/login
    A->>DB: Verify credentials
    DB-->>A: User record
    A->>A: Generate JWT token
    A-->>F: Token + user data
    F->>F: Store token (localStorage)
    F->>A: Subsequent requests with token
    A->>A: Validate token
    A->>A: Extract user_id
    A-->>F: Authenticated response
```

---

## Workspace Isolation Flow

```mermaid
graph TB
    A[API Request] --> B[get_current_user]
    B --> C[Extract user_id from token]
    C --> D[Query with workspace filter]
    D --> E{Workspace belongs to user?}
    E -->|Yes| F[Process Request]
    E -->|No| G[403 Forbidden]
    F --> H[Filter by workspace_id]
    H --> I[Return Results]
```

### Isolation Points

1. **Database Queries**: Always filter by `workspace_id`
2. **Vector Store**: Per-workspace collections
3. **File Storage**: Workspace-scoped paths (optional)
4. **Cache Keys**: Include workspace_id

---

## Cache Flow

### Embedding Cache

```mermaid
graph LR
    A[Text Input] --> B[Hash Text]
    B --> C{Cache Hit?}
    C -->|Yes| D[Return Cached]
    C -->|No| E[OpenAI API]
    E --> F[Store in Cache: 7 days]
    F --> D
```

### Cache Strategy

| Cache Type          | Key Pattern                              | TTL      | Invalidation       |
| ------------------- | ---------------------------------------- | -------- | ------------------ |
| **Embeddings**      | `embedding:{model}:{hash}`               | 7 days   | Never (immutable)  |
| **Vector Search**   | `vector_search:{workspace}:{query_hash}` | 1 hour   | On document update |
| **Workspace Stats** | `workspace_stats:{workspace_id}`         | 1 minute | On any change      |

---

## Error Flow

```mermaid
graph TB
    A[Exception Raised] --> B{Exception Type?}
    B -->|ContractIQException| C[Custom Handler]
    B -->|ValidationError| D[Validation Handler]
    B -->|Other| E[General Handler]
    C --> F[Log Error]
    D --> F
    E --> F
    F --> G[Return Error Response]
    G --> H[Client Receives Error]
```

### Error Handling

- **Custom Exceptions**: Structured error codes
- **Validation Errors**: Field-level details
- **General Errors**: Error ID for tracking
- **Logging**: Context-rich logs with error IDs

---

## Next Steps

- **[Database Schema](database-schema.md)** - Entity relationships
- **[Vector Store](vector-store.md)** - Embedding architecture
