from django.urls import path
from medicare_admin.apis.dashboard import Dashboard


urlpatterns = [
    path("dashboard", Dashboard.as_view(), name="dashboard"),
    # path("manage_doctors", User_login.as_view(), name="log-in"),
    # path("appointments", User_login.as_view(), name="log-in"),
    # path("feedback", User_login.as_view(), name="log-in"),
]
