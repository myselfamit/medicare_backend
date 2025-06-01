"""
Pydantic validation schemas for the contacts app.

This module contains all Pydantic models and validation utilities
for validating request data across different API endpoints.
"""

from datetime import date
from typing import Literal, Optional

from attr.validators import min_len
from pydantic import BaseModel, EmailStr, Field, validator
from pydantic import ValidationError as PydanticValidationError
import logging

# Get logger instance
logger = logging.getLogger("contacts")


class UserSigninSchemaV1(BaseModel):
    """
    Pydantic schema for user signin/registration validation (v1)

    This schema validates user registration data including personal information,
    contact details, and account type selection.
    """
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's first name",
        example="John"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's last name",
        example="Doe"
    )
    gender: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="User's gender",
        example="male"
    )
    dob: str = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format",
        regex=r"^\d{4}-\d{2}-\d{2}$",
        example="1990-01-15"
    )
    mobile: int = Field(
        ...,
        ge=1000000000,  # Minimum 10 digits
        le=99999999999999,  # Maximum 14 digits
        description="Mobile number as integer",
        example=1234567890
    )
    email_id: str = Field(
        ...,
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Valid email address",
        example="john.doe@example.com"
    )
    user_type: str = Field(
        ...,
        min_length=1,
        description="Type of user account (patient/doctor/admin)",
        example="patient"
    )

    @validator('first_name', 'last_name')
    def validate_names(cls, v, field):
        """
        Validate that names contain only letters and basic punctuation.

        Args:
            v: The field value
            field: The field being validated

        Returns:
            str: Cleaned and title-cased name

        Raises:
            ValueError: If name contains invalid characters or is empty
        """
        v = v.strip()
        if not v:
            raise ValueError(f'{field.name.replace("_", " ").title()} cannot be empty')

        # Allow letters, spaces, hyphens, and apostrophes
        if not v.replace(' ', '').replace('-', '').replace("'", '').replace('.', '').isalpha():
            raise ValueError(
                f'{field.name.replace("_", " ").title()} can only contain letters, spaces, hyphens, apostrophes, and periods')

        return v.title()

    @validator('gender')
    def validate_gender(cls, v):
        """
        Validate gender field.

        Args:
            v: Gender value

        Returns:
            str: Cleaned gender value

        Raises:
            ValueError: If gender is empty or invalid
        """
        v = v.strip().lower()
        if not v:
            raise ValueError('Gender cannot be empty')

        # Optional: Restrict to specific values
        # valid_genders = ['male', 'female', 'other', 'prefer not to say']
        # if v not in valid_genders:
        #     raise ValueError(f'Gender must be one of: {", ".join(valid_genders)}')

        return v

    @validator('dob')
    def validate_dob(cls, v):
        """
        Validate date of birth format and logical constraints.

        Args:
            v: Date of birth string

        Returns:
            str: Validated date string

        Raises:
            ValueError: If date format is invalid or date is illogical
        """
        try:
            # Parse the date to ensure it's valid
            birth_date = date.fromisoformat(v)

            # Check if date is not in future
            if birth_date > date.today():
                raise ValueError('Date of birth cannot be in the future')

            # Check minimum age (13 years for account creation)
            from datetime import timedelta
            min_age_date = date.today() - timedelta(days=13 * 365)
            if birth_date > min_age_date:
                raise ValueError('User must be at least 13 years old to create an account')

            # Check maximum age (120 years)
            max_age_date = date.today() - timedelta(days=120 * 365)
            if birth_date < max_age_date:
                raise ValueError('Please enter a valid date of birth')

            return v

        except ValueError as e:
            if "Invalid isoformat string" in str(e):
                raise ValueError('Date must be in YYYY-MM-DD format (e.g., 1990-01-15)')
            raise e

    @validator('mobile')
    def validate_mobile(cls, v):
        """
        Validate mobile number format and length.

        Args:
            v: Mobile number as integer

        Returns:
            int: Validated mobile number

        Raises:
            ValueError: If mobile number format is invalid
        """
        mobile_str = str(v)

        # Check length constraints
        if len(mobile_str) < 10:
            raise ValueError('Mobile number must be at least 10 digits')
        if len(mobile_str) > 14:
            raise ValueError('Mobile number cannot exceed 14 digits')

        # Ensure it's all digits (no negative numbers due to ge constraint)
        if not mobile_str.isdigit():
            raise ValueError('Mobile number must contain only digits')

        return v

    @validator('email_id')
    def validate_email_format(cls, v):
        """
        Additional email validation beyond regex.

        Args:
            v: Email address string

        Returns:
            str: Cleaned email address

        Raises:
            ValueError: If email format is invalid
        """
        v = v.strip().lower()
        if not v:
            raise ValueError('Email address cannot be empty')

        # Additional checks
        if len(v) > 254:  # RFC 5321 limit
            raise ValueError('Email address is too long')

        local, domain = v.rsplit('@', 1)
        if len(local) > 64:  # RFC 5321 limit for local part
            raise ValueError('Email local part is too long')

        return v

    @validator('user_type')
    def validate_user_type(cls, v):
        """
        Validate user type value.

        Args:
            v: User type string

        Returns:
            str: Validated user type

        Raises:
            ValueError: If user type is invalid
        """
        v = v.strip().lower()
        if not v:
            raise ValueError('User type cannot be empty')

        # Restrict to valid user types
        valid_types = ['patient', 'doctor', 'admin']
        if v not in valid_types:
            raise ValueError(f'User type must be one of: {", ".join(valid_types)}')

        return v

    class Config:
        """Pydantic model configuration"""
        # Enable validation on assignment
        validate_assignment = True

        # Use enum values instead of enum objects
        use_enum_values = True

        # Example for API documentation
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "gender": "male",
                "dob": "1990-01-15",
                "mobile": 1234567890,
                "email_id": "john.doe@example.com",
                "user_type": "patient"
            }
        }


