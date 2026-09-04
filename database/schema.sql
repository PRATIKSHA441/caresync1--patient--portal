-- =============================================================
-- CareSync Patient Portal
-- Database Schema
-- MySQL 8.0
-- =============================================================

CREATE DATABASE IF NOT EXISTS caresync
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE caresync;

-- -------------------------------------------------------------
-- Table: doctor
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS doctor (
    doctor_id         INT            NOT NULL AUTO_INCREMENT,
    full_name         VARCHAR(150)   NOT NULL,
    specialisation    VARCHAR(100)   NOT NULL,
    phone             VARCHAR(15),
    email             VARCHAR(150),
    licence_number    VARCHAR(50)    NOT NULL,
    is_active         TINYINT(1)     NOT NULL DEFAULT 1,
    created_at        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (doctor_id),
    UNIQUE KEY uq_doctor_email (email),
    UNIQUE KEY uq_doctor_licence (licence_number)
);

-- -------------------------------------------------------------
-- Table: patient
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patient (
    patient_id              INT            NOT NULL AUTO_INCREMENT,
    full_name               VARCHAR(150)   NOT NULL,
    date_of_birth           DATE           NOT NULL,
    gender                  ENUM('Male','Female','Other') NOT NULL,
    phone                   VARCHAR(15),
    email                   VARCHAR(150),
    address                 TEXT,
    blood_group             VARCHAR(5),
    emergency_contact_name  VARCHAR(150),
    emergency_contact_phone VARCHAR(15),
    is_deleted              TINYINT(1)     NOT NULL DEFAULT 0,
    created_at              DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                           ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (patient_id),
    INDEX idx_patient_name (full_name)
);

-- -------------------------------------------------------------
-- Table: appointment
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS appointment (
    appointment_id    INT          NOT NULL AUTO_INCREMENT,
    patient_id        INT          NOT NULL,
    doctor_id         INT          NOT NULL,
    appointment_date  DATE         NOT NULL,
    appointment_time  TIME         NOT NULL,
    reason            TEXT,
    diagnosis         TEXT,
    notes             TEXT,
    status            ENUM('Scheduled','Completed','Cancelled')
                      NOT NULL DEFAULT 'Scheduled',
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (appointment_id),

    CONSTRAINT fk_appt_patient
        FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_appt_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    INDEX idx_appt_patient (patient_id),
    INDEX idx_appt_doctor (doctor_id),
    INDEX idx_appt_date (appointment_date)
);

-- -------------------------------------------------------------
-- Table: billing
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS billing (
    bill_id            INT            NOT NULL AUTO_INCREMENT,
    appointment_id     INT            NOT NULL,
    patient_id         INT            NOT NULL,
    total_amount       DECIMAL(10,2)  NOT NULL,
    amount_paid        DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    discount           DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    status             ENUM('Pending','Paid','Partially Paid','Rejected')
                       NOT NULL DEFAULT 'Pending',
    rejection_reason   TEXT,
    bill_date          DATE           NOT NULL,
    due_date           DATE,
    created_at         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (bill_id),
    UNIQUE KEY uq_bill_appointment (appointment_id),

    CONSTRAINT fk_bill_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (appointment_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_bill_patient
        FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    INDEX idx_bill_patient (patient_id),
    INDEX idx_bill_status (status),
    INDEX idx_bill_date (bill_date)
);

-- -------------------------------------------------------------
-- Table: activity_log
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_log (
    log_id        BIGINT       NOT NULL AUTO_INCREMENT,
    user_type     ENUM('Doctor','Patient','Billing') NOT NULL,
    user_id       INT          NOT NULL,
    action        VARCHAR(100) NOT NULL,
    target_table  VARCHAR(50),
    target_id     INT,
    old_value     TEXT,
    new_value     TEXT,
    ip_address    VARCHAR(45),
    logged_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),
    INDEX idx_log_user (user_type, user_id),
    INDEX idx_log_action (action),
    INDEX idx_log_time (logged_at)
);
