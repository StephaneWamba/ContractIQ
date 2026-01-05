# Documents API

Document upload, processing, and management endpoints.

---

## Upload Document

Upload a document for processing.

**Endpoint**: `POST /api/v1/documents/upload`

**Headers**: `Authorization: Bearer <token>`

**Request**: `multipart/form-data`
- `file`: PDF or DOCX file (max 50MB)
- `workspace_id`: UUID of workspace

**Response** (201):
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "name": "contract.pdf",
  "original_filename": "contract.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "page_count": null,
  "file_size": 1024000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Processing**: Document processing runs in background. Status updates automatically.

**Errors**:
- `400`: Invalid file type or size
- `404`: Workspace not found

---

## List Documents

List documents, optionally filtered by workspace.

**Endpoint**: `GET /api/v1/documents/?workspace_id={id}`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `workspace_id` (optional): Filter by workspace

**Response** (200):
```json
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "name": "contract.pdf",
    "original_filename": "contract.pdf",
    "file_type": "pdf",
    "status": "processed",
    "page_count": 25,
    "file_size": 1024000,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

## Get Document

Get document details.

**Endpoint**: `GET /api/v1/documents/{document_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "name": "contract.pdf",
  "original_filename": "contract.pdf",
  "file_type": "pdf",
  "status": "processed",
  "page_count": 25,
  "file_size": 1024000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors**:
- `404`: Document not found

---

## Get Document File

Download the original document file.

**Endpoint**: `GET /api/v1/documents/{document_id}/file`

**Headers**: `Authorization: Bearer <token>`

**Response** (200): File stream (PDF or DOCX)

**Content-Type**: `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

**Errors**:
- `404`: Document not found or file missing

---

## Delete Document

Delete a document and all associated data.

**Endpoint**: `DELETE /api/v1/documents/{document_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (204): No content

**Errors**:
- `404`: Document not found

**Note**: Deleting a document also deletes:
- All extracted clauses
- All vector embeddings for the document
- The document file

---

## Document Statuses

| Status | Description | Next Actions |
|--------|-------------|--------------|
| `uploaded` | File uploaded, processing not started | Wait for processing |
| `processing` | Document is being processed | Wait for completion |
| `processed` | Processing complete | Extract clauses, Q&A |
| `failed` | Processing failed | Review error, re-upload |

---

## Endpoint Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/documents/upload` | Yes | Upload document |
| GET | `/documents/` | Yes | List documents |
| GET | `/documents/{id}` | Yes | Get document |
| GET | `/documents/{id}/file` | Yes | Download file |
| DELETE | `/documents/{id}` | Yes | Delete document |

---

## File Limits

| Limit | Value |
|-------|-------|
| **Max File Size** | 50MB |
| **Max Pages** | 100 |
| **Supported Types** | PDF, DOCX |

---

## Processing Time

| Document Size | Estimated Time |
|---------------|----------------|
| < 10 pages | 30-60 seconds |
| 10-50 pages | 1-3 minutes |
| 50-100 pages | 3-5 minutes |

---

## Next Steps

- **[Clauses API](clauses.md)** - Clause extraction
- **[Conversations API](conversations.md)** - Q&A endpoints

