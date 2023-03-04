from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

# 다른 것과 마찬가지로 url check를 진행할 때,
# 위에서 아래로 순서대로 진행함.
urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.Me.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("@<str:username>", views.PublicUser.as_view()),
    path("log-in", views.LogIn.as_view()),
    path("log-out", views.LogOut.as_view()),
    path("token-login", obtain_auth_token),
]