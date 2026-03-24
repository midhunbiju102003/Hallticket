from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
import os

def create_hall_ticket_pdf(hall_ticket, all_tickets=None):
    """Generate Hall Ticket PDF with potential timetable of multiple exams"""
    if all_tickets is None:
        all_tickets = [hall_ticket]
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*cm, leftMargin=0.5*cm, topMargin=0.5*cm, bottomMargin=0.5*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceBefore=10,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        lineHeight=14,
    )
    
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#444444'),
        lineHeight=12,
    )
    
    student = hall_ticket.student
    
    # Header
    elements.append(Paragraph("EXAMINATION HALL TICKET", title_style))
    elements.append(Paragraph("<b>CampusEntry Academic Services</b>", ParagraphStyle('InstName', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER)))
    elements.append(Spacer(1, 0.4*cm))
    
    # Student Info Table (Side by side with Photo placeholder)
    elements.append(Paragraph("STUDENT INFORMATION", heading_style))
    
    student_info = [
        ['Roll Number:', student.roll_number, 'Batch:', student.batch],
        ['Name:', student.name, 'Branch:', student.branch],
        ['Email:', student.email, 'Gender:', dict(student.GENDER_CHOICES).get(student.gender, student.gender)],
    ]
    
    st_table = Table(student_info, colWidths=[2.8*cm, 6.5*cm, 2.5*cm, 4*cm])
    st_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(st_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Exams Timetable Section
    elements.append(Paragraph("EXAMINATION TIMETABLE", heading_style))
    
    # Table header
    table_data = [['Subject Code', 'Subject Name', 'Date', 'Time', 'Room', 'Seat']]
    
    # Add all exams
    for t in sorted(all_tickets, key=lambda x: (x.exam.date, x.exam.start_time)):
        ex = t.exam
        table_data.append([
            ex.subject_code,
            ex.subject_name,
            ex.date.strftime('%d-%m-%Y'),
            f"{ex.start_time.strftime('%I:%M %p')} - {ex.end_time.strftime('%I:%M %p')}",
            ex.room_number,
            t.seat_assigned or 'N/A'
        ])
    
    timetable = Table(table_data, colWidths=[2.5*cm, 5.5*cm, 2.5*cm, 4*cm, 2*cm, 1.5*cm])
    timetable.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'), # Left align subject names
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(timetable)
    elements.append(Spacer(1, 0.8*cm))
    
    # QR and Verification
    # For unified tickets, we can show the QR of the main ticket requested or just the first one
    v_data = [
        [
            Paragraph("<b>Security & Verification Center</b><br/><br/>This Master QR Code is your unique digital identity. Scan this code at any examination venue entrance. The invigilator's terminal will automatically verify your enrollment for the specific session and mark your attendance.<br/><br/><i>Keep this code clear and undamaged for high-speed scanning.</i>", small_style),
            Image(hall_ticket.qr_code.path, width=4.5*cm, height=4.5*cm) if hall_ticket.qr_code else "[No QR]"
        ]
    ]
    
    v_table = Table(v_data, colWidths=[11.5*cm, 4.5*cm])
    v_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(v_table)
    
    elements.append(Spacer(1, 1*cm))
    
    # Instructions & Signatures
    elements.append(Paragraph("IMPORTANT INSTRUCTIONS", heading_style))
    inst_text = """
    1. Arrive at the examination center at least 30 minutes before the scheduled start time.<br/>
    2. Carrying original ID Proof and this Hall Ticket is mandatory for entry.<br/>
    3. Mobile phones, smartwatches, and unauthorized electronics are strictly prohibited.<br/>
    4. Maintain the allotted seating arrangement for the entire duration of the exam.
    """
    elements.append(Paragraph(inst_text, small_style))
    
    elements.append(Spacer(1, 1.5*cm))
    
    # Signatures
    sig_data = [
        ['Student Signature', '', 'Controller of Examinations'],
        ['', '', ''],
        ['_____________________', '', '_____________________'],
    ]
    sig_table = Table(sig_data, colWidths=[6*cm, 6*cm, 6*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    elements.append(sig_table)
    
    # Build
    doc.build(elements)
    buffer.seek(0)
    return buffer
