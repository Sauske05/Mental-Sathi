# 🧠 Mental Satahi

**Mental Satahi** is a mental health engagement and sentiment tracking platform designed to support individuals dealing with mental health challenges. The platform provides an AI-powered chatbot for conversational support, tracks users' emotional well-being over time, and offers periodic sentiment reports to promote self-awareness and mental clarity.

## 🌟 Features

- **Conversational Chatbot with Context Awareness**  
  Engage with a chatbot that retains session-based conversation history and uses it to respond meaningfully to user queries.

- **Sentiment Tracker**  
  Users can input journal-style text to detect and log emotional sentiment using a BERT-based sentiment classifier (implemented from scratch).  
  The classified sentiment is scored and used to track emotional trends over weekly, monthly, and custom periods.

- **Scheduled Email Reports**  
  A cron job, implemented using **Celery Beat**, sends users a summary of their weekly sentiment report via email.

- **Sentiment Report Generator**  
  Users can generate a full sentiment analysis report at any time, showing trends and emotional insights based on past entries.

## 🛠️ Tech Stack

- **Backend:** Django (main application)
- **LLM Container:** FastAPI
- **NLP Model:** BERT-based sentiment classifier (custom implementation)
- **Task Scheduling:** Celery + Celery Beat
- **Database:** Default Django ORM-supported DB (e.g., SQLite/PostgreSQL)

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Sauske05/Mental-Sathi.git
cd mental-sathi
```

### 2. Set Up a Virtual Environment
```bash
python -m venv env
source env/bin/activate  # For Linux/macOS
# or
env\Scripts\activate  # For Windows
```
### 3. Install Dependencies
```bash
pip instaall -r requirements.txt
```

### 4. Run the App Locally
```bash
python manage.py migrate
python manage.py runserver
```
## Usage
- Interact with the chatbot to receive context-aware responses.

- Submit personal journal entries to log and analyze your mood.

- Receive automated weekly email reports.

- Generate sentiment reports directly from the UI.

## Email Setup
```bash
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your.smtp.server'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_password'
```
## Contributing
Feel free to fork the repo, open issues, and submit pull requests. Contributions are welcome!

## License
This project is licensed under the MIT License
