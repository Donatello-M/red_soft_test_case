import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    # Фикстура для создания пользователя
    def make_user(username, password):
        user = get_user_model().objects.create_user(username=username, password=password)
        return user
    return make_user