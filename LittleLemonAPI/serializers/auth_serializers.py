from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    """Serializador para mostrar datos básicos de usuario."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializador personalizado para JWT que incluye info extra en el token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token