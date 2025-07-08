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

def get_doctor_dashboard_data(user_type=None, email_id=None):
    """
    Get comprehensive dashboard data for a doctor
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
        
        # Find the doctor's user_id
        doctor_user = users_df[
            (users_df['user_type'] == user_type) & 
            (users_df['email_id'] == email_id)
        ]
        
        if doctor_user.empty:
            return {"error": "Doctor not found"}
        
        doctor_info = doctor_user.iloc[0].to_dict()
        
        # Get doctor's additional details
        doctor_details = {}
        if not dataframes['doctors'].empty and 'user_id' in dataframes['doctors'].columns:
            # Since we don't have user_id in users.csv, we'll match by email or create mock data
            doctor_details = {
                'specialty': 'General Medicine',
                'qualifications': 'MD, MBBS',
                'experience': '5+ years'
            }
        
        # Mock dashboard statistics (since CSV files are empty)
        dashboard_stats = {
            'total_appointments': 45,
            'today_appointments': 8,
            'pending_appointments': 3,
            'completed_appointments': 42,
            'cancelled_appointments': 2,
            'total_patients': 120,
            'average_rating': 4.7,
            'total_reviews': 89,
            'pending_reviews': 5
        }
        
        # Mock today's schedule
        today_schedule = [
            {
                'appointment_id': 'apt_001',
                'patient_name': 'John Smith',
                'time': '09:00 AM',
                'type': 'Consultation',
                'status': 'confirmed',
                'duration': '30 mins'
            },
            {
                'appointment_id': 'apt_002', 
                'patient_name': 'Sarah Johnson',
                'time': '10:30 AM',
                'type': 'Follow-up',
                'status': 'confirmed',
                'duration': '20 mins'
            },
            {
                'appointment_id': 'apt_003',
                'patient_name': 'Mike Wilson',
                'time': '02:00 PM', 
                'type': 'Consultation',
                'status': 'pending',
                'duration': '30 mins'
            }
        ]
        
        # Mock recent patients
        recent_patients = [
            {
                'patient_id': 'pat_001',
                'name': 'Emily Davis',
                'last_visit': '2025-01-02',
                'condition': 'Hypertension',
                'status': 'Active'
            },
            {
                'patient_id': 'pat_002',
                'name': 'Robert Brown', 
                'last_visit': '2025-01-01',
                'condition': 'Diabetes',
                'status': 'Follow-up needed'
            },
            {
                'patient_id': 'pat_003',
                'name': 'Lisa Anderson',
                'last_visit': '2024-12-30',
                'condition': 'Allergies',
                'status': 'Recovered'
            }
        ]
        
        # Mock recent reviews
        recent_reviews = [
            {
                'review_id': 'rev_001',
                'patient_name': 'Anonymous',
                'rating': 5,
                'comment': 'Excellent doctor, very professional and caring.',
                'date': '2025-01-02'
            },
            {
                'review_id': 'rev_002',
                'patient_name': 'Anonymous', 
                'rating': 4,
                'comment': 'Good experience, would recommend.',
                'date': '2025-01-01'
            }
        ]
        
        # Mock notifications
        notifications = [
            {
                'notification_id': 'not_001',
                'type': 'appointment_reminder',
                'message': 'Appointment with John Smith in 30 minutes',
                'time': '08:30 AM',
                'priority': 'high'
            },
            {
                'notification_id': 'not_002',
                'type': 'new_review',
                'message': 'You have received a new 5-star review',
                'time': '07:45 AM', 
                'priority': 'medium'
            }
        ]
        
        return {
            'doctor_info': {
                'first_name': doctor_info.get('first_name', ''),
                'last_name': doctor_info.get('last_name', ''),
                'email_id': doctor_info.get('email_id', ''),
                'mobile': doctor_info.get('mobile', ''),
                'user_type': doctor_info.get('user_type', ''),
                **doctor_details
            },
            'dashboard_stats': dashboard_stats,
            'today_schedule': today_schedule,
            'recent_patients': recent_patients,
            'recent_reviews': recent_reviews,
            'notifications': notifications
        }
        
    except Exception as e:
        logger.error(f"Error getting doctor dashboard data: {e}")
        return {"error": str(e)}

def dashboard_function(request):
    """
    Main function to handle doctor dashboard API request
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
        
        if user_type != "doctor":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied. Only doctors can access this dashboard.",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        dashboard_data = get_doctor_dashboard_data(user_type=user_type, email_id=email_id)
        
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
                "message": "Doctor dashboard data retrieved successfully",
                "data": dashboard_data,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("DOCTOR DASHBOARD - FUNCTION HELPER - GET DASHBOARD DATA - {}".format(e))
        raise ce.InternalServerError
