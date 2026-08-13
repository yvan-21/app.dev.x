package com.attendance;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.Scanner;

public class Main {
    private static final Scanner scanner = new Scanner(System.in);
    private static final AttendanceDAO dao = new AttendanceDAO();

    public static void main(String[] args) {
        System.out.println("=================================");
        System.out.println("       ATTENDANCE SYSTEM");
        System.out.println("=================================");

        while (true) {
            System.out.println("\n1. Add Attendance");
            System.out.println("2. View Records");
            System.out.println("3. Update Attendance");
            System.out.println("4. Delete Attendance");
            System.out.println("5. Exit");
            System.out.print("Choose an option: ");

            switch (scanner.nextLine().trim()) {
                case "1" -> add();
                case "2" -> view();
                case "3" -> update();
                case "4" -> delete();
                case "5" -> {
                    System.out.println("Program closed.");
                    return;
                }
                default -> System.out.println("Invalid choice. Enter 1-5.");
            }
        }
    }

    private static void add() {
        System.out.println("\n--- ADD ATTENDANCE ---");
        try {
            Attendance a = readInput();
            System.out.println(dao.create(a)
                    ? "Attendance added successfully."
                    : "Attendance was not added.");
        } catch (IllegalArgumentException e) {
            System.out.println("Invalid input: " + e.getMessage());
        }
    }

    private static void view() {
        System.out.println("\n--- ATTENDANCE RECORDS ---");
        List<Attendance> records = dao.readAll();

        if (records.isEmpty()) {
            System.out.println("No records found.");
            return;
        }

        System.out.printf("%-4s %-20s %-12s %-12s %-9s %-9s %-10s%n",
                "ID", "Student", "Student ID", "Date", "Time In", "Time Out", "Status");
        System.out.println("-------------------------------------------------------------------------------");

        for (Attendance a : records) {
            System.out.printf("%-4d %-20s %-12s %-12s %-9s %-9s %-10s%n",
                    a.getId(),
                    shorten(a.getStudentName(), 20),
                    shorten(a.getStudentId(), 12),
                    a.getDate(),
                    a.getTimeIn() == null ? "-" : a.getTimeIn(),
                    a.getTimeOut() == null ? "-" : a.getTimeOut(),
                    a.getStatus());
        }
    }

    private static void update() {
        System.out.println("\n--- UPDATE ATTENDANCE ---");
        int id = readId("Enter ID to update: ");

        Attendance old = dao.findById(id);
        if (old == null) {
            System.out.println("Record not found.");
            return;
        }

        System.out.println("Updating: " + old.getStudentName() + " - " + old.getDate());

        try {
            Attendance replacement = readInput();
            System.out.println(dao.update(id, replacement)
                    ? "Attendance updated successfully."
                    : "Attendance was not updated.");
        } catch (IllegalArgumentException e) {
            System.out.println("Invalid input: " + e.getMessage());
        }
    }

    private static void delete() {
        System.out.println("\n--- DELETE ATTENDANCE ---");
        int id = readId("Enter ID to delete: ");

        Attendance record = dao.findById(id);
        if (record == null) {
            System.out.println("Record not found.");
            return;
        }

        System.out.print("Delete " + record.getStudentName() + "? (Y/N): ");
        if (!scanner.nextLine().trim().equalsIgnoreCase("Y")) {
            System.out.println("Delete cancelled.");
            return;
        }

        System.out.println(dao.delete(id)
                ? "Attendance deleted successfully."
                : "Attendance was not deleted.");
    }

    private static Attendance readInput() {
        System.out.print("Student Name: ");
        String name = scanner.nextLine().trim();

        System.out.print("Student ID: ");
        String studentId = scanner.nextLine().trim();

        System.out.print("Date (YYYY-MM-DD): ");
        String dateText = scanner.nextLine().trim();

        System.out.print("Time In (HH:mm, blank if none): ");
        String inText = scanner.nextLine().trim();

        System.out.print("Time Out (HH:mm, blank if none): ");
        String outText = scanner.nextLine().trim();

        System.out.print("Status (Present/Late/Absent): ");
        String status = scanner.nextLine().trim();

        if (name.isBlank()) throw new IllegalArgumentException("Student name is required.");
        if (studentId.isBlank()) throw new IllegalArgumentException("Student ID is required.");

        LocalDate date;
        try {
            date = LocalDate.parse(dateText);
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("Date must be YYYY-MM-DD.");
        }

        LocalTime timeIn = parseTime(inText);
        LocalTime timeOut = parseTime(outText);

        if (!(status.equalsIgnoreCase("Present")
                || status.equalsIgnoreCase("Late")
                || status.equalsIgnoreCase("Absent"))) {
            throw new IllegalArgumentException("Status must be Present, Late, or Absent.");
        }

        String normalizedStatus =
                Character.toUpperCase(status.toLowerCase().charAt(0))
                + status.toLowerCase().substring(1);

        return new Attendance(name, studentId, date, timeIn, timeOut, normalizedStatus);
    }

    private static LocalTime parseTime(String value) {
        if (value.isBlank()) return null;

        try {
            return LocalTime.parse(value);
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("Time must use HH:mm, for example 08:00.");
        }
    }

    private static int readId(String prompt) {
        while (true) {
            System.out.print(prompt);
            try {
                return Integer.parseInt(scanner.nextLine().trim());
            } catch (NumberFormatException e) {
                System.out.println("Enter a valid numeric ID.");
            }
        }
    }

    private static String shorten(String text, int max) {
        return text.length() <= max ? text : text.substring(0, max - 3) + "...";
    }
}
