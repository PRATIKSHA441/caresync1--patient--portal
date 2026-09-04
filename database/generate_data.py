# generate_data.py
# CareSync Sample Data Generator
#
# This script populates the CareSync database with realistic test data.
# Run this ONCE after creating your database and tables.
# Running it twice will cause errors because some unique values will repeat.
#
# Required libraries. Install them before running this script:
#   pip install mysql-connector-python
#   pip install Faker

import mysql.connector       # connects Python to MySQL
import random                # for generating random numbers and choices
from faker import Faker      # generates realistic fake names, addresses, etc.
from datetime import date, timedelta, datetime
import decimal

# Create a Faker instance set to India so names look realistic.
fake = Faker('en_IN')

# ─── DATABASE CONNECTION ────────────────────────────────────────────────────
# Change password if you used something different during MySQL setup.
connection = mysql.connector.connect(
    host='localhost',      # MySQL is running on this same computer
    port=3306,             # Default MySQL port
    user='root',           # The administrator user
    password='',  # Your MySQL root password
    database='caresync'    # The database we created
)
cursor = connection.cursor()

print('Connected to MySQL successfully.')

# ─── CONSTANTS ──────────────────────────────────────────────────────────────
NUM_DOCTORS      = 40
NUM_PATIENTS     = 500
NUM_APPOINTMENTS = 3000
NUM_BILLS        = 2500
BILL_REJECT_LOW  = 0.08   # 8 percent minimum rejection rate
BILL_REJECT_HIGH = 0.12   # 12 percent maximum rejection rate

SPECIALISATIONS = [
    'Cardiology', 'General Medicine', 'Orthopaedics', 'Gynaecology',
    'Paediatrics', 'Neurology', 'Dermatology', 'Ophthalmology',
    'ENT', 'Psychiatry', 'Oncology', 'Urology', 'Endocrinology'
]

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

DIAGNOSES = [
    'Hypertension', 'Type 2 Diabetes', 'Upper Respiratory Infection',
    'Migraine', 'Lumbar Spondylosis', 'Anxiety Disorder', 'Anaemia',
    'Hypothyroidism', 'Gastritis', 'Urinary Tract Infection',
    'Dengue Fever', 'Viral Fever', 'Asthma', 'Arthritis', 'Obesity',
    'Iron Deficiency', 'Vitamin D Deficiency', 'Sinusitis', 'Eczema'
]

REJECTION_REASONS = [
    'Insurance claim limit exceeded for this policy year.',
    'Procedure not covered under current insurance plan.',
    'Pre-authorisation was not obtained before treatment.',
    'Patient not eligible under submitted insurance policy number.',
    'Duplicate claim submitted for the same service date.',
    'Medical documents submitted are incomplete.',
    'Claim submitted after the deadline specified by insurer.'
]

# ─── STEP 1: INSERT DOCTORS ─────────────────────────────────────────────────
print(f'Inserting {NUM_DOCTORS} doctors...')

doctor_ids = []  # We store the IDs so we can use them for appointments later.

