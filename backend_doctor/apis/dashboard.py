import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.versioning import NamespaceVersioning

from cerberus import Validator  # type: ignore
from rest_framework import status
from rest_framework.response import Response

from medicare_capstone.utils import custom_exceptions as ce
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from backend_doctor.functions.dashboard import dashboard_function

# Get an instance of logger
logger = logging.getLogger("backend_doctor")


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


# sign in api
class Dashboard(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    versioning_class = VersioningConfig
    permission_classes = [AllowAny]

    def post(self, request):
        """
        here we will seperate through the slug given in the request
        """
        ...
        try:
            if request.version == "v1":
                output = dashboard_function(request)
                return output
            else:
                raise ce.VersionNotSupported

        except ce.InvalidSlug as ins:
            logger.error("USER DASHBOARD API VIEW : POST - {}".format(ins))
            raise

        except ce.ValidationFailed as vf:
            logger.error("USER DASHBOARD API VIEW : POST - {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("USER DASHBOARD API VIEW : POST - {}".format(vns))
            raise

        except Exception as e:
            logger.error("USER DASHBOARD API VIEW : POST - {}".format(e))
            raise ce.InternalServerError
