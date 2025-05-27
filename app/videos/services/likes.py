from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError

from app.users.models import AppUser
from app.videos.models import Like, Video


class LikeSetter:
    def __init__(self, user: AppUser, video: Video):
        self.user = user
        self.video = video

    def __update(self, value: int):
        self.video.total_likes = F("total_likes") + value
        self.video.save(update_fields=["total_likes"])

    def like(self):
        """If a like already exists, an IntegrityError will be raised because of the unique constraint on user+video."""
        try:
            Like.objects.create(user=self.user, video=self.video)
            self.__update(+1)
        except IntegrityError:
            return False
        return True

    def unlike(self):
        """
        In this case, it is possible to handle concurrency without select_for_update
        because delete() returns the number of deleted objects. select_for_update is just an example;
        it would be suitable if we wanted to read something before deleting it.

        Example with delete():
            deleted_objects_count, *_ = self.user.likes.all().filter(video=self.video).delete()
            if deleted_objects_count: ...
        """
        with transaction.atomic():
            like = self.user.likes.all().filter(video=self.video).select_for_update(skip_locked=True).first()

            if like is None:
                return False

            like.delete()
            self.__update(-1)
            return True
