import pytest
from django.db.models import Sum
from django.urls import reverse
from pytest_schema import schema
from rest_framework import status

from app.videos.models import Like, Video
from app.videos.tests.factories import VideoFactory


class TestVideoViewSet:
    @pytest.fixture
    def paths(self, video):
        return {
            "detail": reverse("videos:video-detail", kwargs={"pk": video.id}),
            "list": reverse("videos:video-list"),
            "ids": reverse("videos:video-ids"),
            "likes": reverse("videos:video-likes", kwargs={"pk": video.id}),
            "statistics-subquery": reverse("videos:video-statistics-subquery"),
            "statistics-group-by": reverse("videos:video-statistics-group-by"),
        }

    def test_paths(self, paths, video):
        assert paths == {
            "detail": f"/v1/videos/{video.id}/",
            "list": "/v1/videos/",
            "ids": "/v1/videos/ids/",
            "likes": f"/v1/videos/{video.id}/likes/",
            "statistics-subquery": "/v1/videos/statistics-subquery/",
            "statistics-group-by": "/v1/videos/statistics-group-by/",
        }

    def test_get(self, client, paths, video):
        response = client.user.get(paths["detail"])
        reference = {
            "owner": dict,
            "files": [{"file": None, "quality": "HD"}],
            "name": str,
            "total_likes": int,
            "created_at": str,
        }
        assert response.json() == schema(reference)

    @pytest.mark.parametrize(
        "client_user,reference_status",
        [
            ("anonymous", status.HTTP_404_NOT_FOUND),
            ("user", status.HTTP_200_OK),
            ("staff", status.HTTP_200_OK),
        ],
    )
    def test_get__published(self, client, paths, video, client_user, reference_status):
        video.unpublish()
        response = getattr(client, client_user).get(paths["detail"])
        assert response.status_code == reference_status

    def test_list(self, client, paths, video):
        response = client.user.get(paths["list"])
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"]

    def test_ids(self, client, paths, video):
        response = client.staff.get(paths["ids"])
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [video.id]

    def test_likes__anonymous(self, client, paths):
        response = client.anonymous.post(paths["likes"])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db(transaction=True)
    def test_likes__post(self, client, paths, user, video):
        assert video.total_likes == 0

        response = client.user.post(paths["likes"])
        assert response.status_code == status.HTTP_201_CREATED

        video.refresh_from_db()
        assert video.total_likes == 1

        likes = Like.objects.filter(user=user, video=video)
        assert likes.exists()

    @staticmethod
    def create_like(user, video):
        Like.objects.create(user=user, video=video)
        video.total_likes = 1
        video.save()

    def test_likes__delete(self, client, paths, user, video):
        self.create_like(user=user, video=video)
        assert video.total_likes == 1

        response = client.user.delete(paths["likes"])
        assert response.status_code == status.HTTP_204_NO_CONTENT

        video.refresh_from_db()
        assert video.total_likes == 0

        likes = Like.objects.filter(user=user, video=video)
        assert not likes.exists()

    @staticmethod
    def generate_likes(user, likes):
        return [VideoFactory(owner=user, total_likes=i) for i in range(likes)]

    @staticmethod
    def aggregate_likes(user):
        return Video.objects.filter(owner=user).aggregate(sum=Sum("total_likes"))["sum"]

    @pytest.fixture
    def statistics_reference(self, staff, user):
        Video.objects.all().delete()
        self.generate_likes(staff, likes=25)
        self.generate_likes(user, likes=10)
        return [
            {"username": staff.username, "likes_sum": self.aggregate_likes(staff)},
            {"username": user.username, "likes_sum": self.aggregate_likes(user)},
        ]

    def test_statistics__subquery(self, client, paths, statistics_reference):
        response = client.staff.get(paths["statistics-subquery"])
        assert response.json() == statistics_reference

    def test_statistics__group_by(self, client, paths, statistics_reference):
        response = client.staff.get(paths["statistics-group-by"])
        assert response.json() == statistics_reference
