package com.attendance;

import java.time.LocalDate;
import java.time.LocalTime;

public class Attendance {
    private final int id;
    private final String studentName;
    private final String studentId;
    private final LocalDate date;
    private final LocalTime timeIn;
    private final LocalTime timeOut;
    private final String status;

    public Attendance(String studentName, String studentId, LocalDate date,
                      LocalTime timeIn, LocalTime timeOut, String status) {
        this(0, studentName, studentId, date, timeIn, timeOut, status);
    }

    public Attendance(int id, String studentName, String studentId, LocalDate date,
                      LocalTime timeIn, LocalTime timeOut, String status) {
        this.id = id;
        this.studentName = studentName;
        this.studentId = studentId;
        this.date = date;
        this.timeIn = timeIn;
        this.timeOut = timeOut;
        this.status = status;
    }

    public int getId() { return id; }
    public String getStudentName() { return studentName; }
    public String getStudentId() { return studentId; }
    public LocalDate getDate() { return date; }
    public LocalTime getTimeIn() { return timeIn; }
    public LocalTime getTimeOut() { return timeOut; }
    public String getStatus() { return status; }
}
