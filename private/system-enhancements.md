# System Enhancement Opportunities

## Current System Capabilities

### ✅ What We're Already Doing

1. **Line Item Matching**
   - Quantity comparison
   - Unit price comparison
   - Line total calculation
   - Description fuzzy matching

2. **Discrepancy Detection**
   - Quantity mismatches
   - Price changes
   - Missing items
   - Extra items
   - Description mismatches

3. **Total Amount Extraction**
   - Extracts `AmountDue`, `InvoiceTotal`, or `Total` from invoices
   - Calculates totals from line items when not extracted

4. **Basic Data Extraction**
   - Invoice number, PO number, vendor name
   - Dates, addresses
   - Line items with quantities, prices, totals

---

## Enhancement Opportunities

### 1. **Currency Support** 💱

**Current State:** System assumes USD ($) for all amounts.

**Enhancement Needed:**
- Extract currency code from Azure Form Recognizer (`CurrencyCode` field)
- Store currency in `ExtractedData` model
- Display currency in UI (e.g., "USD $1,000.00" or "EUR €850.00")
- **Currency Conversion:**
  - Detect currency mismatches (PO in USD, Invoice in EUR)
  - Convert to common currency for comparison using exchange rates
  - Flag currency mismatches as discrepancies
  - Support multi-currency reconciliation

**Implementation:**
```python
# In form_recognizer.py
if "CurrencyCode" in document.fields:
    extracted_data["currency_code"] = document.fields["CurrencyCode"].value

# In matching.py
if po_data.currency_code != invoice_data.currency_code:
    # Convert or flag as discrepancy
```

**Azure Field:** `CurrencyCode` (e.g., "USD", "EUR", "GBP")

---

### 2. **Tax Handling** 📊

**Current State:** Taxes are NOT extracted or compared.

**Enhancement Needed:**
- Extract tax fields from Azure:
  - `Tax` (total tax amount)
  - `SubTotal` (amount before tax)
  - Tax rate percentage (if available)
- Store tax information in `ExtractedData`
- **Tax Comparison:**
  - Compare tax amounts between PO and Invoice
  - Detect tax discrepancies (e.g., PO: 8%, Invoice: 10%)
  - Calculate tax on line items if not provided
  - Support multiple tax types (VAT, GST, Sales Tax, etc.)

**Implementation:**
```python
# In form_recognizer.py
if "Tax" in document.fields:
    tax_amount = document.fields["Tax"].value
    extracted_data["tax_amount"] = float(tax_amount.amount) if tax_amount else None

if "SubTotal" in document.fields:
    subtotal = document.fields["SubTotal"].value
    extracted_data["subtotal"] = float(subtotal.amount) if subtotal else None

# Calculate tax rate
if extracted_data["subtotal"] and extracted_data["tax_amount"]:
    extracted_data["tax_rate"] = (extracted_data["tax_amount"] / extracted_data["subtotal"]) * 100
```

**Azure Fields:** `Tax`, `SubTotal`, `TotalTax`

---

### 3. **Discounts & Adjustments** 💰

**Current State:** Discounts are NOT extracted or compared.

**Enhancement Needed:**
- Extract discount fields:
  - Discount amount
  - Discount percentage
  - Discount reason/description
- Compare discounts between PO and Invoice
- Flag unexpected discounts as discrepancies
- Support line-item and document-level discounts

**Azure Fields:** May need custom extraction or layout model parsing

---

### 4. **Payment Terms & Due Dates** 📅

**Current State:** Dates are extracted but not compared.

**Enhancement Needed:**
- Extract `DueDate` from invoices
- Compare PO date, Invoice date, and Due date
- Calculate payment terms (e.g., "Net 30", "2/10 Net 30")
- Flag late invoices or payment term mismatches

**Azure Field:** `DueDate`

---

### 5. **Shipping & Handling Charges** 🚚

**Current State:** Not extracted.

**Enhancement Needed:**
- Extract shipping/handling charges
- Compare shipping costs between PO and Invoice
- Flag unexpected shipping charges
- Support multiple charge types (freight, handling, insurance)

**Azure Fields:** May need custom extraction

---

### 6. **Multi-Line Item Tax** 📋

**Current State:** Tax is only at document level.

**Enhancement Needed:**
- Extract tax per line item (if available)
- Compare line-item taxes
- Support tax-exempt items
- Handle different tax rates per item

---

### 7. **Payment Status Tracking** ✅

**Current State:** Not implemented.

**Enhancement Needed:**
- Track payment status (Unpaid, Partially Paid, Paid)
- Link to payment records
- Calculate outstanding amounts
- Support partial payments

---

### 8. **Approval Workflow** 🔄

**Current State:** No approval system.

**Enhancement Needed:**
- Approval workflow for discrepancies
- Escalation rules (e.g., >$1000 requires manager approval)
- Approval history tracking
- Email notifications for approvals

---

### 9. **Historical Comparison** 📈

**Current State:** Only current matching.

**Enhancement Needed:**
- Compare against historical invoices from same vendor
- Detect price trends
- Flag unusual price changes
- Vendor performance metrics

---

### 10. **Multi-Document Reconciliation** 📚

**Current State:** PO + Invoice + Delivery Note.

**Enhancement Needed:**
- Support additional document types:
  - Goods Receipt Notes (GRN)
  - Quality Inspection Reports
  - Credit Notes
  - Debit Notes
- Multi-way reconciliation (4-way, 5-way matching)

---

## Priority Recommendations

### **High Priority** (Immediate Business Value)

1. **Currency Support** - Critical for international vendors
2. **Tax Handling** - Essential for accurate reconciliation
3. **Payment Terms** - Important for cash flow management

### **Medium Priority** (Nice to Have)

4. **Discounts & Adjustments** - Common in business
5. **Shipping Charges** - Frequently varies
6. **Approval Workflow** - Improves process control

### **Low Priority** (Future Enhancements)

7. **Multi-Line Item Tax** - Less common
8. **Payment Status Tracking** - Can be separate system
9. **Historical Comparison** - Advanced analytics
10. **Multi-Document Reconciliation** - Complex feature

---

## Implementation Example: Tax & Currency

```python
# Enhanced ExtractedData model
class ExtractedData(Base):
    # ... existing fields ...
    currency_code = Column(String)  # "USD", "EUR", etc.
    subtotal = Column(Numeric(10, 2))
    tax_amount = Column(Numeric(10, 2))
    tax_rate = Column(Numeric(5, 2))  # Percentage
    discount_amount = Column(Numeric(10, 2))
    shipping_amount = Column(Numeric(10, 2))
    due_date = Column(DateTime)

# Enhanced Matching Service
def _compare_taxes(self, po_data, invoice_data):
    if po_data.tax_rate and invoice_data.tax_rate:
        if abs(po_data.tax_rate - invoice_data.tax_rate) > 0.1:  # 0.1% tolerance
            return {
                "type": "tax_rate_mismatch",
                "severity": "high",
                "po_tax_rate": po_data.tax_rate,
                "invoice_tax_rate": invoice_data.tax_rate,
                "message": f"Tax rate mismatch: PO={po_data.tax_rate}%, Invoice={invoice_data.tax_rate}%"
            }
    return None
```

---

## Summary

**Current System:** ✅ Solid foundation for basic 3-way matching (PO, Invoice, DN)

**Missing:** Currency, Taxes, Discounts, Payment Terms, Shipping Charges

**Recommendation:** Start with Currency and Tax support as they're most critical for accurate reconciliation.


