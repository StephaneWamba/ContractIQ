# Logical Correctness Assessment: CSV vs Generated PDFs

## Generated PDF Sets (24 documents = 12 PO/Invoice pairs)

### Set 1: Multi-Currency (3 pairs)
1. **USD**: PO 8% tax, Invoice 8% tax → **Expected: Perfect match**
2. **EUR**: PO 20% tax, Invoice 20% tax → **Expected: Perfect match**
3. **GBP**: PO 20% tax, Invoice 20% tax → **Expected: Perfect match**

### Set 2: Different Tax Rates (4 pairs)
4. **NO_TAX**: 0% → **Expected: Perfect match**
5. **STANDARD**: 8% → **Expected: Perfect match**
6. **HIGH**: 10% → **Expected: Perfect match**
7. **VAT**: 20% → **Expected: Perfect match**

### Set 3: Tax Rate Mismatch
8. **PO**: 8% tax, Invoice: 10% tax → **Expected: Tax rate mismatch**

### Set 4: Currency Mismatch
9. **PO**: USD 8% tax, Invoice: EUR 20% tax → **Expected: Currency mismatch + Tax rate mismatch**

### Set 5: Large Quantities
10. **PO**: 8% tax, Invoice: 8% tax → **Expected: Perfect match**

### Set 6: High-Value Items
11. **PO**: 8% tax, Invoice: 8% tax → **Expected: Perfect match**

### Set 7: Many Line Items
12. **PO**: 8% tax, 15 items (001-015), Invoice: 8% tax, 15 items (001-015) → **Expected: Perfect match**

---

## CSV Results Analysis

### ✅ **Result 1: Product A (EUR), Product B (EUR)**
- **Expected**: Perfect match (EUR, 20% tax both)
- **Actual**: Perfect match ✓
- **Assessment**: ✅ **CORRECT**

### ✅ **Result 2: Product A (GBP), Product B (GBP)**
- **Expected**: Perfect match (GBP, 20% tax both)
- **Actual**: Perfect match ✓
- **Assessment**: ✅ **CORRECT**

### ⚠️ **Result 3: International Item**
- **Expected**: Currency mismatch (PO: USD 8%, Invoice: EUR 20%) + Tax rate mismatch
- **Actual**: 
  - Line items: Perfect match ✓
  - Tax rate mismatch: PO=8.00%, Invoice=20.00% ✓
  - **MISSING**: Currency mismatch not shown!
- **Tax Calculation Check**:
  - PO: tax_amount=8.0, tax_rate=8% → subtotal should be 100.0, but line item total = 1200.0 ❌
  - Invoice: tax_amount=240.0, tax_rate=20% → subtotal = 1200.0 ✓
- **Assessment**: ⚠️ **PARTIALLY CORRECT** - Tax mismatch detected, but:
  1. Currency mismatch missing
  2. PO tax_amount extraction seems wrong (8.0 vs expected 96.0 for 1200 subtotal at 8%)

### ⚠️ **Result 4: Product A (USD), Product B (USD)**
- **Expected**: Perfect match (USD, 8% tax both) OR Tax mismatch if this is the tax-mismatch set
- **Actual**: 
  - Line items: Perfect match ✓
  - Tax rate mismatch: PO=8.00%, Invoice=20.00% ❌
- **Tax Calculation Check**:
  - PO: tax_amount=8.0, tax_rate=8% → subtotal should be 100.0, but line items total = 2000.0 ❌
  - Invoice: tax_amount=400.0, tax_rate=20% → subtotal = 2000.0 ✓
- **Assessment**: ❌ **INCORRECT** - This should be a perfect match (USD 8% both), but shows tax mismatch. PO tax extraction is wrong.

### ✅ **Result 5: Premium Equipment, Professional Service**
- **Expected**: Perfect match (High-value items, 8% tax both)
- **Actual**: Perfect match ✓
- **Assessment**: ✅ **CORRECT**

### ⚠️ **Result 6: Item 1-15 (Many Items)**
- **Expected**: Perfect match (15 items, 8% tax both)
- **Actual**: 
  - Items 001-011, 013-015: Perfect match ✓
  - Item 12: "Extra in Invoice" ⚠️
  - Item 8: Empty item_number but matched by description ✓
- **Assessment**: ⚠️ **MOSTLY CORRECT** - Item 12 shouldn't be extra if both have 15 items. This suggests:
  - PO has items 001-011, 013-015 (missing 012)
  - Invoice has items 001-012, 013-015
  - OR Azure didn't extract item 012 from PO correctly

### ✅ **Result 7: Item A, Item B**
- **Expected**: Tax rate mismatch (PO: 8%, Invoice: 10%)
- **Actual**: Perfect match (no discrepancies shown)
- **Assessment**: ⚠️ **MISSING DISCREPANCY** - Should show tax rate mismatch but doesn't. Either:
  - Tax rates weren't extracted correctly
  - Or this isn't the tax-mismatch pair

### ✅ **Results 8-12: Standard Item, Premium Item**
- **Expected**: Perfect matches (Tax rate sets: NO_TAX, STANDARD, HIGH, VAT)
- **Actual**: All perfect matches ✓
- **Assessment**: ✅ **CORRECT**

### ✅ **Result 13: Product A (EUR), Product B (EUR)**
- **Expected**: Perfect match (EUR, 20% tax both)
- **Actual**: Perfect match ✓
- **Assessment**: ✅ **CORRECT**

### ⚠️ **Result 14: Product A (EUR), Product B (EUR)**
- **Expected**: Perfect match (EUR, 20% tax both)
- **Actual**: 
  - Line items: Perfect match ✓
  - Tax rate mismatch: PO=20.00%, Invoice=8.00% ❌
- **Tax Calculation Check**:
  - PO: tax_amount=20.0, tax_rate=20% → subtotal should be 100.0, but line items total = 2000.0 ❌
  - Invoice: tax_amount=160.0, tax_rate=8% → subtotal = 2000.0 ✓
- **Assessment**: ❌ **INCORRECT** - Should be perfect match (EUR 20% both), but shows tax mismatch. PO tax extraction is wrong.

---

## Summary of Issues

### 🔴 **Critical Issues:**

1. **PO Tax Amount Extraction is Wrong** (Results 3, 4, 14):
   - PO tax_amount values are too low (8.0, 20.0) compared to line item totals
   - This causes false tax rate mismatches
   - **Root Cause**: PO extraction from layout model may not be extracting subtotal/tax correctly

2. **Missing Currency Mismatch** (Result 3):
   - Should show currency mismatch (USD vs EUR) but doesn't
   - **Root Cause**: Currency extraction may be failing for PO

3. **Missing Tax Rate Mismatch** (Result 7):
   - Should show tax rate mismatch (8% vs 10%) but doesn't
   - **Root Cause**: Tax rates may not be extracted correctly for this pair

4. **Extra Item Issue** (Result 6):
   - Item 12 shown as "Extra in Invoice" when both should have 15 items
   - **Root Cause**: Azure may not have extracted item 012 from PO (or PO generation issue)

### ✅ **What's Working:**

- Line item matching: ✅ Perfect
- Item number normalization (013 = 13): ✅ Working
- Description-based matching: ✅ Working
- Most tax rate matches: ✅ Correct
- Discrepancy detection logic: ✅ Correct (when data is extracted properly)

---

## Recommendations

1. **Fix PO Tax/Subtotal Extraction**: The layout model extraction for POs needs improvement to correctly extract subtotal and tax amounts from the totals section.

2. **Improve Currency Extraction**: Ensure currency codes are extracted from both PO and Invoice for currency mismatch detection.

3. **Verify PDF Generation**: Check if item 012 is actually in the PO PDF for the "many items" set.

4. **Add Extraction Validation**: Add checks to ensure extracted tax_amount matches calculated tax_amount from subtotal and tax_rate.


