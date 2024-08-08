import os
import asyncio
import math
from telegram import Bot
from pymongo import MongoClient

# Fetch sensitive information from environment variables
mongo_uri = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME')

# Initialize MongoDB client and Telegram bot
client = MongoClient(mongo_uri)
bot = Bot(token=BOT_TOKEN)

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
    selected_collection = 'questions'
    print(f"Selected collection: {selected_collection}")
    
    num_questions = 10  # Number of questions to fetch

    questions = fetch_questions_from_collection(selected_db, selected_collection, num_questions)
    
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

if __name__ == "__main__":
    asyncio.run(main())
