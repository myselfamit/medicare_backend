import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict

class DoctorDashboardProcessor:
    def __init__(self, csv_directory: str):
        """Initialize with directory containing CSV files"""
        self.csv_dir = csv_directory
        self.load_data()
    
    def load_data(self):
        """Load all CSV files into pandas DataFrames"""
        try:
            self.users_df = pd.read_csv(f"{self.csv_dir}/users.csv")
            self.doctors_df = pd.read_csv(f"{self.csv_dir}/doctors.csv")
            self.availability_df = pd.read_csv(f"{self.csv_dir}/availability.csv")
            self.feedback_df = pd.read_csv(f"{self.csv_dir}/feedback.csv")
            self.admin_responses_df = pd.read_csv(f"{self.csv_dir}/admin_responses.csv")
            self.notifications_df = pd.read_csv(f"{self.csv_dir}/notifications.csv")
            
            # Create mock appointments dataframe since it's not in CSV files
            self.appointments_df = self._generate_appointments_data()
            
        except FileNotFoundError as e:
            print(f"Error loading CSV files: {e}")
            self.initialize_empty_dataframes()
    
    def initialize_empty_dataframes(self):
        """Initialize empty dataframes with proper columns"""
        self.users_df = pd.DataFrame(columns=['first_name', 'last_name', 'email_id', 'password', 'mobile', 'user_type'])
        self.doctors_df = pd.DataFrame(columns=['doctor_id', 'user_id', 'specialty', 'qualifications', 'experience'])
        self.availability_df = pd.DataFrame(columns=['availability_id', 'doctor_id', 'date', 'start_time', 'end_time'])
        self.feedback_df = pd.DataFrame(columns=['feedback_id', 'appointment_id', 'rating', 'comments'])
        self.appointments_df = pd.DataFrame(columns=['appointment_id', 'doctor_id', 'patient_id', 'date', 'time', 'type', 'status', 'notes'])
    
    def _generate_appointments_data(self) -> pd.DataFrame:
        """Generate mock appointments data based on availability"""
        appointments = []
        
        if len(self.availability_df) > 0 and len(self.users_df) > 0:
            patients = self.users_df[self.users_df['user_type'] == 'patient']
            
            for idx, avail in self.availability_df.iterrows():
                # Generate 2-3 appointments per availability slot
                num_appointments = np.random.randint(2, 4)
                
                for i in range(num_appointments):
                    if len(patients) > 0:
                        patient = patients.sample(1).iloc[0]
                        
                        # Parse time and create appointment slots
                        start_time = datetime.strptime(avail['start_time'], '%H:%M:%S').time() if ':' in str(avail['start_time']) else time(9, 0)
                        appointment_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=30*i)).time()
                        
                        appointments.append({
                            'appointment_id': f"APT{idx:03d}{i:02d}",
                            'doctor_id': avail['doctor_id'],
                            'patient_id': patient.name,  # Using index as patient_id
                            'date': avail['date'],
                            'time': appointment_time.strftime('%H:%M'),
                            'type': np.random.choice(['consultation', 'follow-up', 'check-up', 'emergency']),
                            'status': np.random.choice(['confirmed', 'pending', 'completed', 'cancelled'], p=[0.4, 0.2, 0.3, 0.1]),
                            'notes': f"Patient presents with symptoms. Requires {np.random.choice(['examination', 'tests', 'medication'])}"
                        })
        
        return pd.DataFrame(appointments)
    
    def get_doctor_info(self, doctor_email: str) -> Optional[Dict]:
        """Get doctor information by email"""
        doctor_user = self.users_df[self.users_df['email_id'] == doctor_email]
        
        if len(doctor_user) == 0:
            return None
        
        doctor_info = self.doctors_df[self.doctors_df['user_id'] == doctor_user.index[0]]
        
        if len(doctor_info) == 0:
            return None
        
        doctor = pd.concat([doctor_user.iloc[0], doctor_info.iloc[0]])
        return doctor.to_dict()
    
    # 1. DOCTOR DASHBOARD (/doctor)
    def get_doctor_dashboard(self, doctor_email: str) -> Dict[str, Any]:
        """Get main dashboard data for doctor"""
        doctor = self.get_doctor_info(doctor_email)
        if not doctor:
            return {"success": False, "error": "Doctor not found"}
        
        doctor_id = doctor['doctor_id']
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Today's appointments
        today_appointments = self.appointments_df[
            (self.appointments_df['doctor_id'] == doctor_id) & 
            (self.appointments_df['date'] == today)
        ]
        
        # This week's appointments
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
        week_end = (datetime.now() + timedelta(days=6-datetime.now().weekday())).strftime('%Y-%m-%d')
        week_appointments = self.appointments_df[
            (self.appointments_df['doctor_id'] == doctor_id) & 
            (self.appointments_df['date'] >= week_start) & 
            (self.appointments_df['date'] <= week_end)
        ]
        
        # Calculate stats
        total_patients = len(self.appointments_df[self.appointments_df['doctor_id'] == doctor_id]['patient_id'].unique())
        completed_today = len(today_appointments[today_appointments['status'] == 'completed'])
        pending_today = len(today_appointments[today_appointments['status'].isin(['confirmed', 'pending'])])
        
        # Get recent appointments
        recent_appointments = []
        for _, apt in today_appointments.head(5).iterrows():
            patient = self.users_df.loc[apt['patient_id']] if apt['patient_id'] in self.users_df.index else None
            
            recent_appointments.append({
                "id": apt['appointment_id'],
                "patientName": f"{patient['first_name']} {patient['last_name']}" if patient is not None else f"Patient {apt['patient_id']}",
                "time": apt['time'],
                "type": apt['type'],
                "status": apt['status'],
                "notes": apt['notes'] if pd.notna(apt['notes']) else ""
            })
        
        # Calculate ratings
        doctor_feedback = self.feedback_df[self.feedback_df['appointment_id'].isin(
            self.appointments_df[self.appointments_df['doctor_id'] == doctor_id]['appointment_id']
        )]
        
        avg_rating = doctor_feedback['rating'].astype(float).mean() if len(doctor_feedback) > 0 else 4.5
        total_reviews = len(doctor_feedback)
        
        return {
            "success": True,
            "data": {
                "stats": {
                    "todayAppointments": len(today_appointments),
                    "completedToday": completed_today,
                    "pendingToday": pending_today,
                    "weekAppointments": len(week_appointments),
                    "totalPatients": total_patients,
                    "averageRating": round(avg_rating, 1),
                    "totalReviews": total_reviews,
                    "upcomingAppointments": pending_today
                },
                "todaySchedule": recent_appointments,
                "notifications": [
                    {
                        "id": 1,
                        "type": "appointment",
                        "message": f"You have {pending_today} appointments today",
                        "time": "1 hour ago",
                        "read": False
                    },
                    {
                        "id": 2,
                        "type": "review",
                        "message": "New patient review received",
                        "time": "2 hours ago",
                        "read": True
                    }
                ]
            }
        }
    
    # 2. MY SCHEDULE (/doctor/schedule)
    def get_doctor_schedule(self, doctor_email: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get doctor's schedule for a specific date or week"""
        doctor = self.get_doctor_info(doctor_email)
        if not doctor:
            return {"success": False, "error": "Doctor not found"}
        
        doctor_id = doctor['doctor_id']
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get week dates
        target_date = datetime.strptime(date, '%Y-%m-%d')
        week_start = target_date - timedelta(days=target_date.weekday())
        week_dates = [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        # Get availability for the week
        week_availability = self.availability_df[
            (self.availability_df['doctor_id'] == doctor_id) & 
            (self.availability_df['date'].isin(week_dates))
        ]
        
        # Get appointments for the week
        week_appointments = self.appointments_df[
            (self.appointments_df['doctor_id'] == doctor_id) & 
            (self.appointments_df['date'].isin(week_dates))
        ]
        
        # Build schedule
        schedule = {}
        for day_date in week_dates:
            day_name = datetime.strptime(day_date, '%Y-%m-%d').strftime('%A')
            
            # Get availability for this day
            day_avail = week_availability[week_availability['date'] == day_date]
            
            # Get appointments for this day
            day_appointments = week_appointments[week_appointments['date'] == day_date].sort_values('time')
            
            slots = []
            if len(day_avail) > 0:
                avail = day_avail.iloc[0]
                
                # Generate time slots (30-minute intervals)
                start = datetime.strptime(f"{day_date} {avail['start_time']}", '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(f"{day_date} {avail['end_time']}", '%Y-%m-%d %H:%M:%S')
                
                current_time = start
                while current_time < end:
                    time_str = current_time.strftime('%H:%M')
                    
                    # Check if there's an appointment at this time
                    appointment = day_appointments[day_appointments['time'] == time_str]
                    
                    if len(appointment) > 0:
                        apt = appointment.iloc[0]
                        patient = self.users_df.loc[apt['patient_id']] if apt['patient_id'] in self.users_df.index else None
                        
                        slots.append({
                            "time": time_str,
                            "isBooked": True,
                            "appointment": {
                                "id": apt['appointment_id'],
                                "patientName": f"{patient['first_name']} {patient['last_name']}" if patient is not None else f"Patient {apt['patient_id']}",
                                "type": apt['type'],
                                "status": apt['status']
                            }
                        })
                    else:
                        slots.append({
                            "time": time_str,
                            "isBooked": False,
                            "appointment": None
                        })
                    
                    current_time += timedelta(minutes=30)
            
            schedule[day_name] = {
                "date": day_date,
                "isAvailable": len(day_avail) > 0,
                "slots": slots,
                "summary": {
                    "total": len(slots),
                    "booked": len([s for s in slots if s['isBooked']]),
                    "available": len([s for s in slots if not s['isBooked']])
                }
            }
        
        return {
            "success": True,
            "data": {
                "weekStart": week_dates[0],
                "weekEnd": week_dates[6],
                "schedule": schedule,
                "summary": {
                    "totalAppointments": len(week_appointments),
                    "totalHours": sum(len(s['slots']) * 0.5 for s in schedule.values() if s['isAvailable']),
                    "utilizationRate": round(len(week_appointments) / max(sum(len(s['slots']) for s in schedule.values() if s['isAvailable']), 1) * 100, 1)
                }
            }
        }
    
    # 3. APPOINTMENTS (/doctor/appointments)
    def get_doctor_appointments(self, doctor_email: str, 
                               status: Optional[str] = None,
                               date_from: Optional[str] = None,
                               date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get all appointments for doctor with filters"""
        doctor = self.get_doctor_info(doctor_email)
        if not doctor:
            return {"success": False, "error": "Doctor not found"}
        
        doctor_id = doctor['doctor_id']
        
        # Filter appointments
        appointments = self.appointments_df[self.appointments_df['doctor_id'] == doctor_id].copy()
        
        if status and status != 'all':
            appointments = appointments[appointments['status'] == status]
        
        if date_from:
            appointments = appointments[appointments['date'] >= date_from]
        
        if date_to:
            appointments = appointments[appointments['date'] <= date_to]
        
        # Sort by date and time
        appointments = appointments.sort_values(['date', 'time'], ascending=[False, False])
        
        # Build appointment list
        appointment_list = []
        for _, apt in appointments.iterrows():
            patient = self.users_df.loc[apt['patient_id']] if apt['patient_id'] in self.users_df.index else None
            
            # Check if appointment has feedback
            has_feedback = len(self.feedback_df[self.feedback_df['appointment_id'] == apt['appointment_id']]) > 0
            
            appointment_list.append({
                "id": apt['appointment_id'],
                "patientName": f"{patient['first_name']} {patient['last_name']}" if patient is not None else f"Patient {apt['patient_id']}",
                "patientEmail": patient['email_id'] if patient is not None else "",
                "patientPhone": patient['mobile'] if patient is not None else "",
                "date": apt['date'],
                "time": apt['time'],
                "type": apt['type'],
                "status": apt['status'],
                "notes": apt['notes'] if pd.notna(apt['notes']) else "",
                "hasFeedback": has_feedback,
                "duration": "30 mins"  # Default duration
            })
        
        # Group by status for summary
        status_summary = appointments['status'].value_counts().to_dict()
        
        return {
            "success": True,
            "data": {
                "appointments": appointment_list,
                "summary": {
                    "total": len(appointments),
                    "confirmed": status_summary.get('confirmed', 0),
                    "pending": status_summary.get('pending', 0),
                    "completed": status_summary.get('completed', 0),
                    "cancelled": status_summary.get('cancelled', 0)
                },
                "filters": {
                    "status": status or 'all',
                    "dateFrom": date_from,
                    "dateTo": date_to
                }
            }
        }
    
    # 4. MY PATIENTS (/doctor/patients)
    def get_doctor_patients(self, doctor_email: str, search: Optional[str] = None) -> Dict[str, Any]:
        """Get all patients who have appointments with this doctor"""
        doctor = self.get_doctor_info(doctor_email)
        if not doctor:
            return {"success": False, "error": "Doctor not found"}
        
        doctor_id = doctor['doctor_id']
        
        # Get unique patients from appointments
        doctor_appointments = self.appointments_df[self.appointments_df['doctor_id'] == doctor_id]
        patient_ids = doctor_appointments['patient_id'].unique()
        
        patients_list = []
        for patient_id in patient_ids:
            if patient_id in self.users_df.index:
                patient = self.users_df.loc[patient_id]
                
                # Skip if searching and doesn't match
                if search:
                    search_lower = search.lower()
                    if not (search_lower in patient['first_name'].lower() or 
                           search_lower in patient['last_name'].lower() or
                           search_lower in patient['email_id'].lower()):
                        continue
                
                # Get patient's appointments with this doctor
                patient_appointments = doctor_appointments[doctor_appointments['patient_id'] == patient_id]
                
                # Get last appointment
                last_appointment = patient_appointments.sort_values('date', ascending=False).iloc[0] if len(patient_appointments) > 0 else None
                
                # Get next appointment
                upcoming = patient_appointments[
                    (patient_appointments['date'] >= datetime.now().strftime('%Y-%m-%d')) &
                    (patient_appointments['status'].isin(['confirmed', 'pending']))
                ].sort_values('date')
                next_appointment = upcoming.iloc[0] if len(upcoming) > 0 else None
                
                # Calculate age (mock)
                age = np.random.randint(18, 80)
                
                patients_list.append({
                    "id": patient_id,
                    "name": f"{patient['first_name']} {patient['last_name']}",
                    "email": patient['email_id'],
                    "phone": patient['mobile'],
                    "age": age,
                    "gender": np.random.choice(['Male', 'Female']),
                    "bloodGroup": np.random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
                    "totalVisits": len(patient_appointments),
                    "lastVisit": last_appointment['date'] if last_appointment is not None else None,
                    "nextAppointment": {
                        "date": next_appointment['date'],
                        "time": next_appointment['time']
                    } if next_appointment is not None else None,
                    "medicalHistory": [
                        {
                            "condition": np.random.choice(['Hypertension', 'Diabetes', 'Asthma', 'Allergies']),
                            "since": f"{np.random.randint(1, 10)} years"
                        }
                    ],
                    "status": "active" if len(upcoming) > 0 else "inactive"
                })
        
        # Sort by name
        patients_list = sorted(patients_list, key=lambda x: x['name'])
        
        return {
            "success": True,
            "data": {
                "patients": patients_list,
                "summary": {
                    "total": len(patients_list),
                    "active": len([p for p in patients_list if p['status'] == 'active']),
                    "newThisMonth": np.random.randint(5, 15)
                }
            }
        }
    
    # 5. REVIEWS (/doctor/reviews)
    def get_doctor_reviews(self, doctor_email: str, 
                          rating_filter: Optional[int] = None) -> Dict[str, Any]:
        """Get all reviews for this doctor"""
        doctor = self.get_doctor_info(doctor_email)
        if not doctor:
            return {"success": False, "error": "Doctor not found"}
        
        doctor_id = doctor['doctor_id']
        
        # Get appointments for this doctor
        doctor_appointments = self.appointments_df[self.appointments_df['doctor_id'] == doctor_id]
        appointment_ids = doctor_appointments['appointment_id'].tolist()
        
        # Get feedback for these appointments
        doctor_feedback = self.feedback_df[self.feedback_df['appointment_id'].isin(appointment_ids)].copy()
        
        if rating_filter:
            doctor_feedback = doctor_feedback[doctor_feedback['rating'].astype(int) == rating_filter]
        
        # Build reviews list
        reviews_list = []
        for _, feedback in doctor_feedback.iterrows():
            # Get appointment details
            appointment = doctor_appointments[doctor_appointments['appointment_id'] == feedback['appointment_id']]
            
            if len(appointment) > 0:
                apt = appointment.iloc[0]
                patient = self.users_df.loc[apt['patient_id']] if apt['patient_id'] in self.users_df.index else None
                
                # Check if admin responded
                admin_response = self.admin_responses_df[
                    self.admin_responses_df['feedback_id'] == feedback['feedback_id']
                ]
                
                reviews_list.append({
                    "id": feedback['feedback_id'],
                    "patientName": f"{patient['first_name']} {patient['last_name']}" if patient is not None else "Anonymous",
                    "rating": int(feedback['rating']),
                    "comment": feedback['comments'] if pd.notna(feedback['comments']) else "",
                    "date": apt['date'],
                    "appointmentType": apt['type'],
                    "hasResponse": len(admin_response) > 0,
                    "response": admin_response.iloc[0]['response_text'] if len(admin_response) > 0 else None,
                    "helpful": np.random.randint(0, 20),  # Mock helpful votes
                    "verified": True  # Assuming all reviews are verified
                })
        
        # Sort by date (newest first)
        reviews_list = sorted(reviews_list, key=lambda x: x['date'], reverse=True)
        
        # Calculate rating distribution
        rating_dist = doctor_feedback['rating'].value_counts().to_dict()
        rating_distribution = {
            5: rating_dist.get('5', 0) + rating_dist.get(5, 0),
            4: rating_dist.get('4', 0) + rating_dist.get(4, 0),
            3: rating_dist.get('3', 0) + rating_dist.get(3, 0),
            2: rating_dist.get('2', 0) + rating_dist.get(2, 0),
            1: rating_dist.get('1', 0) + rating_dist.get(1, 0)
        }
        
        # Calculate stats
        avg_rating = doctor_feedback['rating'].astype(float).mean() if len(doctor_feedback) > 0 else 0
        total_reviews = len(doctor_feedback)
        
        return {
            "success": True,
            "data": {
                "reviews": reviews_list,
                "stats": {
                    "averageRating": round(avg_rating, 1),
                    "totalReviews": total_reviews,
                    "ratingDistribution": rating_distribution,
                    "responseRate": round(len(reviews_list) / max(len(reviews_list), 1) * 100, 1) if reviews_list else 0
                },
                "recentTrends": {
                    "lastMonth": round(np.random.uniform(4.5, 5.0), 1),
                    "thisMonth": round(avg_rating, 1),
                    "change": round(np.random.uniform(-0.2, 0.3), 1)
                }
            }
        }
    
    # 6. PROFILE (/doctor/profile)
    def get_doctor_profile(self, doctor_email: str) -> Dict[str, Any]:
        """Get doctor's complete profile information"""
        doctor_user = self.users_df[self.users_df['email_id'] == doctor_email]
        
        if len(doctor_user) == 0:
            return {"success": False, "error": "Doctor not found"}
        
        user_info = doctor_user.iloc[0]
        doctor_info = self.doctors_df[self.doctors_df['user_id'] == doctor_user.index[0]]
        
        if len(doctor_info) == 0:
            return {"success": False, "error": "Doctor profile not found"}
        
        doctor = doctor_info.iloc[0]
        doctor_id = doctor['doctor_id']
        
        # Get availability schedule
        availability = self.availability_df[self.availability_df['doctor_id'] == doctor_id]
        
        # Build weekly schedule
        weekly_schedule = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            # Find availability for this day (mock - would need day of week in real data)
            day_avail = availability.sample(1).iloc[0] if len(availability) > 0 and np.random.random() > 0.3 else None
            
            if day_avail is not None:
                weekly_schedule[day] = {
                    "isAvailable": True,
                    "startTime": day_avail['start_time'],
                    "endTime": day_avail['end_time']
                }
            else:
                weekly_schedule[day] = {
                    "isAvailable": False,
                    "startTime": None,
                    "endTime": None
                }
        
        # Get statistics
        total_appointments = len(self.appointments_df[self.appointments_df['doctor_id'] == doctor_id])
        completed_appointments = len(self.appointments_df[
            (self.appointments_df['doctor_id'] == doctor_id) & 
            (self.appointments_df['status'] == 'completed')
        ])
        
        # Get reviews stats
        doctor_appointments = self.appointments_df[self.appointments_df['doctor_id'] == doctor_id]
        doctor_feedback = self.feedback_df[self.feedback_df['appointment_id'].isin(doctor_appointments['appointment_id'])]
        avg_rating = doctor_feedback['rating'].astype(float).mean() if len(doctor_feedback) > 0 else 0
        
        return {
            "success": True,
            "data": {
                "personalInfo": {
                    "firstName": user_info['first_name'],
                    "lastName": user_info['last_name'],
                    "email": user_info['email_id'],
                    "phone": user_info['mobile'],
                    "dateOfBirth": "1980-05-15",  # Mock
                    "gender": np.random.choice(['Male', 'Female']),
                    "address": {
                        "street": "123 Medical Center Dr",
                        "city": "Healthcare City",
                        "state": "HC",
                        "zipCode": "12345",
                        "country": "USA"
                    }
                },
                "professionalInfo": {
                    "doctorId": doctor_id,
                    "specialty": doctor['specialty'],
                    "qualifications": doctor['qualifications'].split(',') if pd.notna(doctor['qualifications']) else [],
                    "experience": f"{doctor['experience']} years" if pd.notna(doctor['experience']) else "5 years",
                    "licenseNumber": f"MED{np.random.randint(10000, 99999)}",
                    "languages": ["English", "Spanish"],  # Mock
                    "bio": f"Experienced {doctor['specialty']} specialist with expertise in advanced treatments and patient care.",
                    "awards": [
                        "Best Doctor Award 2023",
                        "Excellence in Patient Care 2022"
                    ]
                },
                "workInfo": {
                    "department": doctor['specialty'],
                    "joinDate": "2020-01-15",  # Mock
                    "employeeId": f"EMP{doctor_id}",
                    "officeLocation": "Building A, Floor 3, Room 301",
                    "consultationFee": 150  # Mock
                },
                "schedule": weekly_schedule,
                "statistics": {
                    "totalAppointments": total_appointments,
                    "completedAppointments": completed_appointments,
                    "cancellationRate": round(np.random.uniform(5, 15), 1),
                    "averageRating": round(avg_rating, 1),
                    "totalReviews": len(doctor_feedback),
                    "patientsServed": len(self.appointments_df[self.appointments_df['doctor_id'] == doctor_id]['patient_id'].unique())
                },
                "settings": {
                    "emailNotifications": True,
                    "smsNotifications": True,
                    "appointmentReminders": True,
                    "newsletterSubscription": False
                }
            }
        }
    
    # Additional utility functions
    
    def update_doctor_profile(self, doctor_email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update doctor profile information"""
        # This would update the dataframes and save to CSV
        # For now, return success
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
    
    def update_doctor_schedule(self, doctor_email: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Update doctor's availability schedule"""
        # This would update the availability dataframe and save to CSV
        return {
            "success": True,
            "message": "Schedule updated successfully"
        }
    
    def respond_to_review(self, doctor_email: str, review_id: str, response: str) -> Dict[str, Any]:
        """Allow doctor to respond to a review"""
        # This would add to a doctor_responses table
        return {
            "success": True,
            "message": "Response posted successfully"
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    processor = DoctorDashboardProcessor("./csv_files")
    
    # Test all endpoints
    doctor_email = "doctor@medicare.com"
    
    print("1. Doctor Dashboard:")
    print(json.dumps(processor.get_doctor_dashboard(doctor_email), indent=2))
    
    print("\n2. Doctor Schedule:")
    print(json.dumps(processor.get_doctor_schedule(doctor_email), indent=2))
    
    print("\n3. Doctor Appointments:")
    print(json.dumps(processor.get_doctor_appointments(doctor_email), indent=2))
    
    print("\n4. Doctor Patients:")
    print(json.dumps(processor.get_doctor_patients(doctor_email), indent=2))
    
    print("\n5. Doctor Reviews:")
    print(json.dumps(processor.get_doctor_reviews(doctor_email), indent=2))
    
    print("\n6. Doctor Profile:")
    print(json.dumps(processor.get_doctor_profile(doctor_email), indent=2))