from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("register/tenant/", views.register_tenant, name="register_tenant"),
    path("register/landlord/", views.register_landlord, name="register_landlord"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=__import__("accounts.forms", fromlist=["LoginForm"]).LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("verification/", views.verification, name="verification"),
    path("preferences/", views.preferences, name="preferences"),
]
