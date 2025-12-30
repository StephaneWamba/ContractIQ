# Debugging Implementation: Logging Added

## Changes Implemented

### 1. **Invoice Tax Validation Logging** ✅

Added comprehensive logging to track:
- When LLM validation runs
- What values are being compared (extracted vs calculated)
- What corrections are being made
- Why corrections are or aren't happening

**Log Messages**:
- `[INVOICE TAX VALIDATION]` - All tax validation steps
- Shows: Subtotal, TaxRate, ExtractedTax, ExpectedTax, Difference, Tolerance
- Shows: LLM validation results and corrections
- Shows: When calculated values are used instead of extracted

### 2. **Currency Extraction Logging** ✅

Added logging for both Invoice and PO currency extraction:
- When currency is extracted from Azure field
- When currency is extracted from document text
- When currency is inferred from symbols
- When currency extraction fails

**Log Messages**:
- `[INVOICE CURRENCY]` - Invoice currency extraction
- `[PO CURRENCY]` - PO currency extraction
- Shows: Method used (Azure field, text code, symbol inference)
- Shows: Final currency code extracted

### 3. **Currency Mismatch Detection Logging** ✅

Added logging in matching service to track:
- When currency mismatch check runs
- What currency codes are being compared
- Whether mismatch is detected
- Why mismatch might not be detected (missing currency codes)

**Log Messages**:
- `[CURRENCY CHECK]` - Currency comparison
- `[CURRENCY MISMATCH DETECTED]` - When mismatch is found
- Shows: PO currency and Invoice currency values
- Shows: When currencies match or when one is missing

## How to Use Logs

### View Logs in Docker:
```bash
docker-compose logs -f backend | grep -E "\[INVOICE|\[PO|\[CURRENCY"
```

### Key Things to Look For:

1. **Invoice Tax Validation**:
   - Is LLM validation running? (`LLM extractor is enabled`)
   - Is TaxRate being extracted from Azure? (`calculated_tax_rate`)
   - Is LLM detecting extraction errors? (`is_extraction_error=True`)
   - Are corrections being applied? (`CORRECTING: Using calculated`)

2. **Currency Extraction**:
   - Are currency codes being extracted? (`Final currency code: USD`)
   - Which method is being used? (Azure field, text code, symbol)
   - Are extractions failing? (`Failed to extract currency code`)

3. **Currency Mismatch Detection**:
   - Are both currencies present? (`PO currency: USD, Invoice currency: EUR`)
   - Is mismatch being detected? (`CURRENCY MISMATCH DETECTED`)
   - Why isn't it detected? (`Missing currency codes`)

## Expected Log Output for Problem Cases

### Result 7 (USD - False Tax Mismatch):
```
[INVOICE TAX VALIDATION] Subtotal=2000.00, TaxRate=8.00%, ExtractedTax=400.00, ExpectedTax=160.00, Difference=240.00
[INVOICE TAX VALIDATION] LLM extractor is enabled, running validation
[INVOICE TAX VALIDATION] LLM result: is_extraction_error=True, confidence=0.95
[INVOICE TAX VALIDATION] CORRECTING: Using calculated tax_amount=160.00 instead of extracted=400.00
```

### Result 6 (International - Missing Currency Mismatch):
```
[PO CURRENCY] Final currency code: USD
[INVOICE CURRENCY] Final currency code: EUR
[CURRENCY CHECK] PO currency: USD, Invoice currency: EUR
[CURRENCY MISMATCH DETECTED] PO=USD, Invoice=EUR
```

## Next Steps

1. **Re-process documents** and check logs
2. **Identify root causes** from log output
3. **Fix issues** based on what logs reveal
4. **Verify fixes** by checking logs again


