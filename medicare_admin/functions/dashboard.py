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

def get_admin_dashboard_data(request):
    """
    Get comprehensive dashboard data for an admin
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
            'notifications': base_path + "/data/notifications.csv",
            'admin_responses': base_path + "/data/admin_responses.csv",
            'user_roles': base_path + "/data/user_roles.csv",
            'roles': base_path + "/data/roles.csv"
        }
        
        dataframes = {}
        for name, path in csv_files.items():
            if os.path.exists(path.replace("\\", "/")):
                dataframes[name] = pd.read_csv(path.replace("\\", "/"))
            else:
                dataframes[name] = pd.DataFrame()
        
        # Find the admin's user data
        admin_user = users_df[
            (users_df['user_type'] == user_type) & 
            (users_df['email_id'] == email_id)
        ]
        
        if admin_user.empty:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Administrator not found",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        admin_info = admin_user.iloc[0].to_dict()
        
        # Calculate dashboard statistics from CSV data or use mock data
        # Since CSV files are empty, using mock data
        dashboard_stats = {
            'total_appointments': 1247,
            'today_appointments': 23,
            'completed_appointments': 1089,
            'pending_appointments': 45,
            'cancelled_appointments': 113,
            'total_doctors': 28,
            'active_doctors': 25,
            'total_patients': 5420,
            'average_rating': 4.6,
            'total_feedback': 892,
            'pending_feedback': 15,
            'monthly_revenue': 125000,
            'patient_satisfaction': 94,
            'system_uptime': 99.9
        }
        
        # Mock recent appointments across all doctors
        recent_appointments = [
            {
                'appointment_id': 'apt_a001',
                'patient_name': 'John Smith',
                'doctor_name': 'Dr. Sarah Johnson',
                'department': 'Cardiology',
                'date': '2025-01-03',
                'time': '10:00 AM',
                'type': 'Consultation',
                'status': 'confirmed'
            },
            {
                'appointment_id': 'apt_a002',
                'patient_name': 'Emily Davis',
                'doctor_name': 'Dr. Michael Chen',
                'department': 'Neurology',
                'date': '2025-01-03',
                'time': '2:30 PM',
                'type': 'Follow-up',
                'status': 'pending'
            },
            {
                'appointment_id': 'apt_a003',
                'patient_name': 'Robert Wilson',
                'doctor_name': 'Dr. Emily Rodriguez',
                'department': 'Pediatrics',
                'date': '2025-01-04',
                'time': '9:15 AM',
                'type': 'Vaccination',
                'status': 'confirmed'
            }
        ]
        
        # Mock recent feedback across all doctors
        recent_feedback = [
            {
                'feedback_id': 'fb_a001',
                'patient_name': 'Alice Johnson',
                'doctor_name': 'Dr. Sarah Johnson',
                'department': 'Cardiology',
                'rating': 5,
                'comment': 'Excellent service! Dr. Johnson was very professional and caring.',
                'date': '2025-01-02',
                'status': 'pending'
            },
            {
                'feedback_id': 'fb_a002',
                'patient_name': 'Mark Thompson',
                'doctor_name': 'Dr. Michael Chen',
                'department': 'Neurology',
                'rating': 4,
                'comment': 'Good experience overall, but the waiting time was a bit long.',
                'date': '2024-12-30',
                'status': 'responded'
            },
            {
                'feedback_id': 'fb_a003',
                'patient_name': 'Sarah Brown',
                'doctor_name': 'Dr. Emily Rodriguez',
                'department': 'Pediatrics',
                'rating': 2,
                'comment': 'Not satisfied with the appointment scheduling system.',
                'date': '2024-12-28',
                'status': 'pending'
            }
        ]
        
        # Mock top performing doctors
        top_doctors = [
            {
                'doctor_id': 'doc_001',
                'name': 'Dr. Sarah Johnson',
                'department': 'Cardiology',
                'patients': 245,
                'rating': 4.8,
                'appointments': 32
            },
            {
                'doctor_id': 'doc_002',
                'name': 'Dr. Michael Chen',
                'department': 'Neurology',
                'patients': 189,
                'rating': 4.9,
                'appointments': 28
            },
            {
                'doctor_id': 'doc_003',
                'name': 'Dr. Emily Rodriguez',
                'department': 'Pediatrics',
                'patients': 156,
                'rating': 4.7,
                'appointments': 24
            }
        ]
        
        # Mock system alerts
        system_alerts = [
            {
                'alert_id': 'alert_001',
                'type': 'warning',
                'title': '15 feedback responses pending',
                'message': 'Some patient feedback requires admin response'
            },
            {
                'alert_id': 'alert_002',
                'type': 'info',
                'title': 'System performance is optimal',
                'message': 'All services are running smoothly'
            },
            {
                'alert_id': 'alert_003',
                'type': 'success',
                'title': 'Daily backup completed',
                'message': 'Data backup was successful'
            }
        ]
        
        # Mock notifications
        notifications = [
            {
                'notification_id': 'not_a001',
                'type': 'system_alert',
                'message': 'New doctor registration requires approval',
                'time': '30 minutes ago',
                'priority': 'high'
            },
            {
                'notification_id': 'not_a002',
                'type': 'report_ready',
                'message': 'Monthly report generation completed',
                'time': '2 hours ago',
                'priority': 'medium'
            },
            {
                'notification_id': 'not_a003',
                'type': 'maintenance',
                'message': 'System maintenance scheduled for tonight',
                'time': '4 hours ago',
                'priority': 'low'
            }
        ]
         
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Dashboard data retrieved successfully",
                "data": {
            'admin_info': {
                'first_name': admin_info.get('first_name', ''),
                'last_name': admin_info.get('last_name', ''),
                'email_id': admin_info.get('email_id', ''),
                'mobile': admin_info.get('mobile', ''),
                'user_type': admin_info.get('user_type', ''),
                'last_login': '2025-01-03T08:30:00',
                'access_level': 'Full Access'
            },
            'dashboard_stats': dashboard_stats,
            'recent_appointments': recent_appointments,
            'recent_feedback': recent_feedback,
            'top_doctors': top_doctors,
            'system_alerts': system_alerts,
            'notifications': notifications
        }
            },
            status=status.HTTP_200_OK
        )
        
        
    except Exception as e:

        import traceback
        traceback.print_exc()
        logger.error(f"Error getting admin dashboard data: {e}")
        return {"error": str(e)}

def admin_dashboard_function(request):
    """
    Main function to handle admin dashboard API request
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
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied. Only administrators can access this dashboard.",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        dashboard_data = get_admin_dashboard_data(user_type=user_type, email_id=email_id)
        
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
                "message": "Admin dashboard data retrieved successfully",
                "data": dashboard_data,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN DASHBOARD - FUNCTION HELPER - GET DASHBOARD DATA - {}".format(e))
        raise ce.InternalServerError

