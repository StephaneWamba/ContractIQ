"""
Generate synthetic test PDFs for Invoice, PO, and Delivery Note testing.
Uses reportlab to create realistic-looking documents.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from datetime import datetime, timedelta
import random
from pathlib import Path

# Create assets directory if it doesn't exist
# Try multiple possible locations
possible_dirs = [
    Path(__file__).parent.parent.parent / "assets",  # From scripts/ directory
    Path("/app/assets"),  # Docker mount point
    Path.cwd() / "assets",  # Current working directory
]

ASSETS_DIR = None
for dir_path in possible_dirs:
    if dir_path.exists() or dir_path.parent.exists():
        ASSETS_DIR = dir_path
        break

if ASSETS_DIR is None:
    # Default to project root/assets
    ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def generate_invoice(invoice_number: str, po_number: str, vendor: str, output_path: Path):
    """Generate a synthetic invoice PDF."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
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
    items = [
        ['Item #', 'Description', 'Qty', 'Unit Price', 'Total'],
        ['001', 'Office Chairs - Ergonomic', '10', '$150.00', '$1,500.00'],
        ['002', 'Desk Lamps - LED', '5', '$45.00', '$225.00'],
        ['003', 'Monitor Stands', '8', '$75.00', '$600.00'],
    ]
    
    items_table = Table(items, colWidths=[0.8*inch, 3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
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
    
    # Totals - Use labels Azure Form Recognizer expects
    subtotal = 2325.00
    tax = subtotal * 0.08
    total = subtotal + tax
    
    totals_data = [
        ['Subtotal:', f'${subtotal:,.2f}'],
        ['Tax (8%):', f'${tax:,.2f}'],
        ['Amount Due:', f'${total:,.2f}'],  # Azure expects "Amount Due" not "Total"
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
    # Create a container table to right-align the totals
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
    story.append(Paragraph(f'Amount Due: ${total:,.2f}', amount_due_style))
    
    doc.build(story)


def generate_purchase_order(po_number: str, vendor: str, output_path: Path):
    """Generate a synthetic purchase order PDF."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
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
    
    # Header info
    header_data = [
        ['PO Number:', po_number, 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Ordered By:', 'ACME Corporation', 'Delivery Date:', (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')],
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
    vendor_para = Paragraph(
        f'<b>{vendor}</b><br/>123 Business St<br/>New York, NY 10001<br/>USA',
        styles['Normal']
    )
    ship_to_para = Paragraph(
        '<b>ACME Corporation</b><br/>456 Customer Ave<br/>Los Angeles, CA 90001<br/>USA',
        styles['Normal']
    )
    vendor_data = [
        ['Vendor:', vendor_para],
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
    items = [
        ['Item #', 'Description', 'Qty', 'Unit Price', 'Total'],
        ['001', 'Office Chairs - Ergonomic', '10', '$150.00', '$1,500.00'],
        ['002', 'Desk Lamps - LED', '5', '$45.00', '$225.00'],
        ['003', 'Monitor Stands', '8', '$75.00', '$600.00'],
    ]
    
    items_table = Table(items, colWidths=[0.8*inch, 3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
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
    
    # Totals - Use labels Azure Form Recognizer expects
    subtotal = 2325.00
    tax = subtotal * 0.08
    total = subtotal + tax
    
    totals_data = [
        ['Subtotal:', f'${subtotal:,.2f}'],
        ['Tax (8%):', f'${tax:,.2f}'],
        ['Amount Due:', f'${total:,.2f}'],  # Azure expects "Amount Due" not "Total"
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
    # Create a container table to right-align the totals
    container_table = Table([[totals_table]], colWidths=[7*inch])
    container_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(container_table)
    
    doc.build(story)


def generate_delivery_note(dn_number: str, po_number: str, vendor: str, output_path: Path):
    """Generate a synthetic delivery note PDF."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph("DELIVERY NOTE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header info
    header_data = [
        ['Delivery Note #:', dn_number, 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['PO Number:', po_number, 'Delivery Date:', datetime.now().strftime('%Y-%m-%d')],
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
    deliver_to_para = Paragraph(
        '<b>ACME Corporation</b><br/>456 Customer Ave<br/>Los Angeles, CA 90001<br/>USA',
        styles['Normal']
    )
    vendor_data = [
        ['From:', from_para],
        ['Deliver To:', deliver_to_para],
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
    
    # Line items (delivered quantities - may differ from PO)
    items = [
        ['Item #', 'Description', 'Qty Ordered', 'Qty Delivered', 'Status'],
        ['001', 'Office Chairs - Ergonomic', '10', '10', 'Complete'],
        ['002', 'Desk Lamps - LED', '5', '5', 'Complete'],
        ['003', 'Monitor Stands', '8', '7', 'Partial'],
    ]
    
    items_table = Table(items, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    
    doc.build(story)


def generate_invoice_variant(invoice_number: str, po_number: str, vendor: str, output_path: Path, items: list, total: float):
    """Generate invoice with custom items and total."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
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
            f"${item['price']:.2f}",
            f"${item['total']:.2f}",
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
    
    # Totals - Use labels Azure Form Recognizer expects
    subtotal = sum(item['total'] for item in items)
    tax = subtotal * 0.08
    final_total = subtotal + tax
    
    totals_data = [
        ['Subtotal:', f'${subtotal:,.2f}'],
        ['Tax (8%):', f'${tax:,.2f}'],
        ['Amount Due:', f'${final_total:,.2f}'],  # Azure expects "Amount Due" not "Total"
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
    story.append(Paragraph(f'Amount Due: ${final_total:,.2f}', amount_due_style))
    
    doc.build(story)


def generate_po_variant(po_number: str, vendor: str, output_path: Path, items: list):
    """Generate PO with custom items."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
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
    
    # Header info
    header_data = [
        ['PO Number:', po_number, 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Ordered By:', 'ACME Corporation', 'Delivery Date:', (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')],
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
    vendor_para = Paragraph(
        f'<b>{vendor}</b><br/>123 Business St<br/>New York, NY 10001<br/>USA',
        styles['Normal']
    )
    ship_to_para = Paragraph(
        '<b>ACME Corporation</b><br/>456 Customer Ave<br/>Los Angeles, CA 90001<br/>USA',
        styles['Normal']
    )
    vendor_data = [
        ['Vendor:', vendor_para],
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
            f"${item['price']:.2f}",
            f"${item['total']:.2f}",
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
    
    # Totals - Use labels Azure Form Recognizer expects
    subtotal = sum(item['total'] for item in items)
    tax = subtotal * 0.08
    final_total = subtotal + tax
    
    totals_data = [
        ['Subtotal:', f'${subtotal:,.2f}'],
        ['Tax (8%):', f'${tax:,.2f}'],
        ['Amount Due:', f'${final_total:,.2f}'],  # Azure expects "Amount Due" not "Total"
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


def generate_dn_variant(dn_number: str, po_number: str, vendor: str, output_path: Path, items: list):
    """Generate delivery note with custom items."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph("DELIVERY NOTE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header info
    header_data = [
        ['Delivery Note #:', dn_number, 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['PO Number:', po_number, 'Delivery Date:', datetime.now().strftime('%Y-%m-%d')],
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
    deliver_to_para = Paragraph(
        '<b>ACME Corporation</b><br/>456 Customer Ave<br/>Los Angeles, CA 90001<br/>USA',
        styles['Normal']
    )
    vendor_data = [
        ['From:', from_para],
        ['Deliver To:', deliver_to_para],
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
    table_data = [['Item #', 'Description', 'Qty Ordered', 'Qty Delivered', 'Status']]
    for item in items:
        status = 'Complete' if item['qty_delivered'] >= item['qty_ordered'] else 'Partial'
        table_data.append([
            item['item_num'],
            item['description'],
            str(item['qty_ordered']),
            str(item['qty_delivered']),
            status,
        ])
    
    items_table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    
    doc.build(story)


def main():
    """Generate all test PDFs with multiple scenarios."""
    print("Generating synthetic test PDFs...")
    
    # Scenario 1: Perfect Match (Original)
    print("\n[Scenario 1] Perfect Match Set")
    po_number_1 = "PO-2024-001"
    invoice_number_1 = "INV-2024-001"
    dn_number_1 = "DN-2024-001"
    vendor_1 = "CONTOSO LTD."
    
    generate_invoice(invoice_number_1, po_number_1, vendor_1, ASSETS_DIR / "test-invoice.pdf")
    print(f"[OK] Generated: test-invoice.pdf")
    
    generate_purchase_order(po_number_1, vendor_1, ASSETS_DIR / "test-po.pdf")
    print(f"[OK] Generated: test-po.pdf")
    
    generate_delivery_note(dn_number_1, po_number_1, vendor_1, ASSETS_DIR / "test-delivery-note.pdf")
    print(f"[OK] Generated: test-delivery-note.pdf")
    
    # Scenario 2: Quantity Mismatch
    print("\n[Scenario 2] Quantity Mismatch Set")
    po_number_2 = "PO-2024-002"
    invoice_number_2 = "INV-2024-002"
    dn_number_2 = "DN-2024-002"
    vendor_2 = "ACME SUPPLIERS"
    
    po_items_2 = [
        {'item_num': '001', 'description': 'Laptop Computers', 'qty': 5, 'price': 1200.00, 'total': 6000.00},
        {'item_num': '002', 'description': 'Wireless Keyboards', 'qty': 10, 'price': 75.00, 'total': 750.00},
        {'item_num': '003', 'description': 'USB-C Cables', 'qty': 20, 'price': 15.00, 'total': 300.00},
    ]
    
    invoice_items_2 = [
        {'item_num': '001', 'description': 'Laptop Computers', 'qty': 5, 'price': 1200.00, 'total': 6000.00},
        {'item_num': '002', 'description': 'Wireless Keyboards', 'qty': 10, 'price': 75.00, 'total': 750.00},
        {'item_num': '003', 'description': 'USB-C Cables', 'qty': 20, 'price': 15.00, 'total': 300.00},
    ]
    
    dn_items_2 = [
        {'item_num': '001', 'description': 'Laptop Computers', 'qty_ordered': 5, 'qty_delivered': 5},
        {'item_num': '002', 'description': 'Wireless Keyboards', 'qty_ordered': 10, 'qty_delivered': 8},  # Mismatch
        {'item_num': '003', 'description': 'USB-C Cables', 'qty_ordered': 20, 'qty_delivered': 18},  # Mismatch
    ]
    
    generate_po_variant(po_number_2, vendor_2, ASSETS_DIR / "test-po-002.pdf", po_items_2)
    print(f"[OK] Generated: test-po-002.pdf")
    
    generate_invoice_variant(invoice_number_2, po_number_2, vendor_2, ASSETS_DIR / "test-invoice-002.pdf", invoice_items_2, 0)
    print(f"[OK] Generated: test-invoice-002.pdf")
    
    generate_dn_variant(dn_number_2, po_number_2, vendor_2, ASSETS_DIR / "test-delivery-note-002.pdf", dn_items_2)
    print(f"[OK] Generated: test-delivery-note-002.pdf")
    
    # Scenario 3: Price Change
    print("\n[Scenario 3] Price Change Set")
    po_number_3 = "PO-2024-003"
    invoice_number_3 = "INV-2024-003"
    dn_number_3 = "DN-2024-003"
    vendor_3 = "TECH CORP"
    
    po_items_3 = [
        {'item_num': '001', 'description': 'Server Rack', 'qty': 2, 'price': 2500.00, 'total': 5000.00},
        {'item_num': '002', 'description': 'Network Switch', 'qty': 4, 'price': 450.00, 'total': 1800.00},
    ]
    
    invoice_items_3 = [
        {'item_num': '001', 'description': 'Server Rack', 'qty': 2, 'price': 2650.00, 'total': 5300.00},  # Price increased
        {'item_num': '002', 'description': 'Network Switch', 'qty': 4, 'price': 450.00, 'total': 1800.00},
    ]
    
    dn_items_3 = [
        {'item_num': '001', 'description': 'Server Rack', 'qty_ordered': 2, 'qty_delivered': 2},
        {'item_num': '002', 'description': 'Network Switch', 'qty_ordered': 4, 'qty_delivered': 4},
    ]
    
    generate_po_variant(po_number_3, vendor_3, ASSETS_DIR / "test-po-003.pdf", po_items_3)
    print(f"[OK] Generated: test-po-003.pdf")
    
    generate_invoice_variant(invoice_number_3, po_number_3, vendor_3, ASSETS_DIR / "test-invoice-003.pdf", invoice_items_3, 0)
    print(f"[OK] Generated: test-invoice-003.pdf")
    
    generate_dn_variant(dn_number_3, po_number_3, vendor_3, ASSETS_DIR / "test-delivery-note-003.pdf", dn_items_3)
    print(f"[OK] Generated: test-delivery-note-003.pdf")
    
    # Scenario 4: Missing Item
    print("\n[Scenario 4] Missing Item Set")
    po_number_4 = "PO-2024-004"
    invoice_number_4 = "INV-2024-004"
    dn_number_4 = "DN-2024-004"
    vendor_4 = "GLOBAL SUPPLIES"
    
    po_items_4 = [
        {'item_num': '001', 'description': 'Office Desk', 'qty': 10, 'price': 350.00, 'total': 3500.00},
        {'item_num': '002', 'description': 'Office Chair', 'qty': 10, 'price': 200.00, 'total': 2000.00},
        {'item_num': '003', 'description': 'Monitor', 'qty': 10, 'price': 300.00, 'total': 3000.00},
    ]
    
    invoice_items_4 = [
        {'item_num': '001', 'description': 'Office Desk', 'qty': 10, 'price': 350.00, 'total': 3500.00},
        {'item_num': '002', 'description': 'Office Chair', 'qty': 10, 'price': 200.00, 'total': 2000.00},
        # Item 003 missing in invoice
    ]
    
    dn_items_4 = [
        {'item_num': '001', 'description': 'Office Desk', 'qty_ordered': 10, 'qty_delivered': 10},
        {'item_num': '002', 'description': 'Office Chair', 'qty_ordered': 10, 'qty_delivered': 10},
        {'item_num': '003', 'description': 'Monitor', 'qty_ordered': 10, 'qty_delivered': 10},
    ]
    
    generate_po_variant(po_number_4, vendor_4, ASSETS_DIR / "test-po-004.pdf", po_items_4)
    print(f"[OK] Generated: test-po-004.pdf")
    
    generate_invoice_variant(invoice_number_4, po_number_4, vendor_4, ASSETS_DIR / "test-invoice-004.pdf", invoice_items_4, 0)
    print(f"[OK] Generated: test-invoice-004.pdf")
    
    generate_dn_variant(dn_number_4, po_number_4, vendor_4, ASSETS_DIR / "test-delivery-note-004.pdf", dn_items_4)
    print(f"[OK] Generated: test-delivery-note-004.pdf")
    
    # Scenario 5: Extra Item
    print("\n[Scenario 5] Extra Item Set")
    po_number_5 = "PO-2024-005"
    invoice_number_5 = "INV-2024-005"
    dn_number_5 = "DN-2024-005"
    vendor_5 = "PREMIUM VENDORS"
    
    po_items_5 = [
        {'item_num': '001', 'description': 'Projector', 'qty': 3, 'price': 800.00, 'total': 2400.00},
        {'item_num': '002', 'description': 'Projection Screen', 'qty': 3, 'price': 200.00, 'total': 600.00},
    ]
    
    invoice_items_5 = [
        {'item_num': '001', 'description': 'Projector', 'qty': 3, 'price': 800.00, 'total': 2400.00},
        {'item_num': '002', 'description': 'Projection Screen', 'qty': 3, 'price': 200.00, 'total': 600.00},
        {'item_num': '003', 'description': 'HDMI Cable', 'qty': 5, 'price': 25.00, 'total': 125.00},  # Extra item
    ]
    
    dn_items_5 = [
        {'item_num': '001', 'description': 'Projector', 'qty_ordered': 3, 'qty_delivered': 3},
        {'item_num': '002', 'description': 'Projection Screen', 'qty_ordered': 3, 'qty_delivered': 3},
    ]
    
    generate_po_variant(po_number_5, vendor_5, ASSETS_DIR / "test-po-005.pdf", po_items_5)
    print(f"[OK] Generated: test-po-005.pdf")
    
    generate_invoice_variant(invoice_number_5, po_number_5, vendor_5, ASSETS_DIR / "test-invoice-005.pdf", invoice_items_5, 0)
    print(f"[OK] Generated: test-invoice-005.pdf")
    
    generate_dn_variant(dn_number_5, po_number_5, vendor_5, ASSETS_DIR / "test-delivery-note-005.pdf", dn_items_5)
    print(f"[OK] Generated: test-delivery-note-005.pdf")
    
    print("\n" + "="*60)
    print("All test PDFs generated successfully!")
    print("="*60)
    print(f"\nLocation: {ASSETS_DIR}")
    print("\nGenerated Files:")
    print("  Scenario 1 (Perfect Match):")
    print("    - test-invoice.pdf")
    print("    - test-po.pdf")
    print("    - test-delivery-note.pdf")
    print("\n  Scenario 2 (Quantity Mismatch):")
    print("    - test-po-002.pdf")
    print("    - test-invoice-002.pdf")
    print("    - test-delivery-note-002.pdf")
    print("\n  Scenario 3 (Price Change):")
    print("    - test-po-003.pdf")
    print("    - test-invoice-003.pdf")
    print("    - test-delivery-note-003.pdf")
    print("\n  Scenario 4 (Missing Item):")
    print("    - test-po-004.pdf")
    print("    - test-invoice-004.pdf")
    print("    - test-delivery-note-004.pdf")
    print("\n  Scenario 5 (Extra Item):")
    print("    - test-po-005.pdf")
    print("    - test-invoice-005.pdf")
    print("    - test-delivery-note-005.pdf")


if __name__ == "__main__":
    main()

