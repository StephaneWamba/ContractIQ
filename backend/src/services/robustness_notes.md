# System Robustness Architecture

## Multi-Layer Validation Strategy

### 1. **Ground Truth Protection**
- **Subtotal**: Always calculated from line items first (deterministic, 100% accurate)
- **Line Items**: Extracted from structured tables (high confidence)
- **Total Amount**: Can be calculated from line items if not extracted

### 2. **Multi-Pass Extraction**
- **Phase 1**: Ground truth (line items → subtotal)
- **Phase 2**: Structured extraction (tables)
- **Phase 3**: LLM-enhanced extraction (complex paragraphs)
- **Phase 4**: Validation and reconciliation
- **Phase 5**: Derived calculations (tax_amount = subtotal × tax_rate)

### 3. **LLM Validation Layer**
- **Tax Amount Validation**: LLM validates if extracted tax matches calculated tax
- **Extraction Error Detection**: Distinguishes extraction errors from real discrepancies
- **Context Understanding**: Handles combined paragraphs, ambiguous formats

### 4. **Cross-Validation**
- **PO Tax**: Validated against calculated (subtotal × tax_rate)
- **Invoice Tax**: Validated against Azure extraction + calculated
- **Currency**: Multiple extraction methods (label, symbol, inference)
- **Line Items**: Fuzzy matching for description-based matching

## Why This Is Robust to New Documents

### ✅ **Not Case-by-Case Fixes**
- **LLM understands context**: Handles new document formats automatically
- **Multi-pass approach**: Tries multiple extraction methods, uses best result
- **Validation layer**: Catches extraction errors regardless of document format
- **Ground truth protection**: Always has reliable baseline (line items)

### ✅ **Adaptive Extraction**
- **Regex fallback**: Works when LLM unavailable
- **Table extraction**: Handles structured documents
- **Paragraph analysis**: Handles unstructured text
- **Symbol inference**: Handles currency even without explicit labels

### ✅ **Error Detection**
- **Tax validation**: Detects if wrong number was extracted
- **Calculation validation**: Ensures tax_amount = subtotal × tax_rate
- **Tolerance checks**: Handles rounding differences
- **Confidence scoring**: Tracks extraction reliability

## Example: How It Handles New Document Format

**New Document Format:**
```
Subtotal: $2,000.00
VAT (20%): $400.00
Grand Total: $2,400.00
```

**System Response:**
1. **Ground Truth**: Line items → subtotal = $2,000.00 ✓
2. **Table Extraction**: Finds "Subtotal: $2,000.00" → validates against ground truth ✓
3. **LLM Extraction**: Understands "VAT (20%)" → extracts tax_rate=20%, tax_amount=$400.00 ✓
4. **Validation**: Calculated tax = $2,000 × 0.20 = $400.00 → matches extracted ✓
5. **Result**: Correct extraction, no false discrepancies ✓

**If Extraction Error:**
- Extracted tax_amount = $2,400.00 (wrong - this is total)
- LLM Validation: "This is the total amount, not tax amount" → uses calculated $400.00 ✓
- Result: Error corrected automatically ✓

## Continuous Improvement

- **LLM learns from context**: Better understanding of document variations
- **Validation catches errors**: Prevents false discrepancies
- **Multi-method extraction**: Increases success rate
- **Ground truth baseline**: Ensures accuracy even when extraction fails


