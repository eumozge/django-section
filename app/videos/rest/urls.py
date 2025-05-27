from django.urls import include, path
from rest_framework import routers

from app.videos.rest.views import VideoViewSet

app_name = "videos"

v1_router = routers.SimpleRouter()
v1_router.register("", VideoViewSet)


urlpatterns = [
    path("v1/videos/", include(v1_router.urls)),
]
