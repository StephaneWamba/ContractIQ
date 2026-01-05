# API Overview

ContractIQ REST API documentation.

---

## Base URL

```
http://localhost:8002/api/v1
```

Production: `https://api.contractiq.com/api/v1`

---

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require authentication.

### JWT Token

Include token in `Authorization` header:

```
Authorization: Bearer <token>
```

### Token Expiration

- **Access Token**: 7 days
- **Refresh**: Use `/auth/refresh` endpoint

---

## Response Format

### Success Response

```json
{
  "id": "uuid",
  "name": "string",
  "created_at": "2024-01-01T00:00:00Z",
  ...
}
```

### Error Response

```json
{
  "error": true,
  "error_code": "NOT_FOUND",
  "message": "Resource not found",
  "details": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Missing/invalid token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `422` | Unprocessable Entity | Validation error |
| `500` | Internal Server Error | Server error |

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `NOT_FOUND` | Resource not found |
| `UNAUTHORIZED` | Authentication required |
| `FORBIDDEN` | Insufficient permissions |
| `PROCESSING_ERROR` | Document processing failed |
| `EXTERNAL_SERVICE_ERROR` | External API error |
| `RATE_LIMIT_ERROR` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

---

## Rate Limiting

Currently no rate limits. Future: 100 requests/minute per user.

---

## Pagination

List endpoints support pagination:

```
GET /documents/?page=1&page_size=20
```

**Response**:
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [...]
}
```

---

## Filtering

Many list endpoints support filtering:

```
GET /documents/{id}/clauses?clause_type=Termination&min_risk_score=50
```

---

## API Endpoints

| Category | Endpoints |
|----------|-----------|
| **[Authentication](authentication.md)** | Register, login, refresh, current user |
| **[Workspaces](workspaces.md)** | Create, list, get, delete workspaces |
| **[Documents](documents.md)** | Upload, list, get, delete documents |
| **[Clauses](clauses.md)** | Extract, list, get, delete clauses |
| **[Conversations](conversations.md)** | Create, list, ask questions, delete |
| **[Exports](exports.md)** | Evidence packs, clause exports |

---

## Interactive Documentation

Swagger UI available at:
- Development: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

---

## Next Steps

- **[Authentication](authentication.md)** - Auth endpoints
- **[Workspaces](workspaces.md)** - Workspace management
- **[Documents](documents.md)** - Document operations
- **[Clauses](clauses.md)** - Clause extraction
- **[Conversations](conversations.md)** - Q&A endpoints
- **[Exports](exports.md)** - Export services

