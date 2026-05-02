"""
PDF generation service using ReportLab
Matches the Auto Parts invoice format from sample-images/with-logo.png
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import os

def generate_invoice_pdf(invoice, business):
    """
    Generate PDF invoice matching Auto Parts Corp format
    Args:
        invoice: Invoice model instance (with items, customer)
        business: BusinessInfo model instance
    Returns:
        BytesIO buffer with PDF content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=0.5*inch, 
        leftMargin=0.5*inch, 
        topMargin=0.5*inch, 
        bottomMargin=0.5*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=colors.black
    )
    
    header_info_style = ParagraphStyle(
        'HeaderInfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_LEFT
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitleStyle',
        parent=styles['Heading1'],
        fontSize=28,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        alignment=TA_RIGHT,
        spaceAfter=20
    )
    
    # Header Layout - Logo on left, Company info in center, Invoice details on right
    header_data = []
    
    # Logo path - use synk-auto-parts.jpg from frontend/media
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend', 'media', 'synk-auto-parts.jpg')
    logo_cell = ""
    if os.path.exists(logo_path):
        # Create image with proper sizing
        logo = Image(logo_path, width=1.2*inch, height=0.8*inch)
        logo_cell = logo
    
    # Company info (center)
    company_info = Paragraph(f"""
        <b>{business.company_name}</b><br/>
        {business.address.replace(chr(10), '<br/>')}<br/>
        HST: {business.tax_id or 'N/A'}<br/>
        Phone: {business.phone}
    """, header_info_style)
    
    # Right side info
    right_info = Paragraph(f"""
        PAGE NO: 1<br/>
        SHIP NO: {invoice.invoice_number}<br/>
        TERMS: {invoice.payment_terms or 'COD CASH ONLY'}<br/>
        DATE: {invoice.date.strftime('%Y-%m-%d')}<br/>
        SALESPERSON: {invoice.salesperson or '-'}<br/>
        REFERENCE: {invoice.reference or ''}
    """, header_info_style)
    
    header_data = [[logo_cell, company_info, right_info]]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 3*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Logo left
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),   # Company center-left
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),  # Info right
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # SOLD TO section and INVOICE number
    sold_to_data = [
        [
            Paragraph(f"<b>SOLD TO:</b><br/>{invoice.customer.name}", header_info_style),
            Paragraph(f"<b>INVOICE: {invoice.invoice_number}</b>", invoice_title_style)
        ]
    ]
    
    sold_to_table = Table(sold_to_data, colWidths=[4*inch, 3.5*inch])
    sold_to_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(sold_to_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Line Items Table - matching the exact column structure
    line_items_data = [
        ['LINES', 'PART NUMBERS', 'ORDERED SHIPPED', 'B/O', 'SUGG', 'NET', 'NET CODE EXT. AMOUNT']
    ]
    
    # Add line items
    for i, item in enumerate(invoice.items, 1):
        line_items_data.append([
            str(i),  # Line number
            item.description,  # Part description
            f"{int(item.quantity)} {int(item.quantity)}",  # Ordered/Shipped
            '',  # B/O (Backorder)
            f"${item.unit_price:.2f}",  # SUGG (Suggested price)
            f"${item.unit_price:.2f}",  # NET (Net price)
            f"${item.total:.2f}"  # Extended amount
        ])
    
    # Add empty rows to match the template
    while len(line_items_data) < 16:  # 15 rows + header
        line_items_data.append(['', '', '', '', '', '', ''])
    
    line_items_table = Table(
        line_items_data, 
        colWidths=[0.5*inch, 2*inch, 1.2*inch, 0.5*inch, 0.8*inch, 0.8*inch, 1.2*inch]
    )
    
    line_items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        # All cells
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Line numbers center
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Numbers center
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(line_items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Bottom totals section - exactly matching the layout
    totals_data = [
        [
            # Left side - Taxable breakdown
            Paragraph(f"TAXABLE: {invoice.subtotal:.2f}<br/>NON-TAXABLE: 0.00", header_info_style),
            
            # Right side - Totals
            Paragraph(f"""
                SUB TOTAL:<br/>
                SUBTOTAL:<br/>
                TAX AMOUNT:<br/>
                <b>TOTAL:</b>
            """, header_info_style),
            
            # Amounts column
            Paragraph(f"""
                {invoice.subtotal:.2f}<br/>
                {invoice.subtotal:.2f}<br/>
                {invoice.tax_amount:.2f}<br/>
                <b>{invoice.total:.2f}</b>
            """, ParagraphStyle('AmountsStyle', parent=header_info_style, alignment=TA_RIGHT))
        ]
    ]
    
    totals_table = Table(totals_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    totals_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Footer message
    footer_msg = Paragraph(
        "<b>** AMOUNT CHARGED TO STORE ACCOUNT **</b>", 
        ParagraphStyle('FooterStyle', parent=header_info_style, alignment=TA_CENTER, fontSize=10)
    )
    elements.append(footer_msg)
    
    # Notes (if any)
    if invoice.notes:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", header_info_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer