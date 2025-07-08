from django.urls import path
from backend_doctor.apis.dashboard import Dashboard
# from backend_doctor.apis.schedule import Schedule
# from backend_doctor.apis.appointments import Appointments
# from backend_doctor.apis.patients import Patients
# from backend_doctor.apis.reviews import Reviews
# from backend_doctor.apis.profile import Profile


urlpatterns = [
    path("dashboard", Dashboard.as_view(), name="doctor-dashboard"),
    # path("schedule", User_login.as_view(), name="log-in"),
    # path("appointments", User_login.as_view(), name="log-in"),
    # path("patients", User_login.as_view(), name="log-in"),
    # path("reviews", User_login.as_view(), name="log-in"),
    # path("profile", User_login.as_view(), name="log-in"),
]

