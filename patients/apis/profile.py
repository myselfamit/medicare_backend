import logging
import json
import os
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.versioning import NamespaceVersioning
from cerberus import Validator  # type: ignore
from rest_framework import status
from rest_framework.response import Response
from medicare_capstone.utils import custom_exceptions as ce
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Import profile functions
from patients.functions.profile import get_patient_profile_data, update_patient_profile_data, delete_patient_profile_data


# Get an instance of logger
logger = logging.getLogger("backend_profile")

class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"
    
    
    

# Patient Profile API
class PatientProfile(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Get patient profile data
        """
        try:
            if request.version == "v1":
                output = get_patient_profile_data(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.InvalidSlug as ins:
            logger.error("PATIENT PROFILE API VIEW : POST - {}".format(ins))
            raise
            
        except ce.ValidationFailed as vf:
            logger.error("PATIENT PROFILE API VIEW : POST - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("PATIENT PROFILE API VIEW : POST - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("PATIENT PROFILE API VIEW : POST - {}".format(e))
            raise ce.InternalServerError

    def put(self, request):
        """
        Update patient profile data
        """
        try:
            if request.version == "v1":
                output = update_patient_profile_data(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.InvalidSlug as ins:
            logger.error("PATIENT PROFILE API VIEW : PUT - {}".format(ins))
            raise
            
        except ce.ValidationFailed as vf:
            logger.error("PATIENT PROFILE API VIEW : PUT - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("PATIENT PROFILE API VIEW : PUT - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("PATIENT PROFILE API VIEW : PUT - {}".format(e))
            raise ce.InternalServerError

    def delete(self, request):
        """
        Delete patient profile data
        """
        try:
            if request.version == "v1":
                output = delete_patient_profile_data(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.InvalidSlug as ins:
            logger.error("PATIENT PROFILE API VIEW : DELETE - {}".format(ins))
            raise
            
        except ce.ValidationFailed as vf:
            logger.error("PATIENT PROFILE API VIEW : DELETE - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("PATIENT PROFILE API VIEW : DELETE - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("PATIENT PROFILE API VIEW : DELETE - {}".format(e))
            raise ce.InternalServerError
