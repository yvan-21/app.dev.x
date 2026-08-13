# Java Attendance System

Simple CRUD attendance system using Java, JDBC, Maven, and MySQL.

## CRUD Features
- Create: Add attendance
- Read: View all attendance records
- Update: Edit a record by ID
- Delete: Delete a record by ID

## 1. Create the MySQL database
Run `database.sql` in MySQL Workbench, phpMyAdmin, HeidiSQL, or MySQL CLI.

## 2. Configure your MySQL password
Open:

`src/main/java/com/attendance/DatabaseConnection.java`

Change:

```java
private static final String USER = "root";
private static final String PASSWORD = "";
```

If your MySQL password is `1234`:

```java
private static final String PASSWORD = "1234";
```

## 3. Run the program
Requires Java 17 or newer.

With Maven:

```bash
mvn clean compile
mvn exec:java
```

Or open the project as a Maven project in IntelliJ IDEA, NetBeans, or VS Code and run:

`com.attendance.Main`

## Menu
1. Add Attendance
2. View Records
3. Update Attendance
4. Delete Attendance
5. Exit

## Example
Student Name: John Cruz  
Student ID: 2026-001  
Date: 2026-08-13  
Time In: 08:00  
Time Out: 17:00  
Status: Present
