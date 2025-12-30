# Root Causes Analysis: PO Tax Extraction Issues

## Root Cause #1: Paragraph Extraction Combines Multiple Lines

### Problem:

Azure Form Recognizer's `prebuilt-layout` model extracts paragraphs that may combine multiple table rows or lines into a single paragraph.

### Example:

**PDF Table Format:**

```
Subtotal:        $2,000.00
Tax (8%):        $160.00
Total:           $2,160.00
```

**Azure Extracts as Paragraph:**

```
"Subtotal: $2,000.00 Tax (8%): $160.00 Total: $2,160.00"
```

### Impact:

When extracting tax_amount using `re.findall(r'[\d,]+\.?\d*', content)`:

- Finds ALL numbers: `["2000.00", "8", "160.00", "2160.00"]`
- `numbers[-1]` = `"2160.00"` (TOTAL, not tax!)
- This explains **Result 4**: tax_amount = 2024.0 (likely total from a different calculation)

### Root Cause:

**Line 490 in form_recognizer.py**: `num_str = numbers[-1]` assumes the last number is the tax amount, but in combined paragraphs, the last number is often the TOTAL.

---

## Root Cause #2: Extraction Order Dependency

### Problem:

Tax amount extraction happens BEFORE subtotal is guaranteed to be available.

### Current Flow:

1. Extract from tables (line items, subtotal/tax/total)
2. Extract from paragraphs (subtotal, tax, total)
3. Calculate subtotal from line items (fallback)
4. Final calculations

### Issue:

- **Line 496**: Validation checks `if subtotal and subtotal > 0`
- But if subtotal extraction from paragraphs/tables fails, `subtotal` is `None`
- Tax amount is stored without validation (line 507)
- Later, when subtotal is calculated from line items, tax_rate is recalculated from wrong tax_amount

### Impact:

**Results 9, 10, 12**:

- Tax amount extracted as small values (2.0, 3.0, 4.0) without validation
- When subtotal (2000.0) is calculated later, tax_rate = (2.0/2000.0) \* 100 = 0.10%
- Should be: tax_rate = 8% → tax_amount = 160.0

### Root Cause:

**Line 507**: Tax amount stored without validation when subtotal is not yet available.

---

## Root Cause #3: Table Extraction May Miss Totals Section

### Problem:

The table extraction logic (lines 374-429) only processes rows with `row_idx >= 1` (skips header), but:

- Totals section might be in a separate table
- Totals section might not have enough columns to match the condition `len(row_cells) >= 2`
- Totals might be formatted differently (e.g., single column with labels and values)

### Impact:

- Subtotal/tax/total extraction from tables fails
- Falls back to paragraph extraction (which has Root Cause #1)
- Wrong values extracted

### Root Cause:

**Line 374-429**: Table extraction logic doesn't handle totals section reliably.

---

## Root Cause #4: Tax Rate Extraction Priority Issue

### Problem:

Tax rate extraction (line 474) only runs if `not extracted_data.get("tax_rate")`, but:

- If tax_amount is extracted first (line 484-509), it calculates tax_rate from wrong tax_amount
- This wrong tax_rate is then used, and the correct tax_rate from text is skipped

### Example Flow:

1. Extract tax_amount = 2160.0 (wrong, it's the total)
2. Calculate tax_rate = (2160.0 / 2000.0) \* 100 = 108% (wrong)
3. Later, try to extract tax_rate from "Tax (8%):" but it's already set, so skipped

### Root Cause:

**Line 474**: `if tax_rate_match and not extracted_data.get("tax_rate")` - but tax_rate might already be set from wrong calculation.

---

## Root Cause #5: Number Extraction Regex Too Greedy

### Problem:

The regex `r'[\d,]+\.?\d*'` matches:

- `"8"` from "Tax (8%)"
- `"160.00"` from "$160.00"
- `"2160.00"` from "$2,160.00"
- `"2000.00"` from "$2,000.00"

When content is: `"Tax (8%): $160.00 Total: $2,160.00"`

### Impact:

- `numbers = ["8", "160.00", "2160.00", "2000.00"]`
- `numbers[-1]` = `"2000.00"` or `"2160.00"` (wrong!)

### Root Cause:

**Line 485**: `re.findall(r'[\d,]+\.?\d*', content)` is too greedy and doesn't distinguish between tax amount and other numbers in the same paragraph.

---

## Summary of Root Causes

1. **Paragraph Extraction Combines Lines**: Azure combines multiple table rows into one paragraph
2. **Wrong Number Selection**: `numbers[-1]` assumes last number is tax, but it's often the total
3. **Extraction Order**: Tax extracted before subtotal validation is possible
4. **Missing Validation**: Tax amount stored without validation when subtotal unavailable
5. **Table Extraction Gaps**: Totals section not reliably extracted from tables
6. **Regex Too Greedy**: Matches all numbers, can't distinguish tax from total

---

## Recommended Fixes

1. **Improve Number Selection**: Instead of `numbers[-1]`, find the number that's closest to expected tax amount
2. **Better Validation**: Always validate tax_amount against subtotal, even if calculated later
3. **Extract from Tables First**: Prioritize table extraction for totals section
4. **Smarter Regex**: Use context-aware extraction (e.g., number after "Tax" label, before "Total")
5. **Re-calculate After Subtotal**: If subtotal is calculated later, re-validate and re-calculate tax values

