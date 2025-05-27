import factory
from faker import Faker
from pytest_factoryboy import register

fake = Faker()


@register(_name="user")
@register(_name="staff", is_staff=True)
class AppUserFactory(factory.django.DjangoModelFactory):
    email = factory.LazyAttribute(lambda x: fake.email())
    username = factory.LazyAttribute(lambda x: fake.user_name())
    is_staff = False

    class Meta:
        model = "users.AppUser"
