import os
import asyncio
import math
import random
import datetime
import json
import io
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from pdf_generator import generate_modern_pdf

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
    "🌟 Time to boost your English skills! Ready for today's grammar challenge? Let's see how many you can get right! 🧠",
    "📚 Knowledge is power! Strengthen your grammar with today's quiz! Can you score 100%? 🏆",
    "💡 The more you practice, the better you become! Test your grammar knowledge with these handpicked questions! 📝",
    "🚀 Improve your English one question at a time. Today's quiz will help you level up! Ready to begin? ✨",
    "🎯 Daily practice makes perfect! Here's your English grammar challenge for today! How many can you answer? 🤔",
    "🧠 Exercise your brain with today's English grammar quiz! These questions will test your knowledge! 💪",
    "✨ Great English skills open new doors! Ready to level up with today's grammar challenge? 🚀",
    "📝 Let's see how much you've improved with today's grammar quiz! Challenge yourself! 🔍",
    "🔍 Attention to detail is key in mastering English grammar. Ready to test yours with today's quiz? 📊",
    "🌈 Each quiz brings you one step closer to English fluency! Today's questions are waiting for you! 📈"
]

# Feedback messages to display after quiz
FEEDBACK_MESSAGES = [
    "👍 How did you find today's quiz? React with ❤️ if you enjoyed it and share with friends who want to improve their English! 📲",
    "🌟 Did you learn something new today? If this quiz helped you, please react with ❤️ and share our channel with your friends! 🙏",
    "💯 Rate our quiz by reacting with ❤️! Your feedback helps us create better content for you. Don't forget to share! 📱",
    "📊 Was this quiz helpful? Let us know by reacting to this message and sharing our channel with your friends! 👥",
    "🏆 Don't forget to share your score in the comments! How many did you get right? React with ❤️ if you want more quizzes like this! 💬",
    "❓ We'd love to hear your thoughts! React with ❤️ and comment to let us know how we can improve. Share with friends who need grammar practice! 🔄",
    "🎁 Found this quiz useful? React with ❤️ and share with friends who might benefit! Your support helps us grow! 📣",
    "🤝 Learning is a journey we take together. How was today's English grammar lesson? React and share to help others learn too! 📚",
    "💌 Your feedback helps us create better content! Rate today's quiz with reactions and tag a friend who would enjoy our quizzes! 👫",
    "🎓 Did you enjoy today's grammar challenge? React with ❤️ and share our channel - together, we can help more people improve their English! 🌍"
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
        # Create a message with inline keyboard for better engagement
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📱 Join Channel", url="https://t.me/english_grammar_adda"),
                InlineKeyboardButton("📲 Share Quiz", url=f"https://t.me/share/url?url=https://t.me/english_grammar_adda&text=I'm learning English grammar with these amazing daily quizzes! Check it out!")
            ],
        ])
        
        await bot.send_message(
            chat_id=channel_username,
            text=f"🎉 **Quiz Complete!** 🎉\n\n{message}\n\n[@English_grammar_adda](https://t.me/english_grammar_adda)",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        print("Sent feedback request")
    except Exception as e:
        print(f"Error sending feedback request: {e}")

async def send_quiz_to_channel(question, options, correct_option_index, explanation, channel_username):
    question_text = f"{question}\n[@English_grammar_adda]"
    
    # Use "@english_grammar_adda" if explanation is not available or is NaN
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

async def send_pdf_to_channel(channel_username, pdf_buffer):
    try:
        await bot.send_document(
            chat_id=channel_username,
            document=pdf_buffer,
            filename="English_Grammar_Quiz_Compilation.pdf",
            caption="📚 **QUIZ ANSWERS & EXPLANATIONS** 📚\n\nHere's a beautiful PDF with all questions, correct answers, and explanations from today's quiz!\n\n✅ Save it for your English grammar practice\n✅ Study at your convenience\n✅ Share with friends who are learning English\n\n👉 Join  for daily quizzes and updates!",
            parse_mode="Markdown"
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
    
    # Generate and send PDF with answers using the new modern PDF generator
    try:
        pdf_buffer = generate_modern_pdf(questions)
        await send_pdf_to_channel(CHANNEL_USERNAME, pdf_buffer)
    except Exception as e:
        print(f"Error generating or sending PDF: {e}")
    
    # Store quiz history for tracking
    await store_quiz_history(questions)

if __name__ == "__main__":
    asyncio.run(main())
