import uuid

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView as JWTokenObtainPairView,
    TokenRefreshView as JWTokenRefreshView,
    TokenVerifyView as JWTokenVerifyView,
)

from user.serializers import UserSerializer, UserTelegramSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Create a new user",
    ),
)
class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve information about the current user",
    ),
    put=extend_schema(
        summary="Update information about the current user",
    ),
    patch=extend_schema(
        summary="Partially update information about the current user",
    ),
)
class ManageUserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TelegramLinkView(GenericAPIView):
    serializer_class = UserTelegramSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request):
        user = self.get_object()
        user.telegram_token = uuid.uuid4()
        user.save()
        serializer = UserTelegramSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Obtain access and refresh tokens by given credentials",
    )
)
class TokenObtainPairView(JWTokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Refresh access token by given refresh token",
    )
)
class TokenRefreshView(JWTokenRefreshView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Check whether the given credentials are valid or not",
    )
)
class TokenVerifyView(JWTokenVerifyView):
    pass
