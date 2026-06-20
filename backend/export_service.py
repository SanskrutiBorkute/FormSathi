import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(form_name, form_category, submission_date, fields):
    buffer = io.BytesIO()
    # 36 pt margin leaves 540 pt of printable width on a standard 612x792 letter size page
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#008080') # Teal
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#555555')
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#004D4D'),
        spaceAfter=12,
        spaceBefore=10
    )
    
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#333333')
    )
    
    cell_bold_style = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#111111')
    )
    
    story = []
    
    # Title & Header banner
    story.append(Paragraph("FormSathi Universal Form Report", title_style))
    story.append(Spacer(1, 4))
    
    meta_text = (
        f"<b>Form Name:</b> {form_name} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Category:</b> {form_category} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Submission Date:</b> {submission_date}"
    )
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 15))
    
    # Fields Section
    story.append(Paragraph("Extracted Fields & Validation Results", header_style))
    
    # Setup Table Data
    table_data = [[
        Paragraph("<b>Field Label</b>", cell_bold_style),
        Paragraph("<b>Extracted Value</b>", cell_bold_style),
        Paragraph("<b>Status</b>", cell_bold_style),
        Paragraph("<b>Validation Message</b>", cell_bold_style)
    ]]
    
    for f in fields:
        label = f.get('expanded_label', f.get('label', ''))
        value = f.get('current_value', '') or ''
        status = f.get('status', 'todo').upper()
        
        # Load messages from validation json cache
        val_json = f.get('validation_json')
        val_msgs = []
        if val_json:
            try:
                v_data = json.loads(val_json)
                val_msgs = v_data.get('messages', [])
            except Exception:
                pass
                
        if not val_msgs:
            if f.get('error_message'):
                val_msgs = [f['error_message']]
            else:
                val_msgs = ["Valid input" if status == 'DONE' else "Pending input"]
                
        val_msg = " · ".join(val_msgs)
        
        # Format colored status label
        if status == 'DONE':
            status_html = '<font color="#2E7D32"><b>✓ VALID</b></font>'
        elif status == 'ERROR':
            status_html = '<font color="#C62828"><b>✖ INVALID</b></font>'
        else:
            status_html = '<font color="#EF6C00"><b>⚠ REVIEW</b></font>'
            
        table_data.append([
            Paragraph(label, cell_bold_style),
            Paragraph(value, cell_style),
            Paragraph(status_html, cell_style),
            Paragraph(val_msg, cell_style)
        ])
        
    # Table Width Mapping (Total = 540)
    # Label: 120, Value: 140, Status: 70, Messages: 210
    t = Table(table_data, colWidths=[120, 140, 70, 210])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F2F8F8')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D5E5E5')),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_json_report(form_name, form_category, submission_date, fields):
    fields_list = []
    for f in fields:
        val_json = f.get('validation_json')
        val_data = {}
        if val_json:
            try:
                val_data = json.loads(val_json)
            except Exception:
                pass
        
        fields_list.append({
            "label": f.get('expanded_label', f.get('label', '')),
            "value": f.get('current_value', '') or '',
            "is_required": bool(f.get('is_required')),
            "ocr_confidence": f.get('ocr_confidence'),
            "status": f.get('status', 'todo'),
            "error_message": f.get('error_message'),
            "validation_score": f.get('validation_score'),
            "validation_messages": val_data.get('messages', [])
        })
        
    return {
        "form_name": form_name,
        "form_category": form_category,
        "submission_date": submission_date,
        "total_fields": len(fields),
        "fields": fields_list
    }
