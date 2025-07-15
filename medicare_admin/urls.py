from django.urls import path
from medicare_admin.apis.dashboard import Dashboard
from medicare_admin.apis.profile import AdminProfile


urlpatterns = [
    path("dashboard", Dashboard.as_view(), name="dashboard"),
    path("profile", AdminProfile.as_view(), name="AdminProfile"),
    # path("appointments", User_login.as_view(), name="log-in"),
    # path("feedback", User_login.as_view(), name="log-in"),
]
