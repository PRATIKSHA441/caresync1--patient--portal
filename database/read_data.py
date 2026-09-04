# read_data.py
# CareSync Database Reader
#
# This script demonstrates how to connect Python to MySQL
# and run queries to extract meaningful information.
# This pattern is the foundation of every backend API you will build.

import mysql.connector
from datetime import date

# ─── DATABASE CONNECTION ────────────────────────────────────────────────────
# Best practice: In a real application, you never write the password directly
# in the code. You read it from an environment variable or a config file.
# For today's learning session, we write it directly for simplicity.
connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='caresync'
)
cursor = connection.cursor(dictionary=True)  # dictionary=True gives us column names

print('Connected to CareSync database.')
print('=' * 60)

# ─── QUERY 1: How many doctors in each specialisation? ──────────────────────
print()
print('QUERY 1: Doctor Count by Specialisation')
print('-' * 45)

cursor.execute(
    '''
    SELECT
        specialisation,
        COUNT(*) AS total_doctors
    FROM doctor
    WHERE is_active = 1
    GROUP BY specialisation
    ORDER BY total_doctors DESC
    '''
)

rows = cursor.fetchall()
for row in rows:
    # row is a dictionary because we used dictionary=True above.
    # row['specialisation'] gives us the value in that column.
    print(f"  {row['specialisation']:<25} {row['total_doctors']} doctors")

print()

# ─── QUERY 2: Total revenue by billing status ───────────────────────────────
print('QUERY 2: Revenue Summary by Bill Status')
print('-' * 45)

cursor.execute(
    '''
    SELECT
        status,
        COUNT(*)                        AS total_bills,
        ROUND(SUM(total_amount), 2)     AS total_billed,
        ROUND(SUM(amount_paid), 2)      AS total_collected,
        ROUND(AVG(total_amount), 2)     AS avg_bill_amount
    FROM billing
    GROUP BY status
    ORDER BY total_billed DESC
    '''
)

rows = cursor.fetchall()
for row in rows:
    print(f"  {row['status']:<15}  Bills: {row['total_bills']:>5}  "
          f"Billed: Rs {row['total_billed']:>10}  "
          f"Collected: Rs {row['total_collected']:>10}")

print()

# ─── QUERY 3: Rejection rate calculation ────────────────────────────────────
print('QUERY 3: Bill Rejection Rate')
print('-' * 45)

cursor.execute('SELECT COUNT(*) AS total FROM billing')
total_bills = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) AS rejected FROM billing WHERE status = 'Rejected'")
rejected_bills = cursor.fetchone()['rejected']

rejection_rate = (rejected_bills / total_bills * 100) if total_bills > 0 else 0
print(f'  Total Bills    : {total_bills}')
print(f'  Rejected Bills : {rejected_bills}')
print(f'  Rejection Rate : {rejection_rate:.2f}%')

print()

# ─── QUERY 4: Top 5 busiest doctors ─────────────────────────────────────────
print('QUERY 4: Top 5 Busiest Doctors by Appointments')
print('-' * 50)

cursor.execute(
    '''
    SELECT
        d.full_name,
        d.specialisation,
        COUNT(a.appointment_id) AS total_appointments
    FROM doctor d
    JOIN appointment a ON a.doctor_id = d.doctor_id
    WHERE a.status = 'Completed'
    GROUP BY d.doctor_id, d.full_name, d.specialisation
    ORDER BY total_appointments DESC
    LIMIT 5
    '''
)

rows = cursor.fetchall()
for i, row in enumerate(rows, start=1):
    print(f"  {i}. {row['full_name']:<30} ({row['specialisation']:<20})"
          f"  {row['total_appointments']} completed appointments")

print()

# ─── QUERY 5: Patients with more than 5 visits ──────────────────────────────
print('QUERY 5: Patients With More Than 5 Completed Visits')
print('-' * 52)

cursor.execute(
    '''
    SELECT
        p.full_name,
        p.blood_group,
        COUNT(a.appointment_id) AS visit_count
    FROM patient p
    JOIN appointment a ON a.patient_id = p.patient_id
    WHERE a.status = 'Completed'
      AND p.is_deleted = 0
    GROUP BY p.patient_id, p.full_name, p.blood_group
    HAVING visit_count > 5
    ORDER BY visit_count DESC
    LIMIT 10
    '''
)

rows = cursor.fetchall()
if not rows:
    print('  No patients with more than 5 visits found.')
else:
    for row in rows:
        print(f"  {row['full_name']:<30} Blood: {row['blood_group']:<4}"
              f"  Visits: {row['visit_count']}")

print()

# ─── QUERY 6: Monthly appointment trend (last 6 months) ─────────────────────
print('QUERY 6: Monthly Appointment Count (Last 6 Months)')
print('-' * 52)

cursor.execute(
    '''
    SELECT
        DATE_FORMAT(appointment_date, '%Y-%m') AS month,
        COUNT(*)                               AS total_appointments
    FROM appointment
    WHERE appointment_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
    GROUP BY month
    ORDER BY month ASC
    '''
)

rows = cursor.fetchall()
for row in rows:
    print(f"  {row['month']}   {row['total_appointments']} appointments")

print()
print('=' * 60)
print('All queries completed successfully.')

# ─── CLEANUP ────────────────────────────────────────────────────────────────
cursor.close()
connection.close()
