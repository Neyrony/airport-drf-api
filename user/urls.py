from django.urls import path


from user.views import (
    UserCreateView,
    ManageUserView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="profile"),
]

app_name = "user"
