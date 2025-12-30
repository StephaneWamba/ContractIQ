"""
Generate additional test PDF sets with diverse scenarios including:
- Multi-currency scenarios (USD, EUR, GBP)
- Different tax rates (0%, 8%, 10%, 20% VAT)
- Complex matching scenarios
- Edge cases
"""
from pathlib import Path
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT

# Create additional test sets directory
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets" / "additional-test-sets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def generate_invoice_with_currency(
    invoice_number: str, po_number: str, vendor: str, output_path: Path,
    items: list, currency_code: str = "USD", tax_rate: float = 0.08
):
    """Generate invoice with specific currency and tax rate."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Currency symbol mapping
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
    }
    symbol = currency_symbols.get(currency_code, currency_code)
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header info
    header_data = [
        ['Invoice Number:', invoice_number, 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['PO Number:', po_number, 'Due Date:', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')],
        ['Currency:', currency_code, 'Payment Terms:', 'Net 30'],
    ]
    header_table = Table(header_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Vendor and Bill To
    from_para = Paragraph(
        f'<b>{vendor}</b><br/>123 Business St<br/>New York, NY 10001<br/>USA',
        styles['Normal']
    )
    bill_to_para = Paragraph(
        '<b>ACME Corporation</b><br/>456 Customer Ave<br/>Los Angeles, CA 90001<br/>USA',
        styles['Normal']
    )
    vendor_data = [
        ['From:', from_para],
        ['Bill To:', bill_to_para],
    ]
    vendor_table = Table(vendor_data, colWidths=[1*inch, 6*inch])
    vendor_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(vendor_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Line items
    table_data = [['Item #', 'Description', 'Qty', 'Unit Price', 'Total']]
    for item in items:
        table_data.append([
            item['item_num'],
            item['description'],
            str(item['qty']),
            f"{symbol}{item['price']:.2f}",
            f"{symbol}{item['total']:.2f}",
        ])
    
    items_table = Table(table_data, colWidths=[0.8*inch, 3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Totals
    subtotal = sum(item['total'] for item in items)
    tax = subtotal * tax_rate
    final_total = subtotal + tax
    
    totals_data = [
        ['Subtotal:', f'{symbol}{subtotal:,.2f}'],
        [f'Tax ({tax_rate*100:.0f}%):', f'{symbol}{tax:,.2f}'],
        ['Amount Due:', f'{symbol}{final_total:,.2f}'],
    ]
    totals_table = Table(totals_data, colWidths=[1*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1a1a1a')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    container_table = Table([[totals_table]], colWidths=[7*inch])
    container_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(container_table)
    
    # Add Amount Due as standalone text for better Azure recognition
    story.append(Spacer(1, 0.1*inch))
    amount_due_style = ParagraphStyle(
        'AmountDue',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=2,  # Right align
        textColor=colors.HexColor('#1a1a1a'),
    )
    story.append(Paragraph(f'Amount Due: {symbol}{final_total:,.2f}', amount_due_style))
    
    doc.build(story)


def generate_po_with_currency(
    po_number: str, vendor: str, output_path: Path, items: list, currency_code: str = "USD", tax_rate: float = 0.08
):
    """Generate PO with specific currency and tax rate."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
    }
    symbol = currency_symbols.get(currency_code, currency_code)
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph("PURCHASE ORDER", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header
    header_data = [
        ['PO Number:', po_number, 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Currency:', currency_code, 'Expected Delivery:', (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')],
    ]
    header_table = Table(header_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Vendor and Ship To
    from_para = Paragraph(
        f'<b>{vendor}</b><br/>123 Business St<br/>New York, NY 10001<br/>USA',
        styles['Normal']
    )
    ship_to_para = Paragraph(
        '<b>ACME Corporation</b><br/>456 Customer Ave<br/>Los Angeles, CA 90001<br/>USA',
        styles['Normal']
    )
    vendor_data = [
        ['Vendor:', from_para],
        ['Ship To:', ship_to_para],
    ]
    vendor_table = Table(vendor_data, colWidths=[1*inch, 6*inch])
    vendor_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(vendor_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Line items
    table_data = [['Item #', 'Description', 'Qty', 'Unit Price', 'Total']]
    for item in items:
        table_data.append([
            item['item_num'],
            item['description'],
            str(item['qty']),
            f"{symbol}{item['price']:.2f}",
            f"{symbol}{item['total']:.2f}",
        ])
    
    items_table = Table(table_data, colWidths=[0.8*inch, 3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Totals
    subtotal = sum(item['total'] for item in items)
    tax = subtotal * tax_rate
    final_total = subtotal + tax
    
    totals_data = [
        ['Subtotal:', f'{symbol}{subtotal:,.2f}'],
        [f'Tax ({tax_rate*100:.0f}%):', f'{symbol}{tax:,.2f}'],
        ['Total:', f'{symbol}{final_total:,.2f}'],
    ]
    totals_table = Table(totals_data, colWidths=[1*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1a1a1a')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    container_table = Table([[totals_table]], colWidths=[7*inch])
    container_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(container_table)
    
    doc.build(story)


def main():
    """Generate additional test PDF sets."""
    print("Generating additional test PDF sets...")
    print(f"Output directory: {ASSETS_DIR}\n")
    
    # Set 1: Multi-Currency Scenarios
    print("[Set 1] Multi-Currency Scenarios")
    currencies = [
        ("USD", "$", 0.08),
        ("EUR", "€", 0.20),  # 20% VAT
        ("GBP", "£", 0.20),  # 20% VAT
    ]
    
    for idx, (currency, symbol, tax_rate) in enumerate(currencies, 1):
        po_number = f"PO-2024-MC-{idx:03d}"
        invoice_number = f"INV-2024-MC-{idx:03d}"
        vendor = f"INTERNATIONAL VENDOR {currency}"
        
        items = [
            {'item_num': '001', 'description': f'Product A ({currency})', 'qty': 10, 'price': 100.0, 'total': 1000.0},
            {'item_num': '002', 'description': f'Product B ({currency})', 'qty': 5, 'price': 200.0, 'total': 1000.0},
        ]
        
        generate_po_with_currency(
            po_number, vendor, ASSETS_DIR / f"po-currency-{currency.lower()}.pdf",
            items, currency, tax_rate
        )
        print(f"  [OK] Generated: po-currency-{currency.lower()}.pdf")
        
        generate_invoice_with_currency(
            invoice_number, po_number, vendor, ASSETS_DIR / f"invoice-currency-{currency.lower()}.pdf",
            items, currency, tax_rate
        )
        print(f"  [OK] Generated: invoice-currency-{currency.lower()}.pdf")
    
    # Set 2: Different Tax Rates
    print("\n[Set 2] Different Tax Rates")
    tax_scenarios = [
        (0.0, "NO_TAX"),
        (0.08, "STANDARD"),
        (0.10, "HIGH"),
        (0.20, "VAT"),
    ]
    
    for idx, (tax_rate, label) in enumerate(tax_scenarios, 1):
        po_number = f"PO-2024-TAX-{idx:03d}"
        invoice_number = f"INV-2024-TAX-{idx:03d}"
        vendor = f"TAX VENDOR {label}"
        
        items = [
            {'item_num': '001', 'description': 'Standard Item', 'qty': 20, 'price': 50.0, 'total': 1000.0},
            {'item_num': '002', 'description': 'Premium Item', 'qty': 10, 'price': 100.0, 'total': 1000.0},
        ]
        
        generate_po_with_currency(
            po_number, vendor, ASSETS_DIR / f"po-tax-{label.lower()}.pdf",
            items, "USD", tax_rate
        )
        print(f"  [OK] Generated: po-tax-{label.lower()}.pdf")
        
        generate_invoice_with_currency(
            invoice_number, po_number, vendor, ASSETS_DIR / f"invoice-tax-{label.lower()}.pdf",
            items, "USD", tax_rate
        )
        print(f"  [OK] Generated: invoice-tax-{label.lower()}.pdf")
    
    # Set 3: Tax Rate Mismatch (PO 8%, Invoice 10%)
    print("\n[Set 3] Tax Rate Mismatch")
    po_number = "PO-2024-TAX-MISMATCH"
    invoice_number = "INV-2024-TAX-MISMATCH"
    vendor = "TAX MISMATCH VENDOR"
    
    items = [
        {'item_num': '001', 'description': 'Item A', 'qty': 15, 'price': 80.0, 'total': 1200.0},
        {'item_num': '002', 'description': 'Item B', 'qty': 8, 'price': 150.0, 'total': 1200.0},
    ]
    
    generate_po_with_currency(
        po_number, vendor, ASSETS_DIR / "po-tax-mismatch.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: po-tax-mismatch.pdf")
    
    generate_invoice_with_currency(
        invoice_number, po_number, vendor, ASSETS_DIR / "invoice-tax-mismatch.pdf",
        items, "USD", 0.10  # Different tax rate
    )
    print(f"  [OK] Generated: invoice-tax-mismatch.pdf")
    
    # Set 4: Currency Mismatch (PO USD, Invoice EUR)
    print("\n[Set 4] Currency Mismatch")
    po_number = "PO-2024-CURRENCY-MISMATCH"
    invoice_number = "INV-2024-CURRENCY-MISMATCH"
    vendor = "CURRENCY MISMATCH VENDOR"
    
    items = [
        {'item_num': '001', 'description': 'International Item', 'qty': 12, 'price': 100.0, 'total': 1200.0},
    ]
    
    generate_po_with_currency(
        po_number, vendor, ASSETS_DIR / "po-currency-mismatch.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: po-currency-mismatch.pdf")
    
    generate_invoice_with_currency(
        invoice_number, po_number, vendor, ASSETS_DIR / "invoice-currency-mismatch.pdf",
        items, "EUR", 0.20  # Different currency
    )
    print(f"  [OK] Generated: invoice-currency-mismatch.pdf")
    
    # Set 5: Large Quantities
    print("\n[Set 5] Large Quantities")
    po_number = "PO-2024-LARGE"
    invoice_number = "INV-2024-LARGE"
    vendor = "BULK VENDOR"
    
    items = [
        {'item_num': '001', 'description': 'Bulk Item A', 'qty': 1000, 'price': 5.0, 'total': 5000.0},
        {'item_num': '002', 'description': 'Bulk Item B', 'qty': 500, 'price': 10.0, 'total': 5000.0},
        {'item_num': '003', 'description': 'Bulk Item C', 'qty': 250, 'price': 20.0, 'total': 5000.0},
    ]
    
    generate_po_with_currency(
        po_number, vendor, ASSETS_DIR / "po-large-quantities.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: po-large-quantities.pdf")
    
    generate_invoice_with_currency(
        invoice_number, po_number, vendor, ASSETS_DIR / "invoice-large-quantities.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: invoice-large-quantities.pdf")
    
    # Set 6: High-Value Items
    print("\n[Set 6] High-Value Items")
    po_number = "PO-2024-HIGH-VALUE"
    invoice_number = "INV-2024-HIGH-VALUE"
    vendor = "LUXURY VENDOR"
    
    items = [
        {'item_num': '001', 'description': 'Premium Equipment', 'qty': 2, 'price': 50000.0, 'total': 100000.0},
        {'item_num': '002', 'description': 'Professional Service', 'qty': 1, 'price': 25000.0, 'total': 25000.0},
    ]
    
    generate_po_with_currency(
        po_number, vendor, ASSETS_DIR / "po-high-value.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: po-high-value.pdf")
    
    generate_invoice_with_currency(
        invoice_number, po_number, vendor, ASSETS_DIR / "invoice-high-value.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: invoice-high-value.pdf")
    
    # Set 7: Many Line Items
    print("\n[Set 7] Many Line Items")
    po_number = "PO-2024-MANY-ITEMS"
    invoice_number = "INV-2024-MANY-ITEMS"
    vendor = "DETAILED VENDOR"
    
    items = [
        {'item_num': f'{i:03d}', 'description': f'Item {i}', 'qty': i, 'price': 10.0 * i, 'total': 10.0 * i * i}
        for i in range(1, 16)  # 15 items
    ]
    
    generate_po_with_currency(
        po_number, vendor, ASSETS_DIR / "po-many-items.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: po-many-items.pdf")
    
    generate_invoice_with_currency(
        invoice_number, po_number, vendor, ASSETS_DIR / "invoice-many-items.pdf",
        items, "USD", 0.08
    )
    print(f"  [OK] Generated: invoice-many-items.pdf")
    
    print("\n" + "="*60)
    print("All additional test PDFs generated successfully!")
    print("="*60)
    print(f"\nLocation: {ASSETS_DIR}")
    print(f"\nTotal files generated: {len(list(ASSETS_DIR.glob('*.pdf')))}")


if __name__ == "__main__":
    main()


