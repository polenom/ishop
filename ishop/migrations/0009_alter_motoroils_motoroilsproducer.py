# Generated by Django 4.0.4 on 2022-05-15 17:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0008_client_clientmobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='motoroils',
            name='motoroilsProducer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='oils', to='ishop.oilproducer'),
        ),
    ]