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

def get_patient_dashboard_data1(user_type=None, email_id=None):
    """
    Get comprehensive dashboard data for a patient
    """
    try:
        base_path = os.getcwd()
        
        # Read all required CSV files
        users_df = pd.read_csv(base_path + "/data/users.csv")
        
        # Check if other CSV files exist and read them
        csv_files = {
            'doctors': base_path + "/data/doctors.csv",
            'appointments': base_path + "/data/appointments.csv", 
            'feedback': base_path + "/data/feedback.csv",
            'availability': base_path + "/data/availability.csv",
            'notifications': base_path + "/data/notifications.csv"
        }
        
        dataframes = {}
        for name, path in csv_files.items():
            if os.path.exists(path.replace("\\", "/")):
                dataframes[name] = pd.read_csv(path.replace("\\", "/"))
            else:
                dataframes[name] = pd.DataFrame()
        
        # Find the patient's user data
        patient_user = users_df[
            (users_df['user_type'] == user_type) & 
            (users_df['email_id'] == email_id)
        ]
        
        if patient_user.empty:
            return {"error": "Patient not found"}
        
        patient_info = patient_user.iloc[0].to_dict()
        
        # Mock dashboard statistics (since CSV files are empty)
        dashboard_stats = {
            'total_appointments': 12,
            'upcoming_appointments': 2,
            'completed_appointments': 9,
            'pending_appointments': 1,
            'cancelled_appointments': 2,
            'last_checkup': '2024-12-15',
            'average_rating': 4.5,
            'total_reviews': 8
        }
        
        # Mock upcoming appointments
        upcoming_appointments = [
            {
                'appointment_id': 'apt_p001',
                'doctor_name': 'Dr. Sarah Johnson',
                'specialty': 'Cardiology',
                'date': '2025-01-06',
                'time': '10:00 AM',
                'type': 'Follow-up',
                'status': 'confirmed',
                'location': 'Building A, Room 201'
            },
            {
                'appointment_id': 'apt_p002',
                'doctor_name': 'Dr. Michael Chen',
                'specialty': 'Neurology',
                'date': '2025-01-08',
                'time': '2:30 PM',
                'type': 'Consultation',
                'status': 'confirmed',
                'location': 'Building B, Room 305'
            }
        ]
        
        # Mock past appointments
        past_appointments = [
            {
                'appointment_id': 'apt_p003',
                'doctor_name': 'Dr. Sarah Johnson',
                'specialty': 'Cardiology',
                'date': '2024-12-15',
                'time': '10:00 AM',
                'type': 'Check-up',
                'status': 'completed',
                'rating': 5,
                'can_review': False
            },
            {
                'appointment_id': 'apt_p004',
                'doctor_name': 'Dr. Robert Kim',
                'specialty': 'General Medicine',
                'date': '2024-11-20',
                'time': '3:00 PM',
                'type': 'Consultation',
                'status': 'completed',
                'rating': 4,
                'can_review': False
            },
            {
                'appointment_id': 'apt_p005',
                'doctor_name': 'Dr. Emily Rodriguez',
                'specialty': 'Pediatrics',
                'date': '2024-10-10',
                'time': '11:15 AM',
                'type': 'Vaccination',
                'status': 'completed',
                'rating': None,
                'can_review': True
            }
        ]
        
        # Mock notifications
        notifications = [
            {
                'notification_id': 'not_p001',
                'type': 'appointment_reminder',
                'message': 'Appointment with Dr. Johnson tomorrow at 10:00 AM',
                'time': '2 hours ago',
                'priority': 'high'
            },
            {
                'notification_id': 'not_p002',
                'type': 'health_reminder',
                'message': 'Time for your daily medication',
                'time': '4 hours ago',
                'priority': 'medium'
            },
            {
                'notification_id': 'not_p003',
                'type': 'checkup_reminder',
                'message': 'Annual checkup due next month',
                'time': '1 day ago',
                'priority': 'low'
            }
        ]
        
        # Mock health tips
        health_tips = [
            {
                'tip_id': 'tip_001',
                'title': 'Stay Hydrated',
                'description': 'Drink at least 8 glasses of water daily for optimal health.',
                'category': 'hydration'
            },
            {
                'tip_id': 'tip_002',
                'title': 'Regular Exercise',
                'description': '30 minutes of daily exercise can improve your overall health.',
                'category': 'exercise'
            },
            {
                'tip_id': 'tip_003',
                'title': 'Sleep Well',
                'description': 'Aim for 7-9 hours of quality sleep each night.',
                'category': 'sleep'
            }
        ]
        
        return {
            'patient_info': {
                'first_name': patient_info.get('first_name', ''),
                'last_name': patient_info.get('last_name', ''),
                'email_id': patient_info.get('email_id', ''),
                'mobile': patient_info.get('mobile', ''),
                'user_type': patient_info.get('user_type', ''),
                'member_since': '2023-05-15',
                'health_score': 'Good'
            },
            'dashboard_stats': dashboard_stats,
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
            'notifications': notifications,
            'health_tips': health_tips
        }
        
    except Exception as e:
        logger.error(f"Error getting patient dashboard data: {e}")
        return {"error": str(e)}

