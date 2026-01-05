# Clause Extraction

Extract and analyze key clauses from your contracts with automated risk assessment.

---

## What is Clause Extraction?

Clause extraction identifies and categorizes important contract clauses, providing:
- **Clause Type**: Termination, Liability, Payment, etc.
- **Risk Score**: 0-100 scale indicating risk level
- **Risk Flags**: Specific risk factors identified
- **Risk Reasoning**: Explanation of risk assessment
- **Confidence Score**: Extraction accuracy (0-1)

---

## Clause Types

| Clause Type | Description | Examples |
|------------|-------------|----------|
| **Termination** | Termination conditions | Early termination, breach termination |
| **Payment** | Payment terms | Payment schedule, late fees, penalties |
| **Liability** | Liability limitations | Liability caps, exclusions |
| **Indemnification** | Indemnification clauses | Hold harmless provisions |
| **Intellectual Property** | IP ownership and rights | IP licensing, ownership |
| **Confidentiality** | Confidentiality obligations | NDA terms, data protection |
| **Dispute Resolution** | Dispute handling | Arbitration, jurisdiction |
| **Force Majeure** | Force majeure provisions | Unforeseen circumstances |
| **Compliance** | Regulatory compliance | Certifications, standards |
| **Insurance** | Insurance requirements | Coverage, limits |
| **Warranties** | Warranties and representations | Service warranties |
| **Limitation of Damages** | Damage limitations | Damage caps, exclusions |
| **Data Privacy** | Data protection | GDPR, privacy obligations |
| **Non-Compete** | Non-compete clauses | Restrictive covenants |
| **Assignment** | Assignment rights | Transfer restrictions |
| **Governing Law** | Choice of law | Jurisdiction, venue |
| **Notices** | Notice requirements | Communication methods |
| **Amendment** | Amendment procedures | Change processes |
| **Severability** | Severability clauses | Invalidity handling |
| **Entire Agreement** | Entire agreement clauses | Integration clauses |

---

## Risk Scoring

### Risk Score Ranges

| Score Range | Risk Level | Description | Action |
|-------------|-----------|-------------|--------|
| **0-24** | Low | Standard, acceptable terms | Review if needed |
| **25-49** | Medium | Some concerns | Review recommended |
| **50-74** | High | Significant concerns | Negotiation recommended |
| **75-100** | Critical | Major issues | Immediate attention required |

### Risk Flags

| Flag | Description |
|------|-------------|
| `unfavorable_termination` | One-sided termination rights |
| `high_liability` | Unlimited or very high liability caps |
| `unfair_payment_terms` | Penalties, late fees, unfavorable terms |
| `weak_indemnification` | Limited indemnification protection |
| `ip_risk` | Unfavorable IP ownership or licensing |
| `compliance_risk` | Missing required compliance clauses |
| `data_privacy_risk` | Weak data protection provisions |
| `excessive_penalties` | Excessive penalties or liquidated damages |
| `one_sided_terms` | Terms that heavily favor one party |
| `unclear_language` | Ambiguous or unclear language |
| `missing_protections` | Missing standard protections |

---

## Extraction Workflow

```mermaid
graph LR
    A[Select Document] --> B[Click Extract Clauses]
    B --> C[LLM Analysis]
    C --> D[Clause Identification]
    D --> E[Risk Assessment]
    E --> F[Results Display]
```

### Steps

1. **Navigate to Clauses Page**
2. **Select Document** (must be processed)
3. **Click Extract Clauses**
4. **Wait for Extraction** (30-60 seconds)
5. **Review Results**

---

## Viewing Clauses

### Clause Table

The clause table displays:
- **Clause Type**: Category of clause
- **Page Number**: Where clause appears
- **Risk Score**: Visual risk badge
- **Risk Flags**: List of risk factors
- **Confidence**: Extraction confidence

### Filtering Clauses

Filter by:
- **Clause Type**: Specific clause category
- **Risk Score Range**: Min/max risk score
- **Risk Flags**: Clauses with specific flags

### Clause Details

Click on a clause to see:
- **Full Text**: Complete clause text
- **Risk Reasoning**: Detailed risk explanation
- **Page Reference**: Exact page location
- **Confidence Score**: Extraction accuracy

---

## Re-extraction

If you need to re-extract clauses:
1. Click **Extract Clauses** again
2. Select **Force Re-extract**
3. Existing clauses will be deleted
4. New extraction will run

**Use Cases**:
- Document was updated
- Extraction quality was poor
- New clause types needed

---

## Exporting Clauses

### Export Formats

| Format | Use Case |
|--------|----------|
| **JSON** | Programmatic analysis |
| **CSV** | Spreadsheet analysis |

### Export Options

1. Go to Clauses page
2. Select document
3. Click **Export**
4. Choose format
5. Download file

---

## Best Practices

| Practice | Recommendation |
|----------|----------------|
| **Review High-Risk Clauses** | Focus on scores > 50 |
| **Check Risk Reasoning** | Understand why clause is risky |
| **Compare Across Documents** | Identify patterns |
| **Export for Analysis** | Use CSV for detailed review |
| **Re-extract if Needed** | Improve extraction quality |

---

## Troubleshooting

### No Clauses Extracted

**Possible Causes**:
- Document not processed
- Document has no extractable clauses
- Extraction failed

**Solutions**:
- Verify document status is "processed"
- Check document content
- Try re-extraction

### Low Confidence Scores

- **Document Quality**: Poor OCR or formatting
- **Clause Clarity**: Ambiguous clause language
- **Document Type**: Non-standard contract format

### Missing Clause Types

- **Document Content**: Clause type may not exist
- **Extraction Model**: May not recognize all types
- **Re-extract**: Try force re-extraction

---

## Next Steps

- **[Q&A Conversations](qa-conversations.md)** - Ask questions about extracted clauses
- **[Evidence Packs](evidence-packs.md)** - Generate evidence packs with clauses
- **[API Reference](../api/clauses.md)** - Programmatic clause access

