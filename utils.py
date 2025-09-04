import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging

def generate_pdf_report(malpractice_log, counts, session_start, session_end):
    """Generate a PDF report of malpractice events"""
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"malpractice_report_{timestamp}.pdf"
    
    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=A4, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    # Title
    title = Paragraph("Student Malpractice Detection Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Session Information
    session_info = Paragraph("Session Information", heading_style)
    elements.append(session_info)
    
    session_data = [
        ['Session Start:', session_start if session_start else 'N/A'],
        ['Session End:', session_end if session_end else 'N/A'],
        ['Total Events Detected:', str(len(malpractice_log))],
        ['Report Generated:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    session_table = Table(session_data, colWidths=[2*inch, 3*inch])
    session_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(session_table)
    elements.append(Spacer(1, 12))
    
    # Detection Summary
    summary_heading = Paragraph("Detection Summary", heading_style)
    elements.append(summary_heading)
    
    summary_data = [
        ['Detection Type', 'Count', 'Percentage'],
        ['Hand Gestures', str(counts['hand_gestures']), 
         f"{(counts['hand_gestures']/max(len(malpractice_log), 1)*100):.1f}%"],
        ['Mobile Phone Usage', str(counts['mobile_phone']), 
         f"{(counts['mobile_phone']/max(len(malpractice_log), 1)*100):.1f}%"],
        ['Talking/Mouth Movement', str(counts['talking']), 
         f"{(counts['talking']/max(len(malpractice_log), 1)*100):.1f}%"],
        ['Total Events', str(len(malpractice_log)), '100.0%']
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))
    
    # Detailed Events Log
    if malpractice_log:
        events_heading = Paragraph("Detailed Events Log", heading_style)
        elements.append(events_heading)
        
        # Prepare events data
        events_data = [['Time', 'Detection Type', 'Confidence', 'Event #']]
        
        for idx, event in enumerate(malpractice_log, 1):
            timestamp_str = datetime.fromisoformat(event['timestamp']).strftime("%H:%M:%S")
            detection_type = event['type'].replace('_', ' ').title()
            confidence = f"{event['confidence']:.2f}" if 'confidence' in event else 'N/A'
            
            events_data.append([
                timestamp_str,
                detection_type,
                confidence,
                str(idx)
            ])
        
        events_table = Table(events_data, colWidths=[1.2*inch, 2*inch, 1*inch, 0.8*inch])
        events_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(events_table)
    else:
        no_events = Paragraph("No malpractice events detected during this session.", styles['Normal'])
        elements.append(no_events)
    
    elements.append(Spacer(1, 12))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    footer = Paragraph("Report generated by Student Malpractice Detection System", footer_style)
    elements.append(footer)
    
    # Build PDF
    try:
        doc.build(elements)
        logging.info(f"PDF report generated: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        raise

def format_detection_type(detection_type):
    """Format detection type for display"""
    type_mapping = {
        'hand_gestures': 'Hand Gestures',
        'mobile_phone': 'Mobile Phone Usage',
        'talking': 'Talking/Mouth Movement'
    }
    return type_mapping.get(detection_type, detection_type.replace('_', ' ').title())

def get_detection_color(detection_type):
    """Get color code for detection type"""
    color_mapping = {
        'hand_gestures': '#ff4757',  # Red
        'mobile_phone': '#3742fa',   # Blue
        'talking': '#ffa502'         # Orange
    }
    return color_mapping.get(detection_type, '#747d8c')  # Default gray

def calculate_session_stats(malpractice_log, session_start, session_end):
    """Calculate session statistics"""
    stats = {
        'total_events': len(malpractice_log),
        'events_per_minute': 0,
        'most_common_type': None,
        'avg_confidence': 0
    }
    
    if not malpractice_log:
        return stats
    
    # Calculate events per minute
    if session_start and session_end:
        start_time = datetime.fromisoformat(session_start)
        end_time = datetime.fromisoformat(session_end)
        duration_minutes = (end_time - start_time).total_seconds() / 60
        if duration_minutes > 0:
            stats['events_per_minute'] = len(malpractice_log) / duration_minutes
    
    # Find most common detection type
    type_counts = {}
    total_confidence = 0
    
    for event in malpractice_log:
        detection_type = event['type']
        type_counts[detection_type] = type_counts.get(detection_type, 0) + 1
        if 'confidence' in event:
            total_confidence += event['confidence']
    
    if type_counts:
        stats['most_common_type'] = max(type_counts, key=type_counts.get)
    
    # Calculate average confidence
    if malpractice_log:
        stats['avg_confidence'] = total_confidence / len(malpractice_log)
    
    return stats
