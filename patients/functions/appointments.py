# patients/functions/appointments.py

import json
import os
import logging
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
import uuid

# Get an instance of logger
logger = logging.getLogger("backend_patient_appointments")

def load_json_data(filename):
    """
    Load data from JSON file
    """
    try:
        base_path = os.getcwd()
        file_path = os.path.join(base_path, "data", filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            logger.warning(f"File not found at {file_path}")
            return {} if filename == "appointments.json" else []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filename}: {e}")
        return {} if filename == "appointments.json" else []
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return {} if filename == "appointments.json" else []

def save_json_data(filename, data):
    """
    Save data to JSON file
    """
    try:
        base_path = os.getcwd()
        file_path = os.path.join(base_path, "data", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

def get_doctors_by_department_data(request):
    """
    Get doctors filtered by department and specialty
    """
    try:
        department = request.GET.get('department', '').strip()
        specialty = request.GET.get('specialty', '').strip()
        
        # Load doctors data
        doctors_data = load_json_data("doctors.json")
        doctors = doctors_data.get("doctors", [])
        
        # Filter by department if specified
        if department and department.lower() != 'all':
            doctors = [doc for doc in doctors if doc.get('department', '').lower() == department.lower()]
        
        # Filter by specialty if specified
        if specialty and specialty.lower() != 'all':
            doctors = [doc for doc in doctors if doc.get('specialty', '').lower() == specialty.lower()]
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Doctors retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "doctors": doctors,
                    "total_count": len(doctors)
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting doctors by department: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_departments_data(request):
    """
    Get all available departments
    """
    try:
        # Load departments data
        departments_data = load_json_data("departments.json")
        departments = departments_data.get("departments", [])
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Departments retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "departments": departments
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting departments: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_doctor_profile_data(request, doctor_id):
    """
    Get detailed doctor profile
    """
    try:
        # Load doctors data
        doctors_data = load_json_data("doctors.json")
        doctors = doctors_data.get("doctors", [])
        
        # Find doctor by ID
        doctor = next((doc for doc in doctors if doc.get('id') == int(doctor_id)), None)
        
        if not doctor:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Doctor not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Doctor profile retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": doctor
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting doctor profile: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_doctor_slots_data(request):
    """
    Get available time slots for a doctor on a specific date
    """
    try:
        doctor_id = request.GET.get('doctor_id')
        date = request.GET.get('date')
        
        if not doctor_id or not date:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "doctor_id and date are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load doctors data
        doctors_data = load_json_data("doctors.json")
        doctors = doctors_data.get("doctors", [])
        
        # Find doctor
        doctor = next((doc for doc in doctors if doc.get('id') == int(doctor_id)), None)
        
        if not doctor:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Doctor not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parse date and get day of week
        try:
            appointment_date = datetime.fromisoformat(date)
            day_name = appointment_date.strftime('%A').lower()
        except ValueError:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "Invalid date format. Use YYYY-MM-DD",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get doctor's working hours for the day
        working_hours = doctor.get('working_hours', {})
        day_schedule = working_hours.get(day_name)
        
        if not day_schedule or not day_schedule.get('start') or not day_schedule.get('end'):
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "No available slots - doctor not working on this day",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "slots": []
                    }
                },
                status=status.HTTP_200_OK
            )
        
        # Generate time slots
        start_time = datetime.strptime(day_schedule['start'], '%H:%M').time()
        end_time = datetime.strptime(day_schedule['end'], '%H:%M').time()
        slot_duration = doctor.get('slot_duration', 30)  # Default 30 minutes
        
        # Load existing appointments to check availability
        appointments_data = load_json_data("appointments.json")
        existing_appointments = appointments_data.get("appointments", [])
        
        # Filter appointments for this doctor and date
        doctor_appointments = [
            apt for apt in existing_appointments 
            if apt.get('doctor_id') == int(doctor_id) and 
            apt.get('date') == date and 
            apt.get('status') in ['confirmed', 'pending']
        ]
        
        booked_times = [apt.get('time') for apt in doctor_appointments]
        
        # Generate available slots
        slots = []
        current_time = datetime.combine(appointment_date.date(), start_time)
        end_datetime = datetime.combine(appointment_date.date(), end_time)
        
        while current_time + timedelta(minutes=slot_duration) <= end_datetime:
            time_str = current_time.strftime('%H:%M')
            is_available = time_str not in booked_times
            
            slots.append({
                "time": time_str,
                "available": is_available
            })
            
            current_time += timedelta(minutes=slot_duration)
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Time slots retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "slots": slots,
                    "doctor_name": f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}",
                    "date": date,
                    "working_hours": day_schedule
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting doctor slots: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def book_appointment_data(request):
    """
    Book a new appointment
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        doctor_id = request.data.get("doctor_id")
        date = request.data.get("date")
        time = request.data.get("time")
        appointment_type = request.data.get("type", "consultation")
        notes = request.data.get("notes", "")
        
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
        
        if user_type != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only patients can book appointments.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not all([doctor_id, date, time]):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "doctor_id, date, and time are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load necessary data
        doctors_data = load_json_data("doctors.json")
        doctors = doctors_data.get("doctors", [])
        profiles_data = load_json_data("profiles.json")
        appointments_data = load_json_data("appointments.json")
        
        if "appointments" not in appointments_data:
            appointments_data["appointments"] = []
        
        # Find doctor
        doctor = next((doc for doc in doctors if doc.get('id') == int(doctor_id)), None)
        if not doctor:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Doctor not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find patient profile
        patient_profile = profiles_data.get(email_id)
        if not patient_profile or patient_profile.get('user_type') != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Patient profile not found",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if slot is available
        existing_appointment = next((
            apt for apt in appointments_data["appointments"]
            if apt.get('doctor_id') == int(doctor_id) and
            apt.get('date') == date and
            apt.get('time') == time and
            apt.get('status') in ['confirmed', 'pending']
        ), None)
        
        if existing_appointment:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_409_CONFLICT,
                    "error": "Time slot is already booked",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Create new appointment
        appointment_id = str(uuid.uuid4())
        new_appointment = {
            "id": appointment_id,
            "patient_email": email_id,
            "patient_name": f"{patient_profile.get('first_name', '')} {patient_profile.get('last_name', '')}",
            "doctor_id": int(doctor_id),
            "doctor_name": f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}",
            "department": doctor.get('department', ''),
            "specialty": doctor.get('specialty', ''),
            "date": date,
            "time": time,
            "type": appointment_type,
            "notes": notes,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "consultation_fee": doctor.get('consultation_fee', 0),
            "location": doctor.get('location', '')
        }
        
        # Add appointment to data
        appointments_data["appointments"].append(new_appointment)
        
        # Save appointments data
        if save_json_data("appointments.json", appointments_data):
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Appointment booked successfully",
                    "timestamp": datetime.now().isoformat(),
                    "data": new_appointment
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Failed to save appointment",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_patient_appointments_data(request):
    """
    Get patient's appointments
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        appointment_type = request.GET.get('type', 'all')  # all, upcoming, past
        
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
        
        if user_type != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only patients can view patient appointments.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load appointments data
        appointments_data = load_json_data("appointments.json")
        all_appointments = appointments_data.get("appointments", [])
        
        # Filter patient's appointments
        patient_appointments = [
            apt for apt in all_appointments
            if apt.get('patient_email', '').lower() == email_id
        ]
        
        # Filter by type
        current_date = datetime.now().date()
        
        if appointment_type == 'upcoming':
            patient_appointments = [
                apt for apt in patient_appointments
                if datetime.fromisoformat(apt.get('date', '')).date() >= current_date and
                apt.get('status') in ['confirmed', 'pending']
            ]
        elif appointment_type == 'past':
            patient_appointments = [
                apt for apt in patient_appointments
                if datetime.fromisoformat(apt.get('date', '')).date() < current_date or
                apt.get('status') in ['completed', 'cancelled']
            ]
        
        # Sort appointments by date and time
        patient_appointments.sort(
            key=lambda x: (x.get('date', ''), x.get('time', ''))
        )
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Patient appointments retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "appointments": patient_appointments,
                    "total_count": len(patient_appointments)
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting patient appointments: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def update_appointment_data(request, appointment_id):
    """
    Update/Cancel/Reschedule appointment
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        action = request.data.get("action", "").lower()  # cancel, reschedule, update
        new_date = request.data.get("new_date")
        new_time = request.data.get("new_time")
        new_notes = request.data.get("notes")
        
        # Validate input
        if not user_type or not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type and email_id are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_type != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only patients can update appointments.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load appointments data
        appointments_data = load_json_data("appointments.json")
        appointments = appointments_data.get("appointments", [])
        
        # Find appointment
        appointment_index = next((
            index for index, apt in enumerate(appointments)
            if apt.get('id') == appointment_id and apt.get('patient_email', '').lower() == email_id
        ), None)
        
        if appointment_index is None:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Appointment not found or access denied",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        appointment = appointments[appointment_index]
        
        # Check if appointment can be modified
        if appointment.get('status') in ['completed', 'cancelled']:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "Cannot modify completed or cancelled appointments",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle different actions
        if action == 'cancel':
            appointment['status'] = 'cancelled'
            appointment['updated_at'] = datetime.now().isoformat()
            message = "Appointment cancelled successfully"
            
        elif action == 'reschedule':
            if not new_date or not new_time:
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "error": "new_date and new_time are required for rescheduling",
                        "timestamp": datetime.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if new slot is available
            existing_appointment = next((
                apt for apt in appointments
                if apt.get('doctor_id') == appointment.get('doctor_id') and
                apt.get('date') == new_date and
                apt.get('time') == new_time and
                apt.get('status') in ['confirmed', 'pending'] and
                apt.get('id') != appointment_id
            ), None)
            
            if existing_appointment:
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_409_CONFLICT,
                        "error": "New time slot is already booked",
                        "timestamp": datetime.now().isoformat()
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            appointment['date'] = new_date
            appointment['time'] = new_time
            appointment['updated_at'] = datetime.now().isoformat()
            message = "Appointment rescheduled successfully"
            
        elif action == 'update':
            if new_notes is not None:
                appointment['notes'] = new_notes
            appointment['updated_at'] = datetime.now().isoformat()
            message = "Appointment updated successfully"
            
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "Invalid action. Use 'cancel', 'reschedule', or 'update'",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment in data
        appointments[appointment_index] = appointment
        appointments_data["appointments"] = appointments
        
        # Save updated data
        if save_json_data("appointments.json", appointments_data):
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "data": appointment
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Failed to save appointment updates",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error updating appointment: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        
def submit_feedback_data(request):
    """
    Submit feedback/rating for a completed appointment
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        appointment_id = request.data.get("appointment_id")
        doctor_id = request.data.get("doctor_id")
        rating = request.data.get("rating")
        category = request.data.get("category", "overall")
        comment = request.data.get("comment", "")
        would_recommend = request.data.get("would_recommend", "")
        
        # Validate input
        if not user_type or not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type and email_id are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_type != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only patients can submit feedback.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not all([appointment_id, doctor_id, rating, comment]):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "appointment_id, doctor_id, rating, and comment are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "Rating must be a number between 1 and 5",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load necessary data
        appointments_data = load_json_data("appointments.json")
        feedback_data = load_json_data("feedback.json")
        
        if "feedback" not in feedback_data:
            feedback_data["feedback"] = []
        
        # Find the appointment
        appointment = next((
            apt for apt in appointments_data.get("appointments", [])
            if apt.get('id') == appointment_id and apt.get('patient_email', '').lower() == email_id
        ), None)
        
        if not appointment:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Appointment not found or access denied",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if appointment is completed
        if appointment.get('status') != 'completed':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "Can only rate completed appointments",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if feedback already exists
        existing_feedback = next((
            fb for fb in feedback_data["feedback"]
            if fb.get('appointment_id') == appointment_id
        ), None)
        
        if existing_feedback:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_409_CONFLICT,
                    "error": "Feedback already submitted for this appointment",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Create feedback entry
        feedback_id = str(uuid.uuid4())
        new_feedback = {
            "id": feedback_id,
            "appointment_id": appointment_id,
            "patient_email": email_id,
            "patient_name": appointment.get('patient_name', ''),
            "doctor_id": int(doctor_id),
            "doctor_name": appointment.get('doctor_name', ''),
            "department": appointment.get('department', ''),
            "specialty": appointment.get('specialty', ''),
            "rating": rating,
            "category": category,
            "comment": comment.strip(),
            "would_recommend": would_recommend,
            "appointment_date": appointment.get('date', ''),
            "appointment_time": appointment.get('time', ''),
            "feedback_date": datetime.now().strftime('%Y-%m-%d'),
            "feedback_time": datetime.now().strftime('%H:%M:%S'),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Add feedback to data
        feedback_data["feedback"].append(new_feedback)
        
        # Update appointment to mark as rated
        for apt in appointments_data.get("appointments", []):
            if apt.get('id') == appointment_id:
                apt['rated'] = True
                apt['rating'] = rating
                apt['updated_at'] = datetime.now().isoformat()
                break
        
        # Save both files
        feedback_saved = save_json_data("feedback.json", feedback_data)
        appointments_saved = save_json_data("appointments.json", appointments_data)
        
        if feedback_saved and appointments_saved:
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Feedback submitted successfully",
                    "timestamp": datetime.now().isoformat(),
                    "data": new_feedback
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Failed to save feedback",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_feedback_history_data(request):
    """
    Get patient's feedback history
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        
        # Validate input
        if not user_type or not email_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type and email_id are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_type != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only patients can view feedback history.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load feedback data
        feedback_data = load_json_data("feedback.json")
        all_feedback = feedback_data.get("feedback", [])
        
        # Filter patient's feedback
        patient_feedback = [
            fb for fb in all_feedback
            if fb.get('patient_email', '').lower() == email_id and fb.get('status') == 'active'
        ]
        
        # Sort by date (most recent first)
        patient_feedback.sort(
            key=lambda x: (x.get('feedback_date', ''), x.get('feedback_time', '')),
            reverse=True
        )
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Feedback history retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "feedback": patient_feedback,
                    "total_count": len(patient_feedback)
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting feedback history: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def update_feedback_data(request):
    """
    Update existing feedback
    """
    try:
        user_type = request.data.get("user_type", "").lower()
        email_id = request.data.get("email_id", "").lower()
        feedback_id = request.data.get("feedback_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        would_recommend = request.data.get("would_recommend")
        
        # Validate input
        if not user_type or not email_id or not feedback_id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "error": "user_type, email_id, and feedback_id are required",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_type != 'patient':
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "error": "Access denied. Only patients can update feedback.",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Load feedback data
        feedback_data = load_json_data("feedback.json")
        feedback_list = feedback_data.get("feedback", [])
        
        # Find feedback
        feedback_index = next((
            index for index, fb in enumerate(feedback_list)
            if fb.get('id') == feedback_id and fb.get('patient_email', '').lower() == email_id
        ), None)
        
        if feedback_index is None:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Feedback not found or access denied",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        feedback = feedback_list[feedback_index]
        
        # Update feedback fields
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5")
                feedback['rating'] = rating
            except (ValueError, TypeError):
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "error": "Rating must be a number between 1 and 5",
                        "timestamp": datetime.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if comment is not None:
            feedback['comment'] = comment.strip()
        
        if would_recommend is not None:
            feedback['would_recommend'] = bool(would_recommend)
        
        feedback['updated_at'] = datetime.now().isoformat()
        
        # Update feedback in data
        feedback_list[feedback_index] = feedback
        feedback_data["feedback"] = feedback_list
        
        # Save updated data
        if save_json_data("feedback.json", feedback_data):
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Feedback updated successfully",
                    "timestamp": datetime.now().isoformat(),
                    "data": feedback
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Failed to save feedback updates",
                    "timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
