import os
import asyncio
import math
import random
import datetime
import json
import io
from fpdf import FPDF
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Fetch sensitive information from environment variables
mongo_uri = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME')

# Initialize MongoDB client and Telegram bot
client = MongoClient(mongo_uri)
bot = Bot(token=BOT_TOKEN)

# Store questions for later PDF generation
current_quiz_questions = []

# Motivational messages to display before quiz
MOTIVATIONAL_MESSAGES = [
    "🌟 Time to boost your English skills! Ready for today's grammar challenge?",
    "📚 Knowledge is power! Let's strengthen your grammar with today's quiz!",
    "💡 The more you practice, the better you become. Let's test your grammar knowledge!",
    "🚀 Improve your English one question at a time. Today's quiz coming up!",
    "🎯 Daily practice makes perfect! Here's your English grammar challenge for today!",
    "🧠 Exercise your brain with today's English grammar quiz!",
    "✨ Great English skills open new doors! Ready to level up?",
    "📝 Let's see how much you've improved with today's grammar quiz!",
    "🔍 Attention to detail is key in mastering English grammar. Ready to test yours?",
    "🌈 Each quiz brings you one step closer to English fluency!"
]

# Feedback messages to display after quiz
FEEDBACK_MESSAGES = [
    "How did you find today's quiz? React with 👍 if you enjoyed it!",
    "Did you learn something new today? Share with friends if you found it helpful!",
    "Rate our quiz by reacting with ❤️ if you loved it!",
    "Was this quiz helpful? Let us know with your reactions!",
    "Don't forget to share your score in the comments! How many did you get right?",
    "We'd love to hear your thoughts! React or comment on how we can improve.",
    "Found this quiz useful? React with 🌟 and share with friends who might benefit!",
    "Learning is a journey we take together. How was today's English grammar lesson?",
    "Your feedback helps us create better content! Rate today's quiz with reactions.",
    "Did you enjoy today's grammar challenge? Let us know with your reactions!"
]

def fetch_databases():
    return client.list_database_names()

def fetch_collections(database_name):
    db = client[database_name]
    return db.list_collection_names()

def fetch_questions_from_collection(database_name, collection_name, num_questions):
    db = client[database_name]
    collection = db[collection_name]
    questions = collection.aggregate([{ '$sample': { 'size': num_questions } }])
    return list(questions)

def get_correct_option_index(answer_key):
    option_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    return option_mapping.get(answer_key.lower(), None)

async def send_motivational_message(channel_username):
    message = random.choice(MOTIVATIONAL_MESSAGES)
    try:
        await bot.send_message(
            chat_id=channel_username,
            text=f"{message}\n\n[@English_grammar_adda](https://t.me/english_grammar_adda)",
            parse_mode="Markdown"
        )
        print("Sent motivational message")
        await asyncio.sleep(2)  # Small delay before starting quiz
    except Exception as e:
        print(f"Error sending motivational message: {e}")

async def send_feedback_request(channel_username):
    message = random.choice(FEEDBACK_MESSAGES)
    try:
        await bot.send_message(
            chat_id=channel_username,
            text=f"{message}\n\n[@English_grammar_adda](https://t.me/english_grammar_adda)",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Our Channel", url="https://t.me/english_grammar_adda")]
            ])
        )
        print("Sent feedback request")
    except Exception as e:
        print(f"Error sending feedback request: {e}")

async def send_quiz_to_channel(question, options, correct_option_index, explanation, channel_username):
    question_text = f"{question}\n[@English_grammar_adda]"
    
    # Use "@Currentadda" if explanation is not available or is NaN
    if explanation is None or (isinstance(explanation, float) and math.isnan(explanation)):
        explanation = "@english_grammar_adda"
    
    try:
        await bot.send_poll(
            chat_id=channel_username,
            question=question_text,
            options=options,
            type='quiz',
            correct_option_id=correct_option_index,
            explanation=explanation,
            is_anonymous=True,
            allows_multiple_answers=False,
        )
        print(f"Quiz sent successfully: {question}")
    except Exception as e:
        print(f"Error sending quiz: {e}")