for i in range(NUM_DOCTORS):
    name   = 'Dr. ' + fake.name()
    spec   = random.choice(SPECIALISATIONS)
    phone  = '9' + str(random.randint(100000000, 999999999))  # 10-digit Indian number
    email  = f'doctor{i+1}@caresync.in'  # Unique email using the loop counter
    lic    = f'MCI-{2000 + i:04d}'       # Unique licence number

    cursor.execute(
        '''
        INSERT INTO doctor (full_name, specialisation, phone, email, licence_number)
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (name, spec, phone, email, lic)
    )
    doctor_ids.append(cursor.lastrowid)  # lastrowid gives us the auto-generated ID

connection.commit()  # Save all doctor rows to the database
print(f'  Done. Inserted {len(doctor_ids)} doctors.')

# ─── STEP 2: INSERT PATIENTS ────────────────────────────────────────────────
print(f'Inserting {NUM_PATIENTS} patients...')

patient_ids = []

for i in range(NUM_PATIENTS):
    name      = fake.name()
    dob       = fake.date_of_birth(minimum_age=5, maximum_age=85)
    gender    = random.choice(['Male', 'Female'])
    phone     = '9' + str(random.randint(100000000, 999999999))
    email     = f'patient{i+1}@example.com'
    address   = fake.address().replace('\n', ', ')  # Remove line breaks from address
    blood     = random.choice(BLOOD_GROUPS)
    ec_name   = fake.name()   # Emergency contact name
    ec_phone  = '9' + str(random.randint(100000000, 999999999))

    cursor.execute(
        '''
        INSERT INTO patient
            (full_name, date_of_birth, gender, phone, email, address,
             blood_group, emergency_contact_name, emergency_contact_phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (name, dob, gender, phone, email, address, blood, ec_name, ec_phone)
    )
    patient_ids.append(cursor.lastrowid)

connection.commit()
print(f'  Done. Inserted {len(patient_ids)} patients.')

# ─── STEP 3: INSERT APPOINTMENTS ────────────────────────────────────────────
print(f'Inserting {NUM_APPOINTMENTS} appointments...')

appointment_ids = []

# Generate appointments over the past 2 years
start_date = date.today() - timedelta(days=730)
end_date   = date.today()

hour_options   = list(range(9, 17))   # 9 AM to 4 PM
minute_options = [0, 15, 30, 45]      # Every 15 minutes

for _ in range(NUM_APPOINTMENTS):
    p_id    = random.choice(patient_ids)
    d_id    = random.choice(doctor_ids)
    appt_dt = start_date + timedelta(days=random.randint(0, 730))
    appt_tm = f'{random.choice(hour_options):02d}:{random.choice(minute_options):02d}:00'
    reason  = 'Patient complaints of ' + random.choice(DIAGNOSES).lower()
    diag    = random.choice(DIAGNOSES)

    # Weight the status: 80% Completed, 10% Scheduled, 10% Cancelled
    status  = random.choices(
        ['Completed', 'Scheduled', 'Cancelled'],
        weights=[80, 10, 10]
    )[0]

    cursor.execute(
        '''
        INSERT INTO appointment
            (patient_id, doctor_id, appointment_date, appointment_time,
             reason, diagnosis, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (p_id, d_id, appt_dt, appt_tm, reason, diag, status)
    )
    appointment_ids.append(cursor.lastrowid)

connection.commit()
print(f'  Done. Inserted {len(appointment_ids)} appointments.')

# ─── STEP 4: INSERT BILLS ───────────────────────────────────────────────────
print(f'Inserting {NUM_BILLS} bills...')

# Only create bills for Completed appointments.
# We need to find which appointments are Completed.
cursor.execute(
    'SELECT appointment_id, patient_id FROM appointment WHERE status = %s'
    , ('Completed',)
)
completed_appointments = cursor.fetchall()  # Returns list of (appointment_id, patient_id)

if len(completed_appointments) < NUM_BILLS:
    print(f'  Note: Only {len(completed_appointments)} completed appointments available.')
    print(f'  Will create one bill per completed appointment instead of {NUM_BILLS}.')
    bills_to_create = completed_appointments
else:
    # Randomly pick NUM_BILLS from the completed appointments.
    # random.sample ensures no appointment gets two bills (no duplicates).
    bills_to_create = random.sample(completed_appointments, NUM_BILLS)

# Determine the rejection rate for this run.
# A random number between 8% and 12%.
reject_rate = random.uniform(BILL_REJECT_LOW, BILL_REJECT_HIGH)
print(f'  Bill rejection rate for this run: {reject_rate*100:.1f}%')

bills_inserted = 0

for (appt_id, p_id) in bills_to_create:
    # Consultation fee between 300 and 3000 rupees.
    total = round(random.uniform(300, 3000), 2)

    # Decide the bill status.
    rand_val = random.random()  # A number between 0.0 and 1.0

    if rand_val < reject_rate:
        # This bill is Rejected.
        status         = 'Rejected'
        amount_paid    = 0.00
        discount       = 0.00
        reject_reason  = random.choice(REJECTION_REASONS)

    elif rand_val < reject_rate + 0.10:
        # Partially Paid: patient paid between 30% and 70%.
        status         = 'Partially Paid'
        paid_pct       = random.uniform(0.30, 0.70)
        amount_paid    = round(total * paid_pct, 2)
        discount       = 0.00
        reject_reason  = None

    elif rand_val < reject_rate + 0.15:
        # Pending: no payment yet.
        status         = 'Pending'
        amount_paid    = 0.00
        discount       = 0.00
        reject_reason  = None

    else:
        # Paid: full amount paid, sometimes with a small discount.
        status         = 'Paid'
        discount       = round(total * random.uniform(0, 0.05), 2)  # 0-5% discount
        amount_paid    = round(total - discount, 2)
        reject_reason  = None

    # Bill date: a few days after the appointment date.
    cursor.execute(
        'SELECT appointment_date FROM appointment WHERE appointment_id = %s',
        (appt_id,)
    )
    row = cursor.fetchone()
    appt_date  = row[0]
    bill_date  = appt_date + timedelta(days=random.randint(0, 2))
    due_date   = bill_date + timedelta(days=30)

    cursor.execute(
        '''
        INSERT INTO billing
            (appointment_id, patient_id, total_amount, amount_paid, discount,
             status, rejection_reason, bill_date, due_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (appt_id, p_id, total, amount_paid, discount,
         status, reject_reason, bill_date, due_date)
    )
    bills_inserted += 1

connection.commit()
print(f'  Done. Inserted {bills_inserted} bills.')

# ─── STEP 5: VERIFY ROW COUNTS ──────────────────────────────────────────────
print()
print('=== FINAL ROW COUNTS ===')

for table in ['doctor', 'patient', 'appointment', 'billing', 'activity_log']:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table:20s}: {count} rows')

# ─── CLEANUP ────────────────────────────────────────────────────────────────
cursor.close()
connection.close()
print()
print('Done. Database is ready for use.')
