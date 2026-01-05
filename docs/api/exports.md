# Exports API

Export endpoints for evidence packs, clause exports, and review checklists.

---

## Download Evidence Pack (Message)

Generate PDF evidence pack for a specific Q&A message.

**Endpoint**: `GET /api/v1/conversations/{conversation_id}/messages/{message_id}/evidence-pack`

**Headers**: `Authorization: Bearer <token>`

**Response** (200): PDF file stream

**Content-Type**: `application/pdf`

**Content-Disposition**: `attachment; filename="evidence-pack-{message_id}.pdf"`

**Errors**:
- `404`: Conversation or message not found
- `400`: Message is not an assistant message

**Contents**:
- Question and answer
- Citations with page numbers
- Document excerpts
- Workspace and conversation metadata

---

## Download Evidence Pack (Conversation)

Generate PDF evidence pack for entire conversation.

**Endpoint**: `GET /api/v1/conversations/{conversation_id}/evidence-pack`

**Headers**: `Authorization: Bearer <token>`

**Response** (200): PDF file stream

**Content-Type**: `application/pdf`

**Content-Disposition**: `attachment; filename="conversation-evidence-pack-{conversation_id}.pdf"`

**Errors**:
- `404`: Conversation not found or no messages

**Contents**:
- All Q&A pairs in conversation
- All citations
- Conversation summary

---

## Export Clauses

Export clauses for a document in JSON or CSV format.

**Endpoint**: `GET /api/v1/documents/{document_id}/clauses/export?format={json|csv}`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `format`: `json` or `csv` (default: `json`)

**Response** (200): File stream

**Content-Type**: 
- `application/json` (JSON format)
- `text/csv` (CSV format)

**Content-Disposition**: `attachment; filename="clauses-{document_name}-{id}.{ext}"`

**Errors**:
- `404`: Document not found or no clauses

**JSON Format**:
```json
[
  {
    "id": "uuid",
    "clause_type": "Termination",
    "extracted_text": "...",
    "page_number": 5,
    "risk_score": 20.0,
    "risk_flags": [],
    ...
  }
]
```

**CSV Format**: Comma-separated values with headers

---

## Download Review Checklist

Generate PDF review checklist for a document.

**Endpoint**: `GET /api/v1/documents/{document_id}/review-checklist`

**Headers**: `Authorization: Bearer <token>`

**Response** (200): PDF file stream

**Content-Type**: `application/pdf`

**Content-Disposition**: `attachment; filename="review-checklist-{document_name}-{id}.pdf"`

**Errors**:
- `404`: Document not found or no clauses

**Contents**:
- Document summary
- All clauses organized by type
- Risk scores and flags
- Review recommendations

---

## Download Highlighted Contract

Export contract PDF with highlighted risky clauses.

**Endpoint**: `GET /api/v1/documents/{document_id}/highlighted-contract`

**Headers**: `Authorization: Bearer <token>`

**Response** (200): PDF file stream

**Content-Type**: `application/pdf`

**Content-Disposition**: `inline; filename="highlighted-{document_name}.pdf"`

**Errors**:
- `404`: Document not found or no clauses
- `400`: Document is not PDF

**Note**: Only available for PDF documents. Highlights clauses based on risk score:
- High risk (50-74): Yellow highlight
- Critical risk (75-100): Red highlight

---

## Endpoint Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/conversations/{id}/messages/{msg_id}/evidence-pack` | Yes | Message evidence pack |
| GET | `/conversations/{id}/evidence-pack` | Yes | Conversation evidence pack |
| GET | `/documents/{id}/clauses/export` | Yes | Export clauses (JSON/CSV) |
| GET | `/documents/{id}/review-checklist` | Yes | Review checklist PDF |
| GET | `/documents/{id}/highlighted-contract` | Yes | Highlighted contract PDF |

---

## Export Formats

| Format | Use Case | File Type |
|--------|----------|-----------|
| **Evidence Pack** | Q&A documentation | PDF |
| **Clauses JSON** | Data analysis | JSON |
| **Clauses CSV** | Spreadsheet import | CSV |
| **Review Checklist** | Contract review | PDF |
| **Highlighted Contract** | Visual risk review | PDF |

---

## Next Steps

- **[User Guide](../user-guide/getting-started.md)** - Getting started
- **[Architecture](../architecture/overview.md)** - System design

