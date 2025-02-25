import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db(['default'])

def test_registration(api_client):
    """ Тест на регистрацию """
    url = '/api/registration/'
    data = {
        'username': 'testuser',
        'password': 'password123',
        'email': 'testuser@example.com',
        'phone_number': '1234567890',
    }
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
    assert User.objects.get(username='testuser')

def test_login(api_client):
    """ Тест на логин """
    user = User.objects.create_user(username='testuser', password='password123')

    url = '/api/login/'
    data = {'username': 'testuser', 'password': 'password123'}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data

    access_token = response.data.get('access')
    assert access_token is not None, "Access token is missing"

def test_get_user_list(api_client):
    """ Тест на получение списка пользователей """
    user = User.objects.create_user(username="testuser", password="password123")

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    user1 = User.objects.create_user(username='user1', password='password123')
    user2 = User.objects.create_user(username='user2', password='password123')

    url = '/api/users/'
    response = api_client.get(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', format='json')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3

def test_get_user_detail(api_client):
    """ Тест на получение детального представления пользователя """
    user = User.objects.create_user(username='testuser', password='password123')

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    url = f'/api/users/{user.id}/'
    response = api_client.get(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'testuser'
    assert response.data['email'] is None
    assert response.data['phone_number'] is None

def test_logout(api_client):
    """Тест выхода из системы (logout)"""
    
    user = User.objects.create_user(username='testuser', password='password123')

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    url = '/api/logout/'
    response = api_client.post(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', data={'refresh': str(refresh)}, format='json')

    assert response.status_code == status.HTTP_205_RESET_CONTENT

def test_assign_mentees_success(api_client):
    """
    Тест успешного назначения подопечных.
    """
    mentor = User.objects.create_user(username='mentor', password='password123')
    mentee_1 = User.objects.create_user(username='mentee_1', password='password123')
    mentee_2 = User.objects.create_user(username='mentee_2', password='password123')

    data = {"mentees": [mentee_1.username, mentee_2.username]}

    refresh = RefreshToken.for_user(mentor)
    access_token = str(refresh.access_token)

    url = f'/api/users/{mentor.username}/add-mentees/'
    response = api_client.post(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', data=data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == f"Назначено 2 подчиненных пользователю {mentor.username}"

    # Проверяем, что подопечные действительно назначены
    mentee_1.refresh_from_db()
    mentee_2.refresh_from_db()
    assert mentee_1.mentor == mentor
    assert mentee_2.mentor == mentor

def test_assign_mentees_self_error(api_client):
    """
    Наставник не может назначить самого себя подопечным.
    """
    mentor = User.objects.create_user(username='mentor', password='password123')
    url = f"/api/users/{mentor.username}/add-mentees/"
    data = {"mentees": [mentor.username]}

    refresh = RefreshToken.for_user(mentor)
    access_token = str(refresh.access_token)

    response = api_client.post(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', data=data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Нельзя назначить самого себя подопечным"
