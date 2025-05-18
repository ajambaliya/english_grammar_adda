import io
import datetime
import math
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

def get_correct_option_index(answer_key):
    option_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    return option_mapping.get(answer_key.lower(), None)

def generate_modern_pdf(questions):
    """Generate a beautiful modern PDF with all quiz questions and answers"""
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()
    elements = []
    
    # Define custom colors
    primary_color = HexColor("#3498db")  # Blue
    accent_color = HexColor("#e74c3c")   # Red
    text_color = HexColor("#2c3e50")     # Dark blue/gray
    success_color = HexColor("#2ecc71")  # Green
    light_bg = HexColor("#ecf0f1")       # Light gray
    
    # Define custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=primary_color,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=primary_color,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        textColor=text_color,
        leading=20
    )
    
    option_style = ParagraphStyle(
        'OptionStyle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica',
        leftIndent=20,
        textColor=text_color,
        leading=16
    )
    
    correct_option_style = ParagraphStyle(
        'CorrectOptionStyle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        leftIndent=20,
        textColor=success_color,
        leading=16
    )
    
    explanation_style = ParagraphStyle(
        'ExplanationStyle',
        parent=styles['Italic'],
        fontSize=11,
        fontName='Helvetica-Oblique',
        leftIndent=15,
        textColor=text_color,
        borderWidth=1,
        borderColor=light_bg,
        borderPadding=8,
        backColor=light_bg,
        spaceAfter=15,
        leading=14
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica',
        textColor=text_color,
        leading=16
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Oblique',
        textColor=text_color,
        alignment=TA_CENTER
    )
    
    promo_style = ParagraphStyle(
        'PromoStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=accent_color,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    # Add title with date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"✨ English Grammar Adda ✨<br/>Quiz Compilation", title_style))
    elements.append(Paragraph(f"📅 {current_date}", ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        textColor=text_color
    )))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add channel promotion with attractive styling
    promo_text = [
        ["📱 Join Our Telegram Channel 📱"],
        ["@English_grammar_adda"],
        ["https://t.me/english_grammar_adda"]
    ]
    
    t = Table(promo_text, colWidths=[5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('BACKGROUND', (0, 1), (0, 2), light_bg),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, 1), 14),
        ('FONTNAME', (0, 2), (0, 2), 'Helvetica'),
        ('FONTSIZE', (0, 2), (0, 2), 12),
        ('BOTTOMPADDING', (0, 2), (0, 2), 10),
        ('BOX', (0, 0), (-1, -1), 1, primary_color),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add introduction
    intro_text = """<b>📚 About This PDF:</b> This document contains all questions from our latest Telegram quiz with correct answers and detailed explanations. Use it to improve your English grammar skills and prepare for exams.

<b>🔒 Copyright Notice:</b> This content is exclusive to English Grammar Adda. No part of this document may be reproduced without permission. Share the channel link instead!

<b>📈 Daily Practice:</b> Visit our channel daily for new quizzes, tips, and resources to continuously improve your English proficiency."""
    
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add Quiz header
    elements.append(Paragraph("📝 Quiz Questions & Answers", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add each question with modern styling
    for i, q in enumerate(questions):
        # Question box
        question_box = [
            [f"Question {i+1}: {q['Question']}"]
        ]
        
        t = Table(question_box, colWidths=[6.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.1*inch))
        
        # Options
        options = [q['Option A'], q['Option B'], q['Option C'], q['Option D']]
        correct_option_index = get_correct_option_index(q['Answer'])
        
        for j, option in enumerate(options):
            option_letter = chr(65+j)  # A, B, C, D
            option_text = f"{option_letter}) {option}"
            
            if j == correct_option_index:
                option_row = [[f"✓ {option_text}"]]
                t = Table(option_row, colWidths=[6.3*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), success_color.clone(alpha=0.2)),
                    ('TEXTCOLOR', (0, 0), (-1, -1), text_color),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
            else:
                option_row = [[option_text]]
                t = Table(option_row, colWidths=[6.3*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), light_bg.clone(alpha=0.3)),
                    ('TEXTCOLOR', (0, 0), (-1, -1), text_color),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
            elements.append(t)
        
        # Explanation
        explanation = q.get('Explanation', "No explanation provided")
        if explanation and not (isinstance(explanation, float) and math.isnan(explanation)):
            explanation_row = [[f"💡 Explanation: {explanation}"]]
            t = Table(explanation_row, colWidths=[6.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), light_bg),
                ('TEXTCOLOR', (0, 0), (-1, -1), text_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Oblique'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(t)
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Add final promotion
    elements.append(Paragraph("📱 Stay Connected With Us 📱", subtitle_style))
    
    promo_final = [
        ["👉 Join our Telegram channel: @English_grammar_adda"],
        ["👉 Daily quizzes, tips & learning resources"],
        ["👉 Improve your English grammar skills every day!"],
        ["👉 Share with friends who want to improve their English"]
    ]
    
    t = Table(promo_final, colWidths=[6.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, primary_color),
    ]))
    elements.append(t)
    
    # Add copyright footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("© English Grammar Adda | Created with ❤️ to help you master English", footer_style))
    elements.append(Paragraph("All rights reserved. This document is for personal use only.", footer_style))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer 