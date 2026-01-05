# Clauses API

Clause extraction and management endpoints.

---

## Extract Clauses

Extract clauses from a processed document.

**Endpoint**: `POST /api/v1/documents/{document_id}/extract-clauses`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "force_re_extract": false
}
```

**Response** (200):
```json
{
  "document_id": "uuid",
  "clauses_extracted": 15,
  "clauses": [
    {
      "id": "uuid",
      "document_id": "uuid",
      "clause_type": "Termination",
      "extracted_text": "Either party may terminate...",
      "page_number": 5,
      "section": "TERMINATION",
      "confidence_score": 0.95,
      "risk_score": 20.0,
      "risk_flags": [],
      "risk_reasoning": "Standard 30-day notice period...",
      "clause_subtype": "Convenience Termination",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "message": "Clauses extracted successfully"
}
```

**Note**: If clauses already exist, returns existing clauses unless `force_re_extract=true`.

**Errors**:
- `400`: Document not processed
- `404`: Document not found

---

## List Clauses

List clauses for a document with optional filters.

**Endpoint**: `GET /api/v1/documents/{document_id}/clauses`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `clause_type` (optional): Filter by clause type
- `min_risk_score` (optional): Minimum risk score (0-100)
- `max_risk_score` (optional): Maximum risk score (0-100)
- `has_risk_flags` (optional): Filter by presence of risk flags

**Response** (200):
```json
{
  "total": 15,
  "clauses": [
    {
      "id": "uuid",
      "document_id": "uuid",
      "clause_type": "Termination",
      "extracted_text": "Either party may terminate...",
      "page_number": 5,
      "section": "TERMINATION",
      "confidence_score": 0.95,
      "risk_score": 20.0,
      "risk_flags": [],
      "risk_reasoning": "Standard 30-day notice period...",
      "clause_subtype": "Convenience Termination",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Example**: `/documents/{id}/clauses?clause_type=Termination&min_risk_score=50`

---

## Get Clause

Get a specific clause.

**Endpoint**: `GET /api/v1/clauses/{clause_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "clause_type": "Termination",
  "extracted_text": "Either party may terminate...",
  "page_number": 5,
  "section": "TERMINATION",
  "confidence_score": 0.95,
  "risk_score": 20.0,
  "risk_flags": [],
  "risk_reasoning": "Standard 30-day notice period...",
  "clause_subtype": "Convenience Termination",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors**:
- `404`: Clause not found

---

## Delete Clause

Delete a clause.

**Endpoint**: `DELETE /api/v1/clauses/{clause_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (204): No content

**Errors**:
- `404`: Clause not found

---

## Clause Types

| Type | Description |
|------|-------------|
| `Termination` | Termination clauses |
| `Payment` | Payment terms |
| `Liability` | Liability limitations |
| `Indemnification` | Indemnification clauses |
| `Intellectual Property` | IP ownership/licensing |
| `Confidentiality` | Confidentiality obligations |
| `Dispute Resolution` | Arbitration/jurisdiction |
| `Force Majeure` | Force majeure provisions |
| `Compliance` | Regulatory compliance |
| `Insurance` | Insurance requirements |
| `Warranties` | Warranties/representations |
| `Limitation of Damages` | Damage caps |
| `Data Privacy` | Data protection |
| `Non-Compete` | Non-compete clauses |
| `Assignment` | Assignment rights |
| `Governing Law` | Choice of law |
| `Other` | Other clause types |

---

## Risk Scoring

| Score Range | Risk Level | Description |
|-------------|------------|-------------|
| 0-24 | Low | Standard, acceptable terms |
| 25-49 | Medium | Some concerns, review recommended |
| 50-74 | High | Significant concerns, negotiation recommended |
| 75-100 | Critical | Major issues, requires immediate attention |

---

## Risk Flags

| Flag | Description |
|------|-------------|
| `unfavorable_termination` | One-sided termination rights |
| `high_liability` | Unlimited or very high liability caps |
| `unfair_payment_terms` | Penalties, late fees, unfavorable terms |
| `weak_indemnification` | Limited indemnification protection |
| `ip_risk` | Unfavorable IP ownership/licensing |
| `compliance_risk` | Missing required compliance clauses |
| `data_privacy_risk` | Weak data protection provisions |
| `excessive_penalties` | Excessive penalties or liquidated damages |
| `one_sided_terms` | Terms that heavily favor one party |
| `unclear_language` | Ambiguous or unclear language |
| `missing_protections` | Missing standard protections |

---

## Endpoint Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/documents/{id}/extract-clauses` | Yes | Extract clauses |
| GET | `/documents/{id}/clauses` | Yes | List clauses |
| GET | `/clauses/{id}` | Yes | Get clause |
| DELETE | `/clauses/{id}` | Yes | Delete clause |

---

## Next Steps

- **[Conversations API](conversations.md)** - Q&A endpoints
- **[Exports API](exports.md)** - Export services

