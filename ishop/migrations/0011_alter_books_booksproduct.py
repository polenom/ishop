# Generated by Django 4.0.4 on 2022-04-28 12:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0010_alter_books_booksproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='booksProduct',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='book', serialize=False, to='ishop.product'),
        ),
    ]