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
    UpdateAppointment,
    SubmitFeedback,
    FeedbackHistory,
    UpdateFeedback
)


# Add these URLs to the existing urlpatterns list
urlpatterns = [
    path("dashboard", Dashboard.as_view(), name="dashboard"),
    path("profile", PatientProfile.as_view(), name="PatientProfile"),
    path("departments", DepartmentsList.as_view(), name="DepartmentsList"),
    path("doctors", DoctorsList.as_view(), name="DoctorsList"),
    path("doctors/profile", DoctorProfile.as_view(), name="DoctorProfile"),
    path("doctors/slots", DoctorSlots.as_view(), name="DoctorSlots"),
    path("appointments/book", BookAppointment.as_view(), name="BookAppointment"),
    path("appointments", PatientAppointments.as_view(), name="PatientAppointments"),
    path("appointments/update", UpdateAppointment.as_view(), name="UpdateAppointment"),
    # Rating/Feedback URLs
    path("feedback/submit", SubmitFeedback.as_view(), name="SubmitFeedback"),
    path("feedback/history", FeedbackHistory.as_view(), name="FeedbackHistory"),
    path("feedback/update", UpdateFeedback.as_view(), name="UpdateFeedback"),
]