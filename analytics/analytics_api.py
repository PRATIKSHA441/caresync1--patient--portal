# analytics_api.py
# CareSync Analytics Dashboard Backend
#
# Three endpoints powering three hospital reports:
#   /revenue-trend     -- Monthly revenue and rejection rate (12 months)
#   /appointment-heatmap -- Appointment count by day-of-week and month
#   /blood-groups      -- Patient blood group distribution + risk flag
#
# Run with:
#   uvicorn analytics_api:app --reload --port 8001
# (port 8001 avoids conflict if Day 4 dashboard is also running)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI(title='CareSync Analytics API')

# Allow the HTML file to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET'],
    allow_headers=['*'],
)

# ── Database connection helper ───────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Pro64',      # change to your MySQL password
        database='caresync'
    )

# ── ENDPOINT 1: Monthly Revenue Trend ────────────────────────────────────
# Returns 12 months of revenue data with rejection rate.
# Uses a CTE to calculate monthly stats then formats for the chart.
@app.get('/revenue-trend')
def revenue_trend():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('''
        WITH monthly_stats AS (
            SELECT
                DATE_FORMAT(b.bill_date, '%Y-%m')   AS month,
                COUNT(b.bill_id)                    AS total_bills,
                ROUND(SUM(b.amount_paid), 2)        AS collected,
                SUM(b.status = 'Rejected')          AS rejected_count
            FROM billing b
            WHERE b.bill_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY month
        )
        SELECT
            month,
            total_bills,
            collected,
            rejected_count,
            ROUND(rejected_count * 100.0 / NULLIF(total_bills, 0), 1)
                AS rejection_rate_pct
        FROM monthly_stats
        ORDER BY month ASC
    ''')
    rows = cursor.fetchall()

    # Convert Decimal to float so JSON serialisation works
    for r in rows:
        r['collected'] = float(r['collected'])

    cursor.close()
    db.close()
    return {'data': rows}

# ── ENDPOINT 2: Appointment Heatmap ──────────────────────────────────────
# Returns appointment counts grouped by month and day of week.
# DAYOFWEEK: 1=Sunday, 2=Monday ... 7=Saturday
@app.get('/appointment-heatmap')
def appointment_heatmap():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('''
        SELECT
            DATE_FORMAT(appointment_date, '%Y-%m')  AS month,
            DAYOFWEEK(appointment_date)              AS day_num,
            DAYNAME(appointment_date)                AS day_name,
            COUNT(*)                                 AS total
        FROM appointment
        WHERE appointment_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
          AND status = 'Completed'
        GROUP BY month, day_num, day_name
        ORDER BY month ASC, day_num ASC
    ''')
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return {'data': rows}

# ── ENDPOINT 3: Blood Group Distribution ─────────────────────────────────
# Returns patient count per blood group.
# Also returns a risk flag for rare blood groups with upcoming appointments.
@app.get('/blood-groups')
def blood_groups():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    # Count of active patients per blood group
    cursor.execute('''
        SELECT
            COALESCE(blood_group, 'Unknown') AS blood_group,
            COUNT(*)                          AS patient_count
        FROM patient
        WHERE is_deleted = 0
        GROUP BY blood_group
        ORDER BY patient_count DESC
    ''')
    distribution = cursor.fetchall()

    # Rare blood groups with upcoming appointments (clinical risk flag)
    # Rare groups: AB-, B-, A-, O-
    cursor.execute('''
        SELECT
            p.blood_group,
            p.full_name          AS patient_name,
            a.appointment_date,
            d.full_name          AS doctor_name,
            d.specialisation
        FROM patient p
        JOIN appointment a ON a.patient_id = p.patient_id
        JOIN doctor d      ON d.doctor_id  = a.doctor_id
        WHERE p.blood_group IN ('AB-', 'B-', 'A-', 'O-')
          AND p.is_deleted = 0
          AND a.status = 'Scheduled'
          AND a.appointment_date BETWEEN CURDATE()
              AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY a.appointment_date ASC
        LIMIT 20
    ''')
    risk_patients = cursor.fetchall()

    # Convert date objects to string so JSON serialisation works
    for rp in risk_patients:
        rp['appointment_date'] = str(rp['appointment_date'])

    cursor.close()
    db.close()
    return {
        'distribution': distribution,
        'risk_patients': risk_patients,
    }

