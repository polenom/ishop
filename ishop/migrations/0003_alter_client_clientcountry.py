# Generated by Django 4.0.4 on 2022-04-26 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0002_rename_client_client_clientuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='clientCountry',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.PROTECT, to='ishop.city', verbose_name='client'),
        ),
    ]