import factory
from faker import Faker
from pytest_factoryboy import LazyFixture, register

fake = Faker()


@register(_name="video")
class VideoFactory(factory.django.DjangoModelFactory):
    owner = LazyFixture("user")
    is_published = True
    total_likes = 0

    class Meta:
        model = "videos.Video"

    @factory.post_generation
    def create_files(self, *args, **kwargs):
        VideoFileFactory(video=self)


@register(_name="video_file")
class VideoFileFactory(factory.django.DjangoModelFactory):
    video = factory.SubFactory(VideoFactory)

    class Meta:
        model = "videos.VideoFile"
