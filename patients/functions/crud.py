import json
import logging
import os
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from medicare_capstone.utils import custom_exceptions as ce
from patients.common import messages as app_messages
from django.conf import settings

# Get an instance of logger
logger = logging.getLogger("doctors")

# Path to data files
DATA_DIR = os.path.join(settings.BASE_DIR, 'data')


def load_json_file(filename):
    """Load JSON data from file"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        file_path = file_path.replace("\\", "/")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {filename}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return {}


def save_json_file(filename, data):
    """Save JSON data to file"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        file_path = file_path.replace("\\", "/")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False


def get_departments_function():
    """
    Get all departments with their specialties
    """
    try:
        # Load departments data
        data = load_json_file('departments.json')
        
        if not data:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": app_messages.DEPARTMENTS_NOT_FOUND,
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        departments = data.get('departments', [])
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": app_messages.DEPARTMENTS_RETRIEVED_SUCCESSFULLY,
                "departments": departments,
                "total": len(departments)
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("DOCTORS - FUNCTION HELPER - GET DEPARTMENTS - {}".format(e))
        raise ce.InternalServerError


def search_doctors_function(request):
    """
    Search doctors by department and specialty
    """
    try:
        department = request.data.get("department", "").strip()
        specialty = request.data.get("specialty", "").strip()
        
        # Load doctors data
        doctors_data = load_json_file('doctors.json')
        
        if not doctors_data:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": app_messages.DOCTORS_NOT_FOUND,
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        doctors = doctors_data.get('doctors', [])
        filtered_doctors = doctors
        
        # Filter by department if provided
        if department:
            filtered_doctors = [
                doctor for doctor in filtered_doctors 
                if doctor.get('department', '').lower() == department.lower()
            ]
        
        # Filter by specialty if provided
        if specialty:
            filtered_doctors = [
                doctor for doctor in filtered_doctors 
                if doctor.get('specialty', '').lower() == specialty.lower()
            ]
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": app_messages.DOCTORS_RETRIEVED_SUCCESSFULLY,
                "doctors": filtered_doctors,
                "total": len(filtered_doctors)
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("DOCTORS - FUNCTION HELPER - SEARCH DOCTORS - {}".format(e))
        raise ce.InternalServerError


def get_doctor_slots_function(request):
    """
    Get available slots for a doctor on a specific date
    """
    try:
        doctor_id = request.data.get("doctor_id")
        date_str = request.data.get("date")
        
        # Validate date format
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": app_messages.INVALID_DATE_FORMAT,
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Load doctors data
        doctors_data = load_json_file('doctors.json')
        if not doctors_data:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": app_messages.DOCTORS_NOT_FOUND,
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Find the doctor
        doctor = None
        for doc in doctors_data.get('doctors', []):
            if doc['id'] == doctor_id:
                doctor = doc
                break
        
        if not doctor:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": app_messages.DOCTOR_NOT_FOUND,
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Get the day of week for the requested date
        day_name = date_obj.strftime('%A').lower()
        
        # Check if doctor works on this day
        working_hours = doctor.get('working_hours', {}).get(day_name)
        if not working_hours:
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": app_messages.DOCTOR_NOT_AVAILABLE_ON_THIS_DAY,
                    "slots": [],
                    "doctor_name": f"{doctor['first_name']} {doctor['last_name']}",
                    "date": date_str
                },
                status=status.HTTP_200_OK,
            )
        
        # Load appointments data
        appointments_data = load_json_file('appointments.json')
        existing_appointments = appointments_data.get('appointments', [])
        
        # Generate time slots
        slots = []
        try:
            start_time = datetime.strptime(working_hours['start'], '%H:%M')
            end_time = datetime.strptime(working_hours['end'], '%H:%M')
            slot_duration = doctor.get('slot_duration', 30)
            
            current_time = start_time
            while current_time < end_time:
                time_str = current_time.strftime('%H:%M')
                
                # Check if slot is already booked
                is_booked = False
                for appointment in existing_appointments:
                    if (appointment.get('doctor_id') == doctor_id and 
                        appointment.get('date') == date_str and 
                        appointment.get('time_slot') == time_str and
                        appointment.get('status') != 'cancelled'):
                        is_booked = True
                        break
                
                slots.append({
                    'time': time_str,
                    'available': not is_booked
                })
                
                current_time += timedelta(minutes=slot_duration)
                
        except Exception as e:
            logger.error(f"Error generating time slots: {e}")
            raise ce.InternalServerError
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": app_messages.SLOTS_RETRIEVED_SUCCESSFULLY,
                "slots": slots,
                "doctor_name": f"{doctor['first_name']} {doctor['last_name']}",
                "date": date_str
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("DOCTORS - FUNCTION HELPER - GET DOCTOR SLOTS - {}".format(e))
        raise ce.InternalServerError


def book_appointment_function(request):
    """
    Book an appointment
    """
    try:
        doctor_id = request.data.get("doctor_id")
        patient_email = request.data.get("patient_email")
        date_str = request.data.get("date")
        time_slot = request.data.get("time_slot")
        appointment_type = request.data.get("type", "Consultation")
        
        # Load appointments data
        appointments_data = load_json_file('appointments.json')
        appointments = appointments_data.get('appointments', [])
        
        # Check if slot is already booked
        for appointment in appointments:
            if (appointment.get('doctor_id') == doctor_id and 
                appointment.get('date') == date_str and 
                appointment.get('time_slot') == time_slot and
                appointment.get('status') != 'cancelled'):
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": app_messages.SLOT_ALREADY_BOOKED,
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Generate new appointment ID
        new_id = 1
        if appointments:
            new_id = max([apt.get('id', 0) for apt in appointments]) + 1
        
        # Create new appointment
        new_appointment = {
            'id': new_id,
            'doctor_id': doctor_id,
            'patient_email': patient_email,
            'date': date_str,
            'time_slot': time_slot,
            'status': 'confirmed',
            'type': appointment_type,
            'created_at': datetime.now().isoformat()
        }
        
        # Add to appointments list
        appointments.append(new_appointment)
        appointments_data['appointments'] = appointments
        
        # Save to file
        if not save_json_file('appointments.json', appointments_data):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": app_messages.FAILED_TO_SAVE_APPOINTMENT,
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": app_messages.APPOINTMENT_BOOKED_SUCCESSFULLY,
                "appointment": new_appointment
            },
            status=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("DOCTORS - FUNCTION HELPER - BOOK APPOINTMENT - {}".format(e))
        raise ce.InternalServerError