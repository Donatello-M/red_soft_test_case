from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.shortcuts import get_object_or_404

from .serializers import AssignMenteesSerializer, UserSerializer, UserCreateSerializer, LoginSerializer
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class RegistrationView(APIView):
    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя.",
        request_body=UserCreateSerializer,
        responses={
            201: UserCreateSerializer
        }
    )
    def post(self, request, *args, **kwargs):
        """Регистрация нового пользователя"""
        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Авторизация пользователя и получение JWT токенов.",
        request_body=LoginSerializer,
        responses={
            200: 'Token pair'
        }
    )
    def post(self, request):
        from rest_framework_simplejwt.views import TokenObtainPairView
        return TokenObtainPairView.as_view()(request._request)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Выход из системы. Блокирует refresh-токен.",
        request_body=None,
        responses={
            205: "Logout successful"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение списка всех пользователей.",
        responses={
            200: UserSerializer(many=True)
        }
    )
    def get_queryset(self):
        return User.objects.all()


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Получение или изменение данных пользователя.",
        request_body=UserSerializer,
        responses={
            200: UserSerializer
        }
    )
    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['pk'])
    
    def perform_update(self, serializer):
        user = self.get_object()
        self.check_object_permissions(self.request, user)
        serializer.save()


class AddMenteeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Назначение подопечных пользователю",
        request_body=AssignMenteesSerializer,
        responses={
            200: AssignMenteesSerializer
        }
    )
    def post(self, request, username):
        try:
            mentor = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Наставник не найден"}, status=status.HTTP_404_NOT_FOUND)

        mentees_usernames = request.data.get("mentees", [])
        if not isinstance(mentees_usernames, list):
            return Response({"error": "Список подчиненных должен быть массивом username"},
                            status=status.HTTP_400_BAD_REQUEST)

        mentees = User.objects.filter(username__in=mentees_usernames)
        if mentees.count() != len(mentees_usernames):
            return Response({"error": "Один или несколько логинов учеников не существуют"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if mentor.username in mentees_usernames:
            return Response({"error": "Нельзя назначить самого себя подопечным"},
                            status=status.HTTP_400_BAD_REQUEST)

        mentees.update(mentor=mentor)

        return Response({"message": f"Назначено {mentees.count()} подчиненных пользователю {mentor.username}"},
                        status=status.HTTP_200_OK)
