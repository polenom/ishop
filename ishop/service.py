import time
from datetime import datetime, timezone, timedelta
import random
from django.contrib.auth.models import User
from django.core.mail import send_mail


def send(userEmail):
    send_mail(
        'Вы подпичались на расссылку ',
        'ААААААААААААААААААААААААААААААААААА',
        'vitalimit88@gmail.com',
        [userEmail],
        fail_silently=False
    )

def send_6code_to_email(username):
    code = random.randrange(100000,1000000)
    email = User.objects.get(username=username).client.clientEmail
    res = 0
    tim = [60,30,15,5,1,1,0]
    while res != 1 and tim:
        res = send_mail(
            'Code from ishop',
            f'Code: {code}',
            'vitalimit88@gmail.com',
            [email],
            fail_silently=False
        )
        time.sleep(tim.pop())
    if res == 1:
        user = User.objects.get(username=username).checkemail
        user.password = code
        user.datetime = datetime.now(timezone.utc) + timedelta(seconds=10800)
        user.save(update_fields=['password', 'datetime'])