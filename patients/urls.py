from django.urls import path
from patients.apis.dashboard import Dashboard
from patients.apis.crud import DepartmentListAPI,DoctorSearchAPI,DoctorSlotsAPI,BookAppointmentAPI


urlpatterns = [
    path("dashboard", Dashboard.as_view(), name="dashboard"),
    path("departments", DepartmentListAPI.as_view(), name="department-list"),
    path("search", DoctorSearchAPI.as_view(), name="doctor-search"),
    path("slots", DoctorSlotsAPI.as_view(), name="doctor-slots"),
    path("appointments/book", BookAppointmentAPI.as_view(), name="book-appointment"),
]

# from django.urls import path
# from your_app.api_views import (
#     DepartmentListAPI,
#     DoctorSearchAPI,
#     DoctorSlotsAPI,
#     BookAppointmentAPI
# )

# urlpatterns = [
#     # Department endpoints
#     path('v1/doctors/departments', 
#          DepartmentListAPI.as_view(), 
#          name='department-list'),
    
#     # Doctor search endpoint
#     path('v1/doctors/search', 
#          DoctorSearchAPI.as_view(), 
#          name='doctor-search'),
    
#     # Doctor slots endpoint
#     path('v1/doctors/slots', 
#          DoctorSlotsAPI.as_view(), 
#          name='doctor-slots'),
    
#     # Appointment booking endpoint
#     path('v1/appointments/book', 
#          BookAppointmentAPI.as_view(), 
#          name='book-appointment'),
# ]