from django.core.mail import send_mail

def send(userEmail):
    send_mail(
        'Вы подпичались на расссылку ',
        'ААААААААААААААААААААААААААААААААААА',
        'vitalimit88@gmail.com',
        [userEmail],
        fail_silently=False
    )