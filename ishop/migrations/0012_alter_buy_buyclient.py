# Generated by Django 4.0.4 on 2022-05-25 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0011_buy_product_buyproductvalue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buy',
            name='buyClient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buy', to='ishop.client', verbose_name='buy'),
        ),
    ]