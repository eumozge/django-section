# Generated by Django 5.2.1 on 2025-05-28 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0008_alter_videofile_video"),
    ]

    operations = [
        migrations.RenameField(
            model_name="video",
            old_name="likes_count",
            new_name="total_likes",
        ),
    ]
