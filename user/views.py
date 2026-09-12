from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny

from user.serializers import UserSerializer


class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


class ManageUserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
