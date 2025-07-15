# patients/views.py

import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.versioning import NamespaceVersioning
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from medicare_capstone.utils import custom_exceptions as ce

# Import appointment-related functions
from patients.functions.appointments import (
    get_doctors_by_department_data,
    get_departments_data,
    get_doctor_profile_data,
    get_doctor_slots_data,
    book_appointment_data,
    get_patient_appointments_data,
    update_appointment_data
)

# Logger instance
logger = logging.getLogger("backend_patient_appointments")

# Versioning configuration
class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"

# Get Departments API
class DepartmentsList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get all available departments
        """
        try:
            if request.version == "v1":
                output = get_departments_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("DEPARTMENTS LIST API VIEW : GET - {}".format(vns))
            raise
        except Exception as e:
            logger.error("DEPARTMENTS LIST API VIEW : GET - {}".format(e))
            raise ce.InternalServerError

# Get Doctors by Department API
class DoctorsList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get doctors filtered by department and specialty
        Query parameters: department, specialty
        """
        try:
            if request.version == "v1":
                output = get_doctors_by_department_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("DOCTORS LIST API VIEW : GET - {}".format(vns))
            raise
        except Exception as e:
            logger.error("DOCTORS LIST API VIEW : GET - {}".format(e))
            raise ce.InternalServerError

# Get Doctor Profile API
class DoctorProfile(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        """
        Get detailed doctor profile by ID
        """
        try:
            if request.version == "v1":
                output = get_doctor_profile_data(request, doctor_id)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("DOCTOR PROFILE API VIEW : GET - {}".format(vns))
            raise
        except Exception as e:
            logger.error("DOCTOR PROFILE API VIEW : GET - {}".format(e))
            raise ce.InternalServerError

# Get Doctor Available Slots API
class DoctorSlots(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get available time slots for a doctor on a specific date
        Query parameters: doctor_id, date
        """
        try:
            if request.version == "v1":
                output = get_doctor_slots_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("DOCTOR SLOTS API VIEW : GET - {}".format(vns))
            raise
        except Exception as e:
            logger.error("DOCTOR SLOTS API VIEW : GET - {}".format(e))
            raise ce.InternalServerError

# Book Appointment API
class BookAppointment(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Book an appointment for a patient with a doctor
        Request body: patient_id, doctor_id, date, time_slot
        """
        try:
            if request.version == "v1":
                output = book_appointment_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("BOOK APPOINTMENT API VIEW : POST - {}".format(vns))
            raise
        except Exception as e:
            logger.error("BOOK APPOINTMENT API VIEW : POST - {}".format(e))
            raise ce.InternalServerError

# Get Patient Appointments API
class PatientAppointments(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get list of all appointments for a patient
        Query parameters: patient_id
        """
        try:
            if request.version == "v1":
                output = get_patient_appointments_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("PATIENT APPOINTMENTS API VIEW : GET - {}".format(vns))
            raise
        except Exception as e:
            logger.error("PATIENT APPOINTMENTS API VIEW : GET - {}".format(e))
            raise ce.InternalServerError

    def post(self, request):
        """
        Get list of all appointments for a patient
        Request body: user_type, email_id
        """
        try:
            if request.version == "v1":
                output = get_patient_appointments_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("PATIENT APPOINTMENTS API VIEW : POST - {}".format(vns))
            raise
        except Exception as e:
            logger.error("PATIENT APPOINTMENTS API VIEW : POST - {}".format(e))
            raise ce.InternalServerError

# Update Appointment API
class UpdateAppointment(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def put(self, request, appointment_id):
        """
        Update an existing appointment's details
        Path parameter: appointment_id
        Request body: new_date, new_time_slot
        """
        try:
            if request.version == "v1":
                # Ensure appointment_id is passed to the function
                request.data._mutable = True if hasattr(request.data, "_mutable") else False
                request.data["appointment_id"] = appointment_id
                output = update_appointment_data(request)
                return output
            else:
                raise ce.VersionNotSupported
        except ce.VersionNotSupported as vns:
            logger.error("UPDATE APPOINTMENT API VIEW : PUT - {}".format(vns))
            raise
        except Exception as e:
            logger.error("UPDATE APPOINTMENT API VIEW : PUT - {}".format(e))
            raise ce.InternalServerError