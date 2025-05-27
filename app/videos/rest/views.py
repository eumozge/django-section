from django.db.models import OuterRef, Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.users.models import AppUser
from app.videos.models import Video
from app.videos.rest.serializers import StatisticsSerializer, VideoRetrieveSerializer
from app.videos.services.likes import LikeSetter


class VideoViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Video.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action in ("likes", "ids"):
            return qs.published()

        qs = qs.prefetch_related("files").order_by("-created_at")

        if not self.request.user.is_staff:
            return qs.published(user=self.request.user)

        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return VideoRetrieveSerializer
        if self.action in ("statistics_subquery", "statistics_group_by"):
            return StatisticsSerializer
        raise NotImplementedError

    @extend_schema(
        responses={status.HTTP_201_CREATED: None, status.HTTP_204_NO_CONTENT: None},
    )
    @action(["POST", "DELETE"], detail=True, permission_classes=[permissions.IsAuthenticated])
    def likes(self, request, *args, **kwargs):
        handler = LikeSetter(user=request.user, video=self.get_object())

        if request.method == "POST":
            handler.like()
            return Response(status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            handler.unlike()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise NotImplementedError(request.method)

    @extend_schema(
        # Use inline_serializer as example.
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="ListOfNumber", fields={"ids": serializers.ListField(child=serializers.IntegerField())}, many=False
            ),
        },
    )
    @action(["GET"], detail=False, permission_classes=[permissions.IsAdminUser])
    def ids(self, request, *args, **kwargs):
        videos = self.get_queryset().values_list("id", flat=True)
        return Response(videos)

    @extend_schema(
        responses={status.HTTP_200_OK: StatisticsSerializer},
    )
    @action(["GET"], detail=False, url_path="statistics-subquery", permission_classes=[permissions.IsAdminUser])
    def statistics_subquery(self, request, *args, **kwargs):
        """TODO Move queryset building to manager"""
        likes_sum = (
            Video.objects.published()
            .filter(owner=OuterRef("pk"))
            .values("owner")
            .annotate(likes_sum=Sum("total_likes"))
            .values("likes_sum")
        )
        users = AppUser.objects.values("username").annotate(likes_sum=likes_sum).order_by("-likes_sum")
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={status.HTTP_200_OK: StatisticsSerializer},
    )
    @action(["GET"], detail=False, url_path="statistics-group-by", permission_classes=[permissions.IsAdminUser])
    def statistics_group_by(self, request, *args, **kwargs):
        videos = Video.objects.published().statistics()
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)
