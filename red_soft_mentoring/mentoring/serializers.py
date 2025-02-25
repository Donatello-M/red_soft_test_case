from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    mentees = serializers.SerializerMethodField()
    mentor = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'email', 'password', 'mentor', 'mentees']
        read_only_fields = ['mentor', 'mentees']

    def get_mentees(self, obj):
        if obj.is_staff:
            return [mentee.username for mentee in obj.mentees.all()]
        return []

    def get_mentor(self, obj):
        return obj.mentor.username if obj.mentor else None

    def get_password(self, obj):
        request = self.context.get('request')
        if request and request.user == obj:
            return obj.password
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class AssignMenteesSerializer(serializers.Serializer):
    mentees = serializers.ListField(
        child=serializers.CharField()
    )