class UserLoginSchemaV1(BaseModel):
    """
    Pydantic schema for user login validation (v1)
    """
    email_id: str = Field(
        ...,
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="User's email address",
        example="john.doe@example.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        description="User's password",
        example="securepassword123"
    )
    user_type: str = Field(
        ...,
        description="Type of user account",
        example="patient"
    )

    @validator('email_id')
    def validate_email(cls, v):
        """Validate and clean email"""
        return v.strip().lower()

    @validator('user_type')
    def validate_user_type(cls, v):
        """Validate user type"""
        v = v.strip().lower()
        valid_types = ['patient', 'doctor', 'admin']
        if v not in valid_types:
            raise ValueError(f'User type must be one of: {", ".join(valid_types)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "email_id": "john.doe@example.com",
                "password": "securepassword123",
                "user_type": "patient"
            }
        }


class ForgotPasswordSchemaV1(BaseModel):
    """
    Pydantic schema for forgot password validation (v1)
    """
    email_id: str = Field(
        ...,
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="User's email address",
        example="john.doe@example.com"
    )
    user_type: str = Field(
        ...,
        description="Type of user account",
        example="patient"
    )

    @validator('email_id')
    def validate_email(cls, v):
        """Validate and clean email"""
        return v.strip().lower()

    @validator('user_type')
    def validate_user_type(cls, v):
        """Validate user type"""
        v = v.strip().lower()
        valid_types = ['patient', 'doctor', 'admin']
        if v not in valid_types:
            raise ValueError(f'User type must be one of: {", ".join(valid_types)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "email_id": "john.doe@example.com",
                "user_type": "patient"
            }
        }


def validate_pydantic_data(schema_class, data, operation_name="validation"):
    """
    Helper function to validate data against Pydantic schema.

    This function provides a consistent interface for validating request data
    across different API endpoints using Pydantic schemas.

    Args:
        schema_class: Pydantic schema class to validate against
        data: Dictionary data to validate (usually request.data)
        operation_name: Name of the operation for logging purposes

    Returns:
        tuple: (is_valid: bool, validated_data: dict, errors: dict)

    Example:
        >>> is_valid, data, errors = validate_pydantic_data(
        ...     UserSigninSchemaV1,
        ...     request.data,
        ...     "user_signin"
        ... )
        >>> if not is_valid:
        ...     return Response({"errors": errors}, status=400)
    """
    try:
        # Validate data against schema
        validated_instance = schema_class(**data)

        # Log successful validation
        logger.info(f"Pydantic validation successful for {operation_name}")

        return True, validated_instance.dict(), None

    except PydanticValidationError as e:
        # Format errors to be consistent with DRF error format
        formatted_errors = {}

        for error in e.errors():
            # Extract field name from location tuple
            field = error['loc'][0] if error['loc'] else 'non_field_errors'
            message = error['msg']

            # Handle multiple errors for the same field
            if field in formatted_errors:
                if isinstance(formatted_errors[field], list):
                    formatted_errors[field].append(message)
                else:
                    formatted_errors[field] = [formatted_errors[field], message]
            else:
                formatted_errors[field] = [message]

        # Log validation errors
        logger.warning(f"Pydantic validation failed for {operation_name}: {formatted_errors}")

        return False, None, formatted_errors

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error during {operation_name} validation: {str(e)}"
        logger.error(error_msg)

        return False, None, {"non_field_errors": [str(e)]}


def get_schema_for_operation(operation_type, version="v1"):
    """
    Get the appropriate Pydantic schema for a given operation.

    Args:
        operation_type: Type of operation ('signin', 'login', 'forgot_password')
        version: API version (default: 'v1')

    Returns:
        Pydantic schema class

    Raises:
        ValueError: If operation_type or version is not supported
    """
    schema_mapping = {
        "v1": {
            "signin": UserSigninSchemaV1,
            "login": UserLoginSchemaV1,
            "forgot_password": ForgotPasswordSchemaV1,
        }
    }

    if version not in schema_mapping:
        raise ValueError(f"Unsupported API version: {version}")

    if operation_type not in schema_mapping[version]:
        raise ValueError(f"Unsupported operation type: {operation_type}")

    return schema_mapping[version][operation_type]