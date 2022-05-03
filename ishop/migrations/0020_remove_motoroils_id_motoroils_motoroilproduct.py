# Generated by Django 4.0.4 on 2022-05-03 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0019_alter_books_booksdiscription_alter_books_booksphoto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='motoroils',
            name='id',
        ),
        migrations.AddField(
            model_name='motoroils',
            name='motoroilProduct',
            field=models.OneToOneField(default=1, editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='commoditty', serialize=False, to='ishop.product'),
            preserve_default=False,
        ),
    ]
