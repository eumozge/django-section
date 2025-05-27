from django.db import models

from app.videos.querysets import VideoQuerySet


class Video(models.Model):
    owner = models.ForeignKey("users.AppUser", on_delete=models.PROTECT, related_name="videos")
    is_published = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    total_likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = VideoQuerySet.as_manager()

    def __str__(self):
        return self.name

    def unpublish(self):
        self.is_published = False
        self.save(update_fields=["is_published"])


class VideoFile(models.Model):
    class QualityChoices(models.TextChoices):
        HD = "HD", "720p"
        FHD = "FHD", "1080p"
        UHD = "UHD", "4K"

    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE, related_name="files")
    file = models.FileField(blank=True, null=True)
    quality = models.CharField(max_length=3, choices=QualityChoices.choices, default=QualityChoices.HD)

    class Meta:
        unique_together = ("video", "quality")

    def __str__(self):
        return f"{self.video} - {self.quality}"


class Like(models.Model):
    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.AppUser", on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("video", "user")
