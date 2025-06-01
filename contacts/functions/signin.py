import json
import logging
import uuid
import datetime
from rest_framework import status
from rest_framework.response import Response
from medicare_capstone.utils import custom_exceptions as ce
from contacts.common import messages as app_messages

# Get an instance of logger
logger = logging.getLogger("contacts")


def signin_function(request):
    try:
        user_type = request.data.get("user_type").lower()
        first_name = request.data.get("first_name").lower()
        last_name = request.data.get("last_name").lower()
        email_id = request.data.get("email_id").lower()
        mobile = request.data.get("mobile")
        password = request.data.get("password")

        data = {
            "user_type":user_type,
            "first_name": first_name,
            "last_name": last_name,
            "email_id": email_id,
            "mobile": mobile,
            "password": password,
        }

        if data:
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": app_messages.USER_HAS_SIGNED_IN_SUCCESSFULLY,
                    "data": data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": app_messages.USER_HAS_FAILED_TO_SIGNIN,
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("CONTACTS - FUNCTION HELPER - USER SIGNIN - {}".format(e))
        raise ce.InternalServerError
