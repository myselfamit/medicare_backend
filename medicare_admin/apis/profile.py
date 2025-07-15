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

from medicare_admin.functions.profile import get_admin_profile_data, update_admin_profile_data, delete_admin_profile_data

# Get an instance of logger
logger = logging.getLogger("backend_profile")

class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"
    


# Admin Profile API
class AdminProfile(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Get admin profile data
        """
        try:
            if request.version == "v1":
                output = get_admin_profile_data(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.InvalidSlug as ins:
            logger.error("ADMIN PROFILE API VIEW : POST - {}".format(ins))
            raise
            
        except ce.ValidationFailed as vf:
            logger.error("ADMIN PROFILE API VIEW : POST - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("ADMIN PROFILE API VIEW : POST - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("ADMIN PROFILE API VIEW : POST - {}".format(e))
            raise ce.InternalServerError

    def put(self, request):
        """
        Update admin profile data
        """
        try:
            if request.version == "v1":
                output = update_admin_profile_data(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.InvalidSlug as ins:
            logger.error("ADMIN PROFILE API VIEW : PUT - {}".format(ins))
            raise
            
        except ce.ValidationFailed as vf:
            logger.error("ADMIN PROFILE API VIEW : PUT - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("ADMIN PROFILE API VIEW : PUT - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("ADMIN PROFILE API VIEW : PUT - {}".format(e))
            raise ce.InternalServerError

    def delete(self, request):
        """
        Delete admin profile data
        """
        try:
            if request.version == "v1":
                output = delete_admin_profile_data(request)
                return output
            else:
                raise ce.VersionNotSupported
                
        except ce.InvalidSlug as ins:
            logger.error("ADMIN PROFILE API VIEW : DELETE - {}".format(ins))
            raise
            
        except ce.ValidationFailed as vf:
            logger.error("ADMIN PROFILE API VIEW : DELETE - {}".format(vf))
            raise
            
        except ce.VersionNotSupported as vns:
            logger.error("ADMIN PROFILE API VIEW : DELETE - {}".format(vns))
            raise
            
        except Exception as e:
            logger.error("ADMIN PROFILE API VIEW : DELETE - {}".format(e))
            raise ce.InternalServerError