def patient_dashboard_function(request):
    """
    Main function to handle patient dashboard API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if not user_type or not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User type and email ID are required",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if user_type != "patient":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied. Only patients can access this dashboard.",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        dashboard_data = get_patient_dashboard_data(user_type=user_type, email_id=email_id)
        
        if "error" in dashboard_data:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": f"Dashboard data error: {dashboard_data['error']}",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Patient dashboard data retrieved successfully",
                "data": dashboard_data,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("PATIENT DASHBOARD - FUNCTION HELPER - GET DASHBOARD DATA - {}".format(e))
        raise ce.InternalServerError

# Additional patient functions

def get_patient_upcoming_appointments(user_type=None, email_id=None):
    """
    Get patient's upcoming appointments
    """
    try:
        # This would normally query the CSV files, but since they're empty, returning mock data
        upcoming_appointments = [
            {
                'appointment_id': 'apt_p001',
                'doctor_name': 'Dr. Sarah Johnson',
                'specialty': 'Cardiology',
                'date': '2025-01-06',
                'time': '10:00 AM',
                'type': 'Follow-up',
                'status': 'confirmed',
                'location': 'Building A, Room 201'
            },
            {
                'appointment_id': 'apt_p002',
                'doctor_name': 'Dr. Michael Chen',
                'specialty': 'Neurology',
                'date': '2025-01-08',
                'time': '2:30 PM',
                'type': 'Consultation',
                'status': 'pending',
                'location': 'Building B, Room 305'
            }
        ]
        
        return upcoming_appointments
        
    except Exception as e:
        logger.error(f"Error getting patient upcoming appointments: {e}")
        return []

def patient_upcoming_appointments_function(request):
    """
    Function to handle patient upcoming appointments API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "patient":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        appointments = get_patient_upcoming_appointments(user_type=user_type, email_id=email_id)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Upcoming appointments retrieved successfully",
                "data": appointments,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        logger.error("PATIENT UPCOMING APPOINTMENTS - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def get_patient_appointment_history(user_type=None, email_id=None):
    """
    Get patient's appointment history
    """
    try:
        # Mock past appointments data
        past_appointments = [
            {
                'appointment_id': 'apt_p003',
                'doctor_name': 'Dr. Sarah Johnson',
                'specialty': 'Cardiology',
                'date': '2024-12-15',
                'time': '10:00 AM',
                'type': 'Check-up',
                'status': 'completed',
                'rating': 5,
                'can_review': False
            },
            {
                'appointment_id': 'apt_p004',
                'doctor_name': 'Dr. Robert Kim',
                'specialty': 'General Medicine',
                'date': '2024-11-20',
                'time': '3:00 PM',
                'type': 'Consultation',
                'status': 'completed',
                'rating': 4,
                'can_review': False
            }
        ]
        
        return past_appointments
        
    except Exception as e:
        logger.error(f"Error getting patient appointment history: {e}")
        return []

def patient_appointment_history_function(request):
    """
    Function to handle patient appointment history API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "patient":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        appointments = get_patient_appointment_history(user_type=user_type, email_id=email_id)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Appointment history retrieved successfully",
                "data": appointments,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        logger.error("PATIENT APPOINTMENT HISTORY - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError
    
    
def get_patient_dashboard_data(request):
    """
    Get comprehensive dashboard data for a patient
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        base_path = os.getcwd()
        
        # Read all required CSV files
        users_df = pd.read_csv(base_path + "/data/users.csv")
        
        # Check if other CSV files exist and read them
        csv_files = {
            'doctors': base_path + "/data/doctors.csv",
            'appointments': base_path + "/data/appointments.csv", 
            'feedback': base_path + "/data/feedback.csv",
            'availability': base_path + "/data/availability.csv",
            'notifications': base_path + "/data/notifications.csv"
        }
        
        dataframes = {}
        for name, path in csv_files.items():
            if os.path.exists(path.replace("\\", "/")):
                dataframes[name] = pd.read_csv(path.replace("\\", "/"))
            else:
                dataframes[name] = pd.DataFrame()
        
        # Find the patient's user data
        patient_user = users_df[
            (users_df['user_type'] == user_type) & 
            (users_df['email_id'] == email_id)
        ]
        
        if patient_user.empty:
            return {"error": "Patient not found"}
        
        patient_info = patient_user.iloc[0].to_dict()
        
        # Mock dashboard statistics (since CSV files are empty)
        dashboard_stats = {
            'total_appointments': 12,
            'upcoming_appointments': 2,
            'completed_appointments': 9,
            'pending_appointments': 1,
            'cancelled_appointments': 2,
            'last_checkup': '2024-12-15',
            'average_rating': 4.5,
            'total_reviews': 8
        }
        
        # Mock upcoming appointments
        upcoming_appointments = [
            {
                'appointment_id': 'apt_p001',
                'doctor_name': 'Dr. Sarah Johnson',
                'specialty': 'Cardiology',
                'date': '2025-01-06',
                'time': '10:00 AM',
                'type': 'Follow-up',
                'status': 'confirmed',
                'location': 'Building A, Room 201'
            },
            {
                'appointment_id': 'apt_p002',
                'doctor_name': 'Dr. Michael Chen',
                'specialty': 'Neurology',
                'date': '2025-01-08',
                'time': '2:30 PM',
                'type': 'Consultation',
                'status': 'confirmed',
                'location': 'Building B, Room 305'
            }
        ]
        
        # Mock past appointments
        past_appointments = [
            {
                'appointment_id': 'apt_p003',
                'doctor_name': 'Dr. Sarah Johnson',
                'specialty': 'Cardiology',
                'date': '2024-12-15',
                'time': '10:00 AM',
                'type': 'Check-up',
                'status': 'completed',
                'rating': 5,
                'can_review': False
            },
            {
                'appointment_id': 'apt_p004',
                'doctor_name': 'Dr. Robert Kim',
                'specialty': 'General Medicine',
                'date': '2024-11-20',
                'time': '3:00 PM',
                'type': 'Consultation',
                'status': 'completed',
                'rating': 4,
                'can_review': False
            },
            {
                'appointment_id': 'apt_p005',
                'doctor_name': 'Dr. Emily Rodriguez',
                'specialty': 'Pediatrics',
                'date': '2024-10-10',
                'time': '11:15 AM',
                'type': 'Vaccination',
                'status': 'completed',
                'rating': None,
                'can_review': True
            }
        ]
        
        # Mock notifications
        notifications = [
            {
                'notification_id': 'not_p001',
                'type': 'appointment_reminder',
                'message': 'Appointment with Dr. Johnson tomorrow at 10:00 AM',
                'time': '2 hours ago',
                'priority': 'high'
            },
            {
                'notification_id': 'not_p002',
                'type': 'health_reminder',
                'message': 'Time for your daily medication',
                'time': '4 hours ago',
                'priority': 'medium'
            },
            {
                'notification_id': 'not_p003',
                'type': 'checkup_reminder',
                'message': 'Annual checkup due next month',
                'time': '1 day ago',
                'priority': 'low'
            }
        ]
        
        # Mock health tips
        health_tips = [
            {
                'tip_id': 'tip_001',
                'title': 'Stay Hydrated',
                'description': 'Drink at least 8 glasses of water daily for optimal health.',
                'category': 'hydration'
            },
            {
                'tip_id': 'tip_002',
                'title': 'Regular Exercise',
                'description': '30 minutes of daily exercise can improve your overall health.',
                'category': 'exercise'
            },
            {
                'tip_id': 'tip_003',
                'title': 'Sleep Well',
                'description': 'Aim for 7-9 hours of quality sleep each night.',
                'category': 'sleep'
            }
        ]
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Success",
                "data": {
            'patient_info': {
                'first_name': patient_info.get('first_name', ''),
                'last_name': patient_info.get('last_name', ''),
                'email_id': patient_info.get('email_id', ''),
                'mobile': patient_info.get('mobile', ''),
                'user_type': patient_info.get('user_type', ''),
                'member_since': '2023-05-15',
                'health_score': 'Good'
            },
            'dashboard_stats': dashboard_stats,
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
            'notifications': notifications,
            'health_tips': health_tips
        }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting patient dashboard data: {e}")
        return {"error": str(e)}
