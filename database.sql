CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    attendance_date DATE NOT NULL,
    time_in TIME NULL,
    time_out TIME NULL,
    login_start TIME NULL,
    login_end TIME NULL,
    logout_start TIME NULL,
    logout_end TIME NULL,
    status VARCHAR(20) NOT NULL
);

INSERT INTO attendance
(student_name, student_id, attendance_date, time_in, time_out, login_start, login_end, logout_start, logout_end, status)
VALUES
('John Cruz', '2026-001', '2026-08-13', '08:00:00', '17:00:00', '07:00:00', '07:50:00', '11:00:00', '12:00:00', 'Present'),
('Maria Santos', '2026-002', '2026-08-13', '08:15:00', '17:00:00', '07:00:00', '07:50:00', '11:00:00', '12:00:00', 'Late');

