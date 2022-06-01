from core.selery import app
from .service import send, send_6code_to_email

@app.task
def send_spam_email(userEmail):
    send(userEmail)


@app.task
def send_6code(username):
    send_6code_to_email(username)