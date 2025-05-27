from contextlib import suppress

from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError

from app.users.models import AppUser
from app.videos.models import Like, Video


class LikeHandler:
    def __init__(self, user: AppUser, video: Video):
        self.user = user
        self.video = video

    def _update(self, value: int):
        self.video.total_likes = F("total_likes") + value
        self.video.save(update_fields=["total_likes"])

    def like(self):
        with suppress(IntegrityError):
            Like.objects.create(user=self.user, video=self.video)
            self._update(+1)

    def unlike(self):
        with transaction.atomic():
            like = Like.objects.filter(user=self.user, video=self.video).select_for_update(skip_locked=True).first()
            if like is None:
                return

            like.delete()
            self._update(-1)
