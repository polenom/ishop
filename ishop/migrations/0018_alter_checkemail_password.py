# Generated by Django 4.0.4 on 2022-05-31 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0017_checkemail_datetime_checkemail_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkemail',
            name='password',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]