# Additional admin functions

def get_admin_all_appointments(user_type=None, email_id=None):
    """
    Get all appointments for admin management
    """
    try:
        # Mock all appointments data
        all_appointments = [
            {
                'appointment_id': 'apt_a001',
                'patient_name': 'John Smith',
                'doctor_name': 'Dr. Sarah Johnson',
                'department': 'Cardiology',
                'date': '2025-01-03',
                'time': '10:00 AM',
                'type': 'Consultation',
                'status': 'confirmed'
            },
            {
                'appointment_id': 'apt_a002',
                'patient_name': 'Emily Davis',
                'doctor_name': 'Dr. Michael Chen',
                'department': 'Neurology',
                'date': '2025-01-03',
                'time': '2:30 PM',
                'type': 'Follow-up',
                'status': 'pending'
            },
            {
                'appointment_id': 'apt_a003',
                'patient_name': 'Robert Wilson',
                'doctor_name': 'Dr. Emily Rodriguez',
                'department': 'Pediatrics',
                'date': '2025-01-04',
                'time': '9:15 AM',
                'type': 'Vaccination',
                'status': 'confirmed'
            }
        ]
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Success",
                "data": all_appointments
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error getting all appointments: {e}")
        raise
    
def admin_all_appointments_function(request):
    """
    Function to handle admin all appointments API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        appointments = get_admin_all_appointments(user_type=user_type, email_id=email_id)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "All appointments retrieved successfully",
                "data": appointments,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:

        import traceback
        traceback.print_exc()
        logger.error("ADMIN ALL APPOINTMENTS - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def get_admin_all_feedback(user_type=None, email_id=None):
    """
    Get all feedback for admin management
    """
    try:
        # Mock all feedback data
        all_feedback = [
            {
                'feedback_id': 'fb_a001',
                'patient_name': 'Alice Johnson',
                'doctor_name': 'Dr. Sarah Johnson',
                'department': 'Cardiology',
                'rating': 5,
                'comment': 'Excellent service! Dr. Johnson was very professional and caring.',
                'date': '2025-01-02',
                'status': 'pending'
            },
            {
                'feedback_id': 'fb_a002',
                'patient_name': 'Mark Thompson',
                'doctor_name': 'Dr. Michael Chen',
                'department': 'Neurology',
                'rating': 4,
                'comment': 'Good experience overall, but the waiting time was a bit long.',
                'date': '2024-12-30',
                'status': 'responded'
            },
            {
                'feedback_id': 'fb_a003',
                'patient_name': 'Sarah Brown',
                'doctor_name': 'Dr. Emily Rodriguez',
                'department': 'Pediatrics',
                'rating': 2,
                'comment': 'Not satisfied with the appointment scheduling system.',
                'date': '2024-12-28',
                'status': 'pending'
            }
        ]
        
        return all_feedback
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error getting all feedback: {e}")
        return []

def admin_all_feedback_function(request):
    """
    Function to handle admin all feedback API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        feedback_list = get_admin_all_feedback(user_type=user_type, email_id=email_id)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "All feedback retrieved successfully",
                "data": feedback_list,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN ALL FEEDBACK - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def admin_respond_feedback_function(request):
    """
    Function to handle admin respond to feedback API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        feedback_id = request.data.get("feedback_id")
        response_text = request.data.get("response_text")
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        if not feedback_id or not response_text:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "feedback_id and response_text are required",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # In a real implementation, you would save this to CSV/database
        # For now, just return success
        response_data = {
            'response_id': str(uuid.uuid4()),
            'feedback_id': feedback_id,
            'admin_email': email_id,
            'response_text': response_text,
            'responded_at': datetime.datetime.now().isoformat()
        }
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Response submitted successfully",
                "data": response_data,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN RESPOND FEEDBACK - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def get_admin_analytics(user_type=None, email_id=None):
    """
    Get system analytics for admin
    """
    try:
        # Mock analytics data
        analytics_data = {
            'total_appointments': 1247,
            'today_appointments': 23,
            'completed_appointments': 1089,
            'pending_appointments': 45,
            'cancelled_appointments': 113,
            'total_doctors': 28,
            'active_doctors': 25,
            'total_patients': 5420,
            'average_rating': 4.6,
            'total_feedback': 892,
            'pending_feedback': 15,
            'monthly_revenue': 125000,
            'patient_satisfaction': 94,
            'system_uptime': 99.9,
            'monthly_growth': 12.5,
            'doctor_utilization': 85.3,
            'appointment_success_rate': 87.4
        }
        
        return analytics_data
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error getting admin analytics: {e}")
        return {}

def admin_analytics_function(request):
    """
    Function to handle admin analytics API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        analytics = get_admin_analytics(user_type=user_type, email_id=email_id)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "System analytics retrieved successfully",
                "data": analytics,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN ANALYTICS - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def get_admin_doctor_management(user_type=None, email_id=None):
    """
    Get doctor management data for admin
    """
    try:
        base_path = os.getcwd()
        
        # Try to read users CSV to get real doctor data
        users_df = pd.read_csv(base_path + "/data/users.csv")
        doctors_df = pd.DataFrame()
        
        if os.path.exists(base_path + "/data/doctors.csv"):
            doctors_df = pd.read_csv(base_path + "/data/doctors.csv")
        
        # Filter doctors from users
        doctor_users = users_df[users_df['user_type'] == 'doctor']
        
        doctors_list = []
        if not doctor_users.empty:
            for _, doctor in doctor_users.iterrows():
                doctor_data = {
                    'doctor_id': doctor.get('user_id', str(uuid.uuid4())),
                    'name': f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}",
                    'email': doctor.get('email_id', ''),
                    'mobile': doctor.get('mobile', ''),
                    'specialty': 'General Medicine',  # Default since not in CSV
                    'experience': '5+ years',  # Default since not in CSV
                    'qualifications': 'MD, MBBS',  # Default since not in CSV
                    'status': 'active',  # Default since not in CSV
                    'patients': 0,  # Default since not in CSV
                    'rating': 4.5,  # Default since not in CSV
                    'appointments': 0  # Default since not in CSV
                }
                doctors_list.append(doctor_data)
        else:
            # Mock doctor data if no doctors in CSV
            doctors_list = [
                {
                    'doctor_id': 'doc_001',
                    'name': 'Dr. Sarah Johnson',
                    'email': 'sarah.johnson@medicare.com',
                    'mobile': '+1-555-123-4567',
                    'specialty': 'Cardiology',
                    'experience': '8 years',
                    'qualifications': 'MD, FACC',
                    'status': 'active',
                    'patients': 245,
                    'rating': 4.8,
                    'appointments': 32
                },
                {
                    'doctor_id': 'doc_002',
                    'name': 'Dr. Michael Chen',
                    'email': 'michael.chen@medicare.com',
                    'mobile': '+1-555-234-5678',
                    'specialty': 'Neurology',
                    'experience': '12 years',
                    'qualifications': 'MD, PhD',
                    'status': 'active',
                    'patients': 189,
                    'rating': 4.9,
                    'appointments': 28
                },
                {
                    'doctor_id': 'doc_003',
                    'name': 'Dr. Emily Rodriguez',
                    'email': 'emily.rodriguez@medicare.com',
                    'mobile': '+1-555-345-6789',
                    'specialty': 'Pediatrics',
                    'experience': '6 years',
                    'qualifications': 'MD, FAAP',
                    'status': 'inactive',
                    'patients': 156,
                    'rating': 4.7,
                    'appointments': 24
                }
            ]
        
        return doctors_list
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error getting doctor management data: {e}")
        return []

