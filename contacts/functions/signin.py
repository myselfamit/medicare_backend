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

def check_user_function(user_type=None, email_id=None, mobile=None):

    base_path = os.getcwd()
    customise_path = "/data/users.csv"
    full_path = base_path + customise_path
    full_path = full_path.replace("\\", "/")
    df = pd.read_csv(full_path)

    for i in range(0, len(df["email_id"])):
        if (
            (df["user_type"][i] == user_type)
            and (df["email_id"][i] == email_id)
            and (df["mobile"][i] == mobile)
        ):
            data = "exists"
            return data
        else:
            data = "does not exists"
            return data


def add_user_details(
    user_type=None,
    first_name=None,
    last_name=None,
    email_id=None,
    mobile=None,
    password=None,
):
    base_path = os.getcwd()
    customise_path = "/data/users.csv"
    full_path = base_path + customise_path
    full_path = full_path.replace("\\", "/")

    new_user = {
        "first_name": [first_name],  # Wrap values in lists for DataFrame
        "last_name": [last_name],
        "email_id": [email_id],
        "password": [password],  # Consider hashing password before saving
        "mobile": [mobile],
        "user_type": [user_type],
    }
    # Make data frame of above data
    df = pd.DataFrame(new_user)
    df.to_csv(full_path, mode="a", index=False, header=False)

def signin_function(request):
    try:
        user_type = request.data.get("user_type").lower()
        first_name = request.data.get("first_name").lower()
        last_name = request.data.get("last_name").lower()
        email_id = request.data.get("email_id").lower()
        mobile = request.data.get("mobile")
        password = request.data.get("password")

        user_check = check_user_function(
            user_type=user_type, email_id=email_id, mobile=mobile
        )

        if user_check == "exists":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": app_messages.USER_ALREADY_EXISTS,
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            add_user_details(
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                email_id=email_id,
                mobile=mobile,
                password=password,
            )

            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": app_messages.USER_HAS_SIGNED_IN_SUCCESSFULLY,
                    "data": None,
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("CONTACTS - FUNCTION HELPER - USER SIGNIN - {}".format(e))
        raise ce.InternalServerError
