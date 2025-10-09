from django.urls import path

from apps.authentication import views

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("register/", views.register, name="register"),
    path("login/", views.auth_login, name="login"),
    path("logout/", views.logout_user, name="logout_user"),
]
