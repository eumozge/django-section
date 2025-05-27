from django.contrib import admin

from app.videos.models import Video, VideoFile


class VideoFileInlineAdmin(admin.StackedInline):
    model = VideoFile


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    search_fields = ("owner__email", "owner__username", "name")
    list_display = ("owner", "name", "created_at", "total_likes", "is_published")
    list_filter = ("is_published",)
    raw_id_fields = ("owner",)
    list_select_related = ("owner",)
    inlines = (VideoFileInlineAdmin,)
