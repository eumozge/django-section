import pytest
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
            "likes": reverse("videos:video-likes", kwargs={"pk": video.id}),
            "statistics-subquery": reverse("videos:video-statistics-subquery"),
            "statistics": reverse("videos:video-statistics"),
        }

    def test_paths(self, paths, video):
        assert paths == {
            "detail": f"/v1/videos/{video.id}/",
            "list": "/v1/videos/",
            "likes": f"/v1/videos/{video.id}/likes/",
            "statistics-subquery": "/v1/videos/statistics-subquery/",
            "statistics": "/v1/videos/statistics/",
        }

    def test_get(self, client, paths, video):
        response = client.user.get(paths["detail"])
        reference = {
            "owner": dict,
            "files": [{"file": None, "quantity": "HD"}],
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

    def test_likes__anonymous(self, client, paths):
        response = client.anonymous.post(paths["likes"])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_likes__post(self, client, paths, video):
        assert video.total_likes == 0

        response = client.user.post(paths["likes"])
        assert response.status_code == status.HTTP_201_CREATED

        video.refresh_from_db()
        assert video.total_likes == 1

    def test_likes__delete(self, client, paths, user, video):
        Like.objects.create(user=user, video=video)
        video.total_likes = 1
        video.save()

        response = client.user.delete(paths["likes"])
        assert response.status_code == status.HTTP_204_NO_CONTENT

        video.refresh_from_db()
        assert video.total_likes == 0

        likes = Like.objects.filter(user=user, video=video)
        assert not likes.exists()

    def test_statistics(self, client, paths, user, staff):
        Video.objects.all().delete()
        [VideoFactory(owner=user, total_likes=i) for i in range(5)] + [
            VideoFactory(owner=staff, total_likes=i * 2) for i in range(5)
        ]
        reference = [{"username": staff.username, "likes_sum": 20}, {"username": user.username, "likes_sum": 10}]

        response_subquery = client.staff.get(paths["statistics-subquery"])
        assert response_subquery.json() == reference

        response = client.staff.get(paths["statistics"])
        assert response.json() == reference
