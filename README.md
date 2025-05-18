# English Grammar Adda Quiz Bot

An automated Telegram bot that sends engaging English grammar quizzes to the [English Grammar Adda](https://t.me/english_grammar_adda) Telegram channel.

## Features

- 🤖 **Automated Quiz Delivery**: Sends quizzes twice daily at scheduled times
- ✨ **Engaging Content**: Includes motivational messages before quizzes and feedback requests after
- 📚 **PDF Generation**: Creates beautiful PDFs with questions, answers, and explanations
- 📊 **Quiz History**: Stores quiz history in MongoDB for tracking and analysis
- 🔄 **GitHub Actions Integration**: Fully automated deployment and scheduling

## How It Works

1. The bot connects to a MongoDB database to fetch random English grammar questions
2. A motivational message is sent to engage users before the quiz starts
3. Multiple-choice quiz questions are sent to the channel as polls
4. After the quiz, a feedback request encourages user interaction
5. A beautifully formatted PDF containing all questions with answers is shared for reference

## Environment Variables

The following environment variables need to be set as GitHub repository secrets:

- `MONGO_URI`: MongoDB connection string
- `TELEGRAM_BOT_TOKEN`: Telegram Bot API token
- `CHANNEL_USERNAME`: Telegram channel username (with @ symbol)

## Scheduling

The bot is configured to run automatically:
- Every day at 9:00 AM UTC
- Every day at 5:00 PM UTC

You can also trigger a manual run by using the "Run workflow" button in the GitHub Actions tab.

## Technologies Used

- Python
- python-telegram-bot
- MongoDB
- ReportLab (PDF generation)
- GitHub Actions (CI/CD)

## Join Our Channel

👉 [Join English Grammar Adda on Telegram](https://t.me/english_grammar_adda) 