def generate_pdf(questions):
    """Generate a beautiful PDF with all quiz questions and answers"""
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Define custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.darkblue,
        spaceAfter=20,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=15
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        textColor=colors.black
    )
    
    option_style = ParagraphStyle(
        'OptionStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        leftIndent=20
    )
    
    correct_option_style = ParagraphStyle(
        'CorrectOptionStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        leftIndent=20,
        textColor=colors.darkgreen
    )
    
    explanation_style = ParagraphStyle(
        'ExplanationStyle',
        parent=styles['Italic'],
        fontSize=10,
        fontName='Helvetica-Oblique',
        leftIndent=15,
        textColor=colors.darkslategray,
        borderWidth=1,
        borderColor=colors.lightgrey,
        borderPadding=5,
        backColor=colors.lightgrey.lighter(),
        spaceAfter=15
    )
    
    # Add title
    elements.append(Paragraph("English Grammar Adda - Quiz Compilation", title_style))
    
    # Add date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Date: {current_date}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add introduction
    intro_text = """This PDF contains all questions from our Telegram channel quiz with correct answers and explanations. 
    Improve your English grammar by studying these questions and joining our channel for daily quizzes!"""
    elements.append(Paragraph(intro_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add channel promotion
    elements.append(Paragraph("Join Our Telegram Channel", subtitle_style))
    elements.append(Paragraph("@English_grammar_adda - https://t.me/english_grammar_adda", styles['Normal']))
    elements.append(Paragraph("Daily quizzes, tips, and resources to improve your English grammar skills!", styles['Italic']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Add questions section
    elements.append(Paragraph("Quiz Questions and Answers", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add each question
    for i, q in enumerate(questions):
        # Question
        elements.append(Paragraph(f"Question {i+1}: {q['Question']}", question_style))
        
        # Options
        options = [q['Option A'], q['Option B'], q['Option C'], q['Option D']]
        correct_option_index = get_correct_option_index(q['Answer'])
        
        for j, option in enumerate(options):
            if j == correct_option_index:
                elements.append(Paragraph(f"{chr(65+j)}) {option} ✓", correct_option_style))
            else:
                elements.append(Paragraph(f"{chr(65+j)}) {option}", option_style))
        
        # Explanation
        explanation = q.get('Explanation', "No explanation provided")
        if explanation and not (isinstance(explanation, float) and math.isnan(explanation)):
            elements.append(Paragraph(f"Explanation: {explanation}", explanation_style))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Add footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Keep learning and improving your English skills every day!", styles['Normal']))
    elements.append(Paragraph("Created with ❤️ by English Grammar Adda", styles['Normal']))
    
    # Build the PDF document
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

async def send_pdf_to_channel(channel_username, pdf_buffer):
    try:
        await bot.send_document(
            chat_id=channel_username,
            document=pdf_buffer,
            filename="English_Grammar_Quiz_Compilation.pdf",
            caption="📚 Here's a compilation of all questions from today's quiz with answers and explanations! Save this PDF for your English grammar practice. \n\n👉 Join @english_grammar_adda for daily quizzes and updates!"
        )
        print("PDF sent successfully to channel")
    except Exception as e:
        print(f"Error sending PDF: {e}")

async def store_quiz_history(questions):
    """Store quiz history in MongoDB for tracking"""
    try:
        db = client["QuizHistory"]
        collection = db["sent_quizzes"]
        
        quiz_record = {
            "date": datetime.datetime.now(),
            "questions": questions,
            "channel": CHANNEL_USERNAME
        }
        
        collection.insert_one(quiz_record)
        print("Quiz history stored in database")
    except Exception as e:
        print(f"Error storing quiz history: {e}")

async def main():
    print("Fetching databases...")
    databases = fetch_databases()
    print("Databases found:")
    for i, db_name in enumerate(databases):
        print(f"{i + 1}. {db_name}")
    
    # Use the specific database "MasterQuestions"
    selected_db = 'MasterQuestions'
    print(f"Selected database: {selected_db}")
    
    print(f"Fetching collections from database '{selected_db}'...")
    collections = fetch_collections(selected_db)
    print("Collections found:")
    for i, coll_name in enumerate(collections):
        print(f"{i + 1}. {coll_name}")
    
    # Use the specific collection "questions"
    selected_collection = 'English Grammar'
    print(f"Selected collection: {selected_collection}")
    
    num_questions = 5  # Number of questions to fetch

    questions = fetch_questions_from_collection(selected_db, selected_collection, num_questions)
    
    # Store questions for PDF generation
    global current_quiz_questions
    current_quiz_questions = questions
    
    # Send motivational message before quiz
    await send_motivational_message(CHANNEL_USERNAME)
    
    # Send quiz questions
    for question in questions:
        question_text = question['Question']
        options = [question['Option A'], question['Option B'], question['Option C'], question['Option D']]
        correct_option_index = get_correct_option_index(question['Answer'])
        explanation = question.get('Explanation', None)
        
        if correct_option_index is not None:
            await send_quiz_to_channel(question_text, options, correct_option_index, explanation, CHANNEL_USERNAME)
            await asyncio.sleep(2)  # 2 seconds delay between questions
        else:
            print(f"Skipping question due to invalid answer format: {question}")
    
    # 5 seconds delay before feedback request
    await asyncio.sleep(5)
    
    # Send feedback request
    await send_feedback_request(CHANNEL_USERNAME)
    
    # Generate and send PDF with answers
    pdf_buffer = generate_pdf(questions)
    await send_pdf_to_channel(CHANNEL_USERNAME, pdf_buffer)
    
    # Store quiz history for tracking
    await store_quiz_history(questions)

if __name__ == "__main__":
    asyncio.run(main())
