# Generated by Django 4.0.4 on 2022-05-05 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0002_alter_motoroils_prod'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='books',
            name='id',
        ),
        migrations.RemoveField(
            model_name='motoroils',
            name='id',
        ),
        migrations.AlterField(
            model_name='books',
            name='prod',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='books', serialize=False, to='ishop.product'),
        ),
        migrations.AlterField(
            model_name='motoroils',
            name='prod',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='motoroils', serialize=False, to='ishop.product'),
        ),
    ]