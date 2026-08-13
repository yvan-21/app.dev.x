CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

CREATE TABLE IF NOT EXISTS settings (
    id INT PRIMARY KEY DEFAULT 1,
    morning_login_start TIME DEFAULT '07:00:00',
    morning_login_end TIME DEFAULT '07:50:00',
    morning_logout_start TIME DEFAULT '11:00:00',
    morning_logout_end TIME DEFAULT '12:00:00',
    afternoon_login_start TIME DEFAULT '13:00:00',
    afternoon_login_end TIME DEFAULT '13:50:00',
    afternoon_logout_start TIME DEFAULT '17:00:00',
    afternoon_logout_end TIME DEFAULT '18:00:00'
);

INSERT IGNORE INTO settings (id) VALUES (1);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    attendance_date DATE NOT NULL,
    morning_time_in TIME NULL,
    morning_time_out TIME NULL,
    morning_status VARCHAR(20) DEFAULT 'Absent',
    afternoon_time_in TIME NULL,
    afternoon_time_out TIME NULL,
    afternoon_status VARCHAR(20) DEFAULT 'Absent'
);

