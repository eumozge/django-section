# Generated by Django 5.2.1 on 2025-06-14 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0010_alter_video_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="videofile",
            name="quantity",
            field=models.CharField(
                choices=[("HD", "720p"), ("FHD", "1080p"), ("UHD", "4K")],
                default="HD",
                max_length=3,
            ),
        ),
    ]