def admin_doctor_management_function(request):
    """
    Function to handle admin doctor management API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        doctors = get_admin_doctor_management(user_type=user_type, email_id=email_id)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Doctor management data retrieved successfully",
                "data": doctors,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN DOCTOR MANAGEMENT - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def admin_add_doctor_function(request):
    """
    Function to handle admin add doctor API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Get doctor data from request
        doctor_data = {
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            'email_id': request.data.get('email_id', ''),
            'mobile': request.data.get('mobile', ''),
            'specialty': request.data.get('specialty', ''),
            'experience': request.data.get('experience', ''),
            'qualifications': request.data.get('qualifications', ''),
            'location': request.data.get('location', ''),
            'status': request.data.get('status', 'active')
        }
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email_id', 'mobile']
        for field in required_fields:
            if not doctor_data.get(field):
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": f"{field} is required",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # In a real implementation, you would save this to CSV
        # For now, just return success with generated ID
        doctor_data['doctor_id'] = str(uuid.uuid4())
        doctor_data['created_at'] = datetime.datetime.now().isoformat()
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "Doctor added successfully",
                "data": doctor_data,
            },
            status=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN ADD DOCTOR - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def admin_update_doctor_function(request):
    """
    Function to handle admin update doctor API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        doctor_id = request.data.get("doctor_id")
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        if not doctor_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "doctor_id is required",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # In a real implementation, you would update the CSV record
        # For now, just return success
        updated_data = {
            'doctor_id': doctor_id,
            'updated_at': datetime.datetime.now().isoformat()
        }
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Doctor updated successfully",
                "data": updated_data,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN UPDATE DOCTOR - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError

def admin_delete_doctor_function(request):
    """
    Function to handle admin delete doctor API request
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        doctor_id = request.data.get("doctor_id")
        
        if user_type != "admin":
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Access denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        if not doctor_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "doctor_id is required",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # In a real implementation, you would delete/deactivate the CSV record
        # For now, just return success
        deleted_data = {
            'doctor_id': doctor_id,
            'deleted_at': datetime.datetime.now().isoformat()
        }
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Doctor deleted successfully",
                "data": deleted_data,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("ADMIN DELETE DOCTOR - FUNCTION HELPER - {}".format(e))
        raise ce.InternalServerError