# Document Management

Upload, process, and manage contract documents in ContractIQ.

---

## Supported File Types

| Format | Extension | Max Size | Notes |
|-------|-----------|---------|-------|
| PDF | `.pdf` | 50MB | Best support, accurate page numbers |
| DOCX | `.docx` | 50MB | Page numbers approximated |

---

## Document Statuses

| Status | Description | Actions Available |
|--------|-------------|-------------------|
| **uploaded** | File uploaded, processing not started | Wait for processing |
| **processing** | Document is being processed | Wait for completion |
| **processed** | Processing complete, ready for use | Extract clauses, Q&A |
| **failed** | Processing failed | Review error, re-upload |

---

## Upload Process

### Upload Flow

```mermaid
graph LR
    A[Select File] --> B[Upload]
    B --> C[Status: uploaded]
    C --> D[Background Processing]
    D --> E[Status: processing]
    E --> F[Text Extraction]
    F --> G[LLM Structuring]
    G --> H[Vector Indexing]
    H --> I[Status: processed]
```

### Steps

1. **Navigate to Documents Page**
2. **Click Upload Document**
3. **Select File** (drag & drop supported)
4. **Select Workspace** (if multiple workspaces)
5. **Click Upload**

### Processing Details

During processing, the system:
1. Extracts text using PyMuPDF (PDF) or python-docx (DOCX)
2. Uses LLM to structure the document:
   - Identifies sections
   - Creates semantic chunks
   - Extracts metadata
3. Indexes chunks in vector store for RAG
4. Updates document status to "processed"

---

## Viewing Documents

### Document List

The documents page shows:
- Document name
- Original filename
- File type
- Status
- Page count
- File size
- Upload date

### Document Viewer

1. Click on a document
2. PDF viewer opens with:
   - Page navigation
   - Zoom controls
   - Search functionality
   - Citation highlighting (when viewing Q&A results)

---

## Document Processing

### Processing Time

| Document Size | Estimated Time |
|---------------|----------------|
| < 10 pages | 30-60 seconds |
| 10-50 pages | 1-3 minutes |
| 50-100 pages | 3-5 minutes |

**Factors affecting processing**:
- Document complexity
- Number of pages
- LLM API response time
- System load

### Processing Status

The UI automatically refreshes to show processing status. You can:
- See real-time status updates
- Continue working while processing
- Get notified when processing completes

---

## Document Limits

| Limit | Value | Notes |
|-------|-------|-------|
| **Max File Size** | 50MB | Per document |
| **Max Pages** | 100 | Configurable |
| **Concurrent Processing** | Unlimited | Background tasks |

---

## Deleting Documents

**Warning**: Deleting a document removes:
- The document file
- All extracted clauses
- All vector embeddings
- All citations in conversations

**To Delete**:
1. Go to Documents page
2. Click on document
3. Click **Delete**
4. Confirm deletion

---

## Troubleshooting

### Processing Fails

**Common Causes**:
- File is corrupted
- File format not supported
- File too large (> 50MB)
- Too many pages (> 100)

**Solutions**:
- Verify file integrity
- Check file format (PDF/DOCX only)
- Reduce file size or split document
- Check backend logs for errors

### Document Not Appearing

- **Check workspace**: Ensure correct workspace selected
- **Refresh page**: Status may need refresh
- **Check filters**: Filters may hide document

### Slow Processing

- **Large files**: Processing time increases with size
- **LLM API delays**: External API may be slow
- **System load**: High load affects processing

---

## Best Practices

| Practice | Recommendation |
|----------|----------------|
| **File Naming** | Use descriptive names (e.g., "Vendor-Agreement-2024.pdf") |
| **File Size** | Keep files < 20MB for faster processing |
| **Organization** | Use workspaces to organize by project/client |
| **Backup** | Keep original files outside ContractIQ |
| **Version Control** | Upload new versions as separate documents |

---

## Next Steps

- **[Clause Extraction](clause-extraction.md)** - Extract clauses from processed documents
- **[Q&A Conversations](qa-conversations.md)** - Ask questions about documents
- **[Evidence Packs](evidence-packs.md)** - Generate evidence packs

