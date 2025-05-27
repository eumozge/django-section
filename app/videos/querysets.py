from django.db import models
from django.db.models import F, Q, Sum


class VideoQuerySet(models.QuerySet):
    def published(self, user=None):
        if user is not None and user.is_authenticated:
            return self.filter(Q(is_published=True) | Q(owner=user))
        return self.filter(is_published=True)

    def statistics(self):
        return (
            self.values("owner__username")
            .annotate(username=F("owner__username"), likes_sum=Sum("total_likes"))
            .values("username", "likes_sum")
            .order_by("-likes_sum")
        )
