# Generated by Django 4.0.4 on 2022-06-03 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0021_alter_replycomoil_commentmain_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replycomoil',
            name='commentMain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replyoil', to='ishop.commentsoil'),
        ),
    ]