import pytest
from rest_framework.test import APIClient

from app.users.models import AppUser

__all__ = ("client",)


class AppClientFactory:
    def __init__(self, user: AppUser, staff: AppUser):
        self._client_class = APIClient
        self._user = user
        self._staff = staff

    def get_client(self, user: AppUser = None):
        client = self._client_class()
        user is not None and client.force_authenticate(user)
        return client

    @property
    def anonymous(self):
        return self.get_client()

    @property
    def user(self):
        return self.get_client(user=self._user)

    @property
    def staff(self):
        return self.get_client(user=self._staff)


@pytest.fixture
def client(user, staff):
    return AppClientFactory(user=user, staff=staff)
