import pandas as pd

# Create DataFrames with appropriate dtypes
users = pd.DataFrame({
    "user_id": pd.Series(dtype="int64"),
    "name": pd.Series(dtype="string"),
    "email": pd.Series(dtype="string"),
    "password_hash": pd.Series(dtype="string"),
    "contact_info": pd.Series(dtype="string")
})

roles = pd.DataFrame({
    "role_id": pd.Series(dtype="int64"),
    "role_name": pd.Series(dtype="string")
})

user_roles = pd.DataFrame({
    "user_id": pd.Series(dtype="int64"),
    "role_id": pd.Series(dtype="int64")
})

doctors = pd.DataFrame({
    "doctor_id": pd.Series(dtype="int64"),
    "user_id": pd.Series(dtype="int64"),
    "specialty": pd.Series(dtype="string"),
    "qualifications": pd.Series(dtype="string"),
    "experience": pd.Series(dtype="int64")
})

availability = pd.DataFrame({
    "availability_id": pd.Series(dtype="int64"),
    "doctor_id": pd.Series(dtype="int64"),
    "date": pd.Series(dtype="datetime64[ns]"),
    "start_time": pd.Series(dtype="datetime64[ns]"),
    "end_time": pd.Series(dtype="datetime64[ns]")
})

appointments = pd.DataFrame({
    "appointment_id": pd.Series(dtype="int64"),
    "patient_id": pd.Series(dtype="int64"),
    "doctor_id": pd.Series(dtype="int64"),
    "scheduled_datetime": pd.Series(dtype="datetime64[ns]"),
    "status": pd.Series(dtype="category")
})

notifications = pd.DataFrame({
    "notification_id": pd.Series(dtype="int64"),
    "appointment_id": pd.Series(dtype="int64"),
    "sent_via": pd.Series(dtype="category"),
    "sent_at": pd.Series(dtype="datetime64[ns]")
})

feedback = pd.DataFrame({
    "feedback_id": pd.Series(dtype="int64"),
    "appointment_id": pd.Series(dtype="int64"),
    "rating": pd.Series(dtype="int64"),
    "comments": pd.Series(dtype="string")
})

admin_responses = pd.DataFrame({
    "response_id": pd.Series(dtype="int64"),
    "feedback_id": pd.Series(dtype="int64"),
    "admin_id": pd.Series(dtype="int64"),
    "response_text": pd.Series(dtype="string"),
    "responded_at": pd.Series(dtype="datetime64[ns]")
})

# Print dtypes to confirm
tables = {
    "Users": users,
    "Roles": roles,
    "UserRoles": user_roles,
    "Doctors": doctors,
    "Availability": availability,
    "Appointments": appointments,
    "Notifications": notifications,
    "Feedback": feedback,
    "AdminResponses": admin_responses
}

for name, df in tables.items():
    print(f"\n=== {name} DataFrame dtypes ===")
    print(df.dtypes)
