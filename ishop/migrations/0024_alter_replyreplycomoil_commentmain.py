# Generated by Django 4.0.4 on 2022-06-03 07:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0023_replyreplycomoil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replyreplycomoil',
            name='commentMain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replyreplyoil', to='ishop.replycomoil'),
        ),
    ]