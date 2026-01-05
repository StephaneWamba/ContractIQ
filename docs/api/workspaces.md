# Workspaces API

Workspace management endpoints for organizing documents and conversations.

---

## Create Workspace

Create a new workspace.

**Endpoint**: `POST /api/v1/workspaces/`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "Q4 Contracts",
  "description": "Contracts for Q4 2024",
  "is_temporary": false
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "Q4 Contracts",
  "description": "Contracts for Q4 2024",
  "is_temporary": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## List Workspaces

List all workspaces for the current user.

**Endpoint**: `GET /api/v1/workspaces/`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "name": "Q4 Contracts",
    "description": "Contracts for Q4 2024",
    "is_temporary": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**Caching**: Results cached for 5 minutes

---

## Get Workspace

Get a specific workspace.

**Endpoint**: `GET /api/v1/workspaces/{workspace_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "Q4 Contracts",
  "description": "Contracts for Q4 2024",
  "is_temporary": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors**:
- `404`: Workspace not found or not owned by user

---

## Delete Workspace

Delete a workspace and all associated data.

**Endpoint**: `DELETE /api/v1/workspaces/{workspace_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (204): No content

**Errors**:
- `404`: Workspace not found or not owned by user

**Note**: Deleting a workspace also deletes:
- All documents in the workspace
- All clauses extracted from those documents
- All conversations in the workspace
- All vector embeddings (ChromaDB collection)

---

## Endpoint Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/workspaces/` | Yes | Create workspace |
| GET | `/workspaces/` | Yes | List workspaces |
| GET | `/workspaces/{id}` | Yes | Get workspace |
| DELETE | `/workspaces/{id}` | Yes | Delete workspace |

---

## Workspace Isolation

- Each workspace is isolated to its owner user
- Documents, clauses, and conversations are workspace-scoped
- Vector store collections are per-workspace

---

## Next Steps

- **[Documents API](documents.md)** - Document operations
- **[Conversations API](conversations.md)** - Q&A endpoints

