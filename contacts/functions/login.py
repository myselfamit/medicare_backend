import json
import logging
import uuid
import datetime
from rest_framework import status
from rest_framework.response import Response
from medicare_capstone.utils import custom_exceptions as ce
from contacts.common import messages as app_messages
import pandas as pd
import os

# Get an instance of logger
logger = logging.getLogger("contacts")

def check_user_function(user_type=None, email_id=None, password=None):

    base_path = os.getcwd()
    customise_path = "/data/users.csv"
    full_path = base_path + customise_path
    full_path = full_path.replace("\\", "/")
    df = pd.read_csv(full_path)
    
    for i in range(len(df)):
        if (
            df["user_type"][i] == user_type and
            df["email_id"][i] == email_id and
            df["password"][i] == password
        ):
            return "exists"
    
    return "does not exist"

def login_function(request):
    try:
        user_type = request.data.get("user_type").lower()
        email_id = request.data.get("email_id").lower()
        password = request.data.get("password")

        user_check = check_user_function(
            user_type=user_type, email_id=email_id, password=password
        )
        data = {
            "user_type":user_type,
            "email_id":email_id,
        }

        if user_check == "exists":
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": app_messages.USER_HAS_LOG_IN_SUCCESSFULLY,
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": app_messages.USER_HAS_FAILED_TO_LOG_IN,
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("CONTACTS - FUNCTION HELPER - USER LOGIN - {}".format(e))
        raise ce.InternalServerError
