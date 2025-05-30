# Generated by Django 5.2.1 on 2025-05-28 12:58

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0005_rename_likes_video_like_count_like"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="like",
            old_name="owner",
            new_name="user",
        ),
        migrations.AlterUniqueTogether(
            name="like",
            unique_together={("video", "user")},
        ),
    ]
