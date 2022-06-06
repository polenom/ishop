# Generated by Django 4.0.4 on 2022-06-06 10:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ishop', '0026_alter_replyreplycombooks_commentmain'),
    ]

    operations = [
        migrations.AddField(
            model_name='motoroils',
            name='motoroilslikes',
            field=models.ManyToManyField(blank=True, related_name='oilslikes', to=settings.AUTH_USER_MODEL),
        ),
    ]