# from django.conf import settings
# from django.core.mail import send_mail
# send_mail('fffffffffffffffffffffffff', 'djangoffffffffffffffff', 'vitalimit88@gmail.com', ['kasmati@tut.by'], fail_silently=False)
#

from celery import Celery
app =  Celery('fd', broker='redis://0.0.0.0:6379/0', backend='redis://0.0.0.0')

@app.task
def add(x,y):
    return x/y
