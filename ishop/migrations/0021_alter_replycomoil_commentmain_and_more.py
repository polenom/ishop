# Generated by Django 4.0.4 on 2022-06-03 05:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ishop', '0020_rename_comment_replycomoil_replyuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replycomoil',
            name='commentMain',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='replyoil', to='ishop.commentsoil'),
        ),
        migrations.AlterField(
            model_name='replycomoil',
            name='replyUser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replyoil', to=settings.AUTH_USER_MODEL),
        ),
    ]
