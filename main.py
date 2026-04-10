name: Run ProTrade Bot

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]
  workflow_dispatch: # يتيح لك تشغيل البوت يدوياً من GitHub

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run Bot
      run: |
        # الكود يبحث عن أي ملف ينتهي بـ .py ويقوم بتشغيله إذا لم يجد main.py
        if [ -f main.py ]; then
          python main.py
        elif [ -f app.py ]; then
          python app.py
        elif [ -f bot.py ]; then
          python bot.py
        else
          python *.py
        fi
