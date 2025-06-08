import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.versioning import NamespaceVersioning

from cerberus import Validator  # type: ignore
from rest_framework import status
from rest_framework.response import Response

from medicare_capstone.utils import custom_exceptions as ce
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from contacts.functions.login import login_function

# Get an instance of logger
logger = logging.getLogger("contacts")


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


# sign in api
class User_login(APIView):
    """
    This class will be used for users  - (signin, login, forgot password) functionality
    """

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
                schema = {
                    "user_type": {"type": "string", "required": True},
                    "email_id": {
                        "type": "string",
                        "required": True,
                        "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                    },
                    "password": {"type": "string", "required": True},

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
                output = login_function(request)
                return output
            else:
                raise ce.VersionNotSupported

        except ce.InvalidSlug as ins:
            logger.error("USER LOG IN API VIEW : POST - {}".format(ins))
            raise

        except ce.ValidationFailed as vf:
            logger.error("USER LOG IN API VIEW : POST - {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("USER LOG IN API VIEW : POST - {}".format(vns))
            raise

        except Exception as e:
            logger.error("USER LOG IN API VIEW : POST - {}".format(e))
            raise ce.InternalServerError
