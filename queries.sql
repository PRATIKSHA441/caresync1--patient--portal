-- Doctor appointment summary
SELECT
    d.full_name AS doctor_name,
    COUNT(a.appointment_id) AS total_appointments
FROM doctor AS d
LEFT JOIN appointment AS a
    ON d.doctor_id = a.doctor_id
GROUP BY d.doctor_id, d.full_name
ORDER BY total_appointments DESC;


-- Doctor appointment summary view
CREATE OR REPLACE VIEW vw_doctor_appointment_summary AS
SELECT
    d.full_name AS doctor_name,
    COUNT(a.appointment_id) AS total_appointments
FROM doctor AS d
LEFT JOIN appointment AS a
    ON d.doctor_id = a.doctor_id
GROUP BY d.doctor_id, d.full_name;


-- Verify view
SELECT *
FROM vw_doctor_appointment_summary
LIMIT 10;