"""
PDF generation service using ReportLab
Lightweight and fast for old hardware
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

def generate_invoice_pdf(invoice, business):
    """
    Generate PDF invoice
    Args:
        invoice: Invoice model instance (with line_items, customer)
        business: BusinessInfo model instance
    Returns:
        BytesIO buffer with PDF content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Title
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Business and Invoice Info (side by side)
    info_data = [
        [
            Paragraph(f"<b>{business.company_name}</b><br/>{business.address.replace(chr(10), '<br/>')}<br/>Phone: {business.phone}<br/>Email: {business.email}<br/>Tax ID: {business.tax_id}", normal_style),
            Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}<br/><b>Date:</b> {invoice.invoice_date.strftime('%Y-%m-%d')}<br/><b>Status:</b> {invoice.status.upper()}", normal_style)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[4*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer Info
    elements.append(Paragraph("<b>Bill To:</b>", heading_style))
    customer_text = f"{invoice.customer.name}<br/>{invoice.customer.address or ''}"
    if invoice.customer.phone:
        customer_text += f"<br/>Phone: {invoice.customer.phone}"
    if invoice.customer.email:
        customer_text += f"<br/>Email: {invoice.customer.email}"
    elements.append(Paragraph(customer_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Line Items Table
    elements.append(Paragraph("<b>Items:</b>", heading_style))
    
    # Table header
    line_items_data = [['Product', 'Part #', 'Qty', 'Unit Price', 'Total']]
    
    # Table rows
    for item in invoice.line_items:
        line_items_data.append([
            item.product_name,
            item.part_number or '-',
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.line_total:.2f}"
        ])
    
    # Totals
    line_items_data.append(['', '', '', 'Subtotal:', f"${invoice.subtotal:.2f}"])
    line_items_data.append(['', '', '', f'Tax ({invoice.tax_rate}%):', f"${invoice.tax_amount:.2f}"])
    line_items_data.append(['', '', '', 'Total:', f"${invoice.total:.2f}"])
    
    line_items_table = Table(line_items_data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1*inch])
    line_items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        # Body
        ('ALIGN', (2, 1), (2, -4), 'CENTER'),  # Quantity center
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Prices right
        ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -4), 9),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
        
        # Totals section
        ('FONTNAME', (3, -3), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (3, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (3, -1), (-1, -1), 2, colors.black),
    ]))
    elements.append(line_items_table)
    
    # Notes
    if invoice.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Notes:</b>", heading_style))
        elements.append(Paragraph(invoice.notes, normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
