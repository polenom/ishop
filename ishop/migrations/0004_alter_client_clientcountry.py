# Generated by Django 4.0.4 on 2022-04-26 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0003_alter_client_clientcountry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='clientCountry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ishop.city', verbose_name='client'),
        ),
    ]
