from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView as JWTokenObtainPairView,
    TokenRefreshView as JWTokenRefreshView,
    TokenVerifyView as JWTokenVerifyView,
)

from user.serializers import UserSerializer


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

    def get_object(self):
        return self.request.user


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
