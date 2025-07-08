import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.versioning import NamespaceVersioning

from cerberus import Validator  # type: ignore
from rest_framework import status
from rest_framework.response import Response

from medicare_capstone.utils import custom_exceptions as ce
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Get an instance of logger
logger = logging.getLogger("patients")
from patients.functions.crud import (
    get_departments_function,
    search_doctors_function,
    get_doctor_slots_function,
    book_appointment_function
)

class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


class DepartmentListAPI(APIView):
    """
    This class will be used to get all departments with their specialties
    """
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get all departments with specialties
        """
        try:
            if request.version == "v1":
                output = get_departments_function()
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.VersionNotSupported as vns:
            logger.error("DEPARTMENT LIST API VIEW : GET - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("DEPARTMENT LIST API VIEW : GET - {}".format(e))
            raise ce.InternalServerError


class DoctorSearchAPI(APIView):
    """
    This class will be used to search doctors by department and specialty
    """
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Search doctors based on filters
        """
        try:
            if request.version == "v1":
                schema = {
                    "department": {"type": "string", "required": False},
                    "specialty": {"type": "string", "required": False}
                }
                
                validator = Validator(schema)
                if not validator.validate(request.data):
                    return Response(
                        {
                            "success": False,
                            "status_code": status.HTTP_400_BAD_REQUEST,
                            "message": "Invalid input",
                            "errors": validator.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                output = search_doctors_function(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.ValidationFailed as vf:
            logger.error("DOCTOR SEARCH API VIEW : POST - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("DOCTOR SEARCH API VIEW : POST - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("DOCTOR SEARCH API VIEW : POST - {}".format(e))
            raise ce.InternalServerError


class DoctorSlotsAPI(APIView):
    """
    This class will be used to get available slots for a doctor on a specific date
    """
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Get available slots for doctor
        """
        try:
            if request.version == "v1":
                schema = {
                    "doctor_id": {"type": "integer", "required": True},
                    "date": {
                        "type": "string", 
                        "required": True,
                        "regex": r"^\d{4}-\d{2}-\d{2}$"
                    }
                }
                
                validator = Validator(schema)
                if not validator.validate(request.data):
                    return Response(
                        {
                            "success": False,
                            "status_code": status.HTTP_400_BAD_REQUEST,
                            "message": "Invalid input",
                            "errors": validator.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                output = get_doctor_slots_function(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.ValidationFailed as vf:
            logger.error("DOCTOR SLOTS API VIEW : POST - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("DOCTOR SLOTS API VIEW : POST - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("DOCTOR SLOTS API VIEW : POST - {}".format(e))
            raise ce.InternalServerError


class BookAppointmentAPI(APIView):
    """
    This class will be used to book appointments
    """
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Book an appointment
        """
        try:
            if request.version == "v1":
                schema = {
                    "doctor_id": {"type": "integer", "required": True},
                    "patient_email": {
                        "type": "string",
                        "required": True,
                        "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                    },
                    "date": {
                        "type": "string", 
                        "required": True,
                        "regex": r"^\d{4}-\d{2}-\d{2}$"
                    },
                    "time_slot": {"type": "string", "required": True},
                    "type": {"type": "string", "required": False}
                }
                
                validator = Validator(schema)
                if not validator.validate(request.data):
                    return Response(
                        {
                            "success": False,
                            "status_code": status.HTTP_400_BAD_REQUEST,
                            "message": "Invalid input",
                            "errors": validator.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                output = book_appointment_function(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.ValidationFailed as vf:
            logger.error("BOOK APPOINTMENT API VIEW : POST - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("BOOK APPOINTMENT API VIEW : POST - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("BOOK APPOINTMENT API VIEW : POST - {}".format(e))
            raise ce.InternalServerError