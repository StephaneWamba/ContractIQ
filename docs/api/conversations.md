# Conversations API

Q&A conversation endpoints for asking questions about contracts.

---

## Create Conversation

Create a new conversation.

**Endpoint**: `POST /api/v1/workspaces/{workspace_id}/conversations`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Payment Terms Discussion"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "title": "Payment Terms Discussion",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "messages": []
}
```

---

## List Conversations

List all conversations in a workspace.

**Endpoint**: `GET /api/v1/workspaces/{workspace_id}/conversations`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "total": 5,
  "conversations": [
    {
      "id": "uuid",
      "workspace_id": "uuid",
      "title": "Payment Terms Discussion",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Get Conversation

Get a conversation with all messages.

**Endpoint**: `GET /api/v1/conversations/{conversation_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "title": "Payment Terms Discussion",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What are the payment terms?",
      "citations": null,
      "message_index": 0,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "The payment terms are Net 30 days...",
      "citations": [
        {
          "document_id": "uuid",
          "document_name": "contract.pdf",
          "page_number": 3,
          "section_name": "PAYMENT TERMS",
          "text_excerpt": "Payment shall be due...",
          "similarity_score": 0.92
        }
      ],
      "message_index": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Ask Question

Ask a question in a conversation.

**Endpoint**: `POST /api/v1/conversations/{conversation_id}/ask`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "question": "What are the termination terms?",
  "document_ids": ["uuid1", "uuid2"]
}
```

**Query Parameters**:
- `document_ids` (optional): Filter search to specific documents

**Response** (200):
```json
{
  "answer": "The contract allows termination with 30 days written notice...",
  "citations": [
    {
      "document_id": "uuid",
      "document_name": "contract.pdf",
      "page_number": 5,
      "section_name": "TERMINATION",
      "text_excerpt": "Either party may terminate...",
      "similarity_score": 0.95,
      "chunk_id": "chunk_123",
      "coordinates": {
        "x0": 100,
        "y0": 200,
        "x1": 500,
        "y1": 250,
        "page": 5
      }
    }
  ],
  "retrieved_chunks_count": 5
}
```

**Processing**:
1. Vector search for relevant chunks
2. LLM generates answer with citations
3. Message saved to conversation

**Errors**:
- `404`: Conversation not found
- `400`: Invalid question or no documents in workspace

---

## Update Conversation

Update conversation title.

**Endpoint**: `PATCH /api/v1/conversations/{conversation_id}`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Updated Title"
}
```

**Response** (200):
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "title": "Updated Title",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z"
}
```

---

## Delete Conversation

Delete a conversation and all messages.

**Endpoint**: `DELETE /api/v1/conversations/{conversation_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (204): No content

**Errors**:
- `404`: Conversation not found

---

## Citation Format

```json
{
  "document_id": "uuid",
  "document_name": "contract.pdf",
  "page_number": 5,
  "section_name": "TERMINATION",
  "text_excerpt": "Either party may terminate...",
  "similarity_score": 0.95,
  "chunk_id": "chunk_123",
  "coordinates": {
    "x0": 100,
    "y0": 200,
    "x1": 500,
    "y1": 250,
    "page": 5
  }
}
```

---

## Endpoint Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/workspaces/{id}/conversations` | Yes | Create conversation |
| GET | `/workspaces/{id}/conversations` | Yes | List conversations |
| GET | `/conversations/{id}` | Yes | Get conversation |
| POST | `/conversations/{id}/ask` | Yes | Ask question |
| PATCH | `/conversations/{id}` | Yes | Update conversation |
| DELETE | `/conversations/{id}` | Yes | Delete conversation |

---

## RAG Pipeline

The Q&A system uses a RAG (Retrieval-Augmented Generation) pipeline:

1. **Retrieve**: Vector search for relevant document chunks
2. **Generate**: LLM generates answer with citations
3. **Validate**: Ensure citations reference valid sources

---

## Next Steps

- **[Exports API](exports.md)** - Export services

