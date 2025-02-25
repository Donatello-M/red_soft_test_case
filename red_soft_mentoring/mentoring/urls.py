from django.urls import path
from .views import RegistrationView, LoginView, UserListView, UserDetailView, LogoutView, AddMenteeView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/<str:username>/add-mentees/', AddMenteeView.as_view(), name='add-mentees')
]
