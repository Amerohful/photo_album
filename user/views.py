from django.contrib.auth import get_user_model
from rest_framework import generics

from user.serializers import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """ Create new user
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
