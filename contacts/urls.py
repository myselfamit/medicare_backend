from django.urls import path
from contacts.apis.login import User_login
from contacts.apis.signin import User_signin

urlpatterns = [
    path("sign-in", User_signin.as_view(), name="sign-in"),
    path("log-in", User_login.as_view(), name="log-in"),
]
