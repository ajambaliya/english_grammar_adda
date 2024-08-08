name: Telegram Quiz Bot

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run the script
      env:
        MONGO_URI: ${{ secrets.MONGO_URI }}
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        CHANNEL_USERNAME: ${{ secrets.CHANNEL_USERNAME }}
      run: |
        python main.py
