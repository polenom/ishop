from core.selery import app
from .service import send

@app.task
def send_spam_email(userEmail):
    send(userEmail)


@app.task
def create_user_profile(username):
    return 123