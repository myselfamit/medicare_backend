# doctors/functions/profile.py

import json
import os
import logging
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response

# Get an instance of logger
logger = logging.getLogger("backend_doctor_profile")

def load_profiles_data():
    """
    Load profiles data from JSON file
    """
    try:
        base_path = os.getcwd()
        profiles_file_path = os.path.join(base_path, "data", "profiles.json")
        
        if os.path.exists(profiles_file_path):
            with open(profiles_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            logger.warning(f"Profiles file not found at {profiles_file_path}")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from profiles file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading profiles: {e}")
        return {}

def save_profiles_data(profiles_data):
    """
    Save profiles data to JSON file
    """
    try:
        base_path = os.getcwd()
        profiles_file_path = os.path.join(base_path, "data", "profiles.json")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(profiles_file_path), exist_ok=True)
        
        with open(profiles_file_path, 'w', encoding='utf-8') as file:
            json.dump(profiles_data, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving profiles: {e}")
        return False

def get_doctor_profile_data(request):
    """
    Get doctor profile data from JSON file
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        # Validate input
        if not user_type:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type is required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST)
        
        if not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "email_id is required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user type
        if user_type != 'doctor':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only doctors can access this endpoint.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load profiles data
        profiles_data = load_profiles_data()
        
        # Get doctor profile
        profile = profiles_data.get(email_id)
        
        if not profile:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Doctor profile not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if this is actually a doctor profile
        if profile.get('user_type') != 'doctor':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Profile exists but is not a doctor profile",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Doctor profile retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": profile
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting doctor profile data: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def update_doctor_profile_data(request):
    """
    Update doctor profile data in JSON file
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        profile_data = request.data.get("profile_data", {})
        
        # Validate input
        if not user_type:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type is required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "email_id is required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user type
        if user_type != 'doctor':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only doctors can update doctor profiles.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load profiles data
        profiles_data = load_profiles_data()
        
        # Get existing profile
        existing_profile = profiles_data.get(email_id)
        
        if not existing_profile:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Doctor profile not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update profile data
        updated_profile = {**existing_profile, **profile_data}
        updated_profile['last_updated'] = datetime.now().isoformat()
        updated_profile['user_type'] = 'doctor'  # Ensure user type is preserved
        
        # Save updated profile
        profiles_data[email_id] = updated_profile
        
        if save_profiles_data(profiles_data):
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Doctor profile updated successfully",
                    "timestamp": datetime.now().isoformat(),
                    "data": updated_profile
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Failed to save profile updates",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error updating doctor profile data: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def delete_doctor_profile_data(request):
    """
    Delete doctor profile data from JSON file
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        # Validate input
        if not user_type:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type is required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "email_id is required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user type
        if user_type != 'doctor':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only doctors can delete doctor profiles.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load profiles data
        profiles_data = load_profiles_data()
        
        # Check if profile exists
        if email_id not in profiles_data:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Doctor profile not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if this is actually a doctor profile
        if profiles_data[email_id].get('user_type') != 'doctor':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Profile exists but is not a doctor profile",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete profile
        del profiles_data[email_id]
        
        if save_profiles_data(profiles_data):
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Doctor profile deleted successfully",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Failed to delete profile",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error deleting doctor profile data: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )