from django.urls import path
from patients.apis.dashboard import Dashboard
from patients.apis.profile import PatientProfile
from patients.apis.crud import DepartmentListAPI,DoctorSearchAPI,DoctorSlotsAPI,BookAppointmentAPI
from patients.apis.appointments import (
    DepartmentsList,
    DoctorsList,
    DoctorProfile,
    DoctorSlots,
    BookAppointment,
    PatientAppointments,
    UpdateAppointment
)

urlpatterns = [
    path("dashboard", Dashboard.as_view(), name="dashboard"),
    # path("departments", DepartmentListAPI.as_view(), name="department-list"),
    # path("search", DoctorSearchAPI.as_view(), name="doctor-search"),
    # path("slots", DoctorSlotsAPI.as_view(), name="doctor-slots"),
    # path("appointments/book", BookAppointmentAPI.as_view(), name="book-appointment"),
    path("profile", PatientProfile.as_view(), name="PatientProfile"),
    path("departments", DepartmentsList.as_view(), name="DepartmentsList"),
    path("doctors", DoctorsList.as_view(), name="DoctorsList"),
    path("doctors/profile", DoctorProfile.as_view(), name="DoctorProfile"),
    path("doctors/slots", DoctorSlots.as_view(), name="DoctorSlots"),
    path("appointments/book", BookAppointment.as_view(), name="BookAppointment"),
    path("appointments", PatientAppointments.as_view(), name="PatientAppointments"),
    path("appointments/update", UpdateAppointment.as_view(), name="UpdateAppointment"),
]