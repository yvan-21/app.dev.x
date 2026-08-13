package com.attendance;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class AttendanceDAO {

    public boolean create(Attendance a) {
        String sql = "INSERT INTO attendance " +
                "(student_name, student_id, attendance_date, time_in, time_out, status) " +
                "VALUES (?, ?, ?, ?, ?, ?)";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            setParams(ps, a);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            System.out.println("Create failed: " + e.getMessage());
            return false;
        }
    }

    public List<Attendance> readAll() {
        List<Attendance> list = new ArrayList<>();
        String sql = "SELECT * FROM attendance ORDER BY attendance_date DESC, id DESC";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {

            while (rs.next()) {
                Time in = rs.getTime("time_in");
                Time out = rs.getTime("time_out");

                list.add(new Attendance(
                        rs.getInt("id"),
                        rs.getString("student_name"),
                        rs.getString("student_id"),
                        rs.getDate("attendance_date").toLocalDate(),
                        in == null ? null : in.toLocalTime(),
                        out == null ? null : out.toLocalTime(),
                        rs.getString("status")
                ));
            }
        } catch (SQLException e) {
            System.out.println("Read failed: " + e.getMessage());
        }
        return list;
    }

    public Attendance findById(int id) {
        String sql = "SELECT * FROM attendance WHERE id = ?";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {

            ps.setInt(1, id);

            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    Time in = rs.getTime("time_in");
                    Time out = rs.getTime("time_out");

                    return new Attendance(
                            rs.getInt("id"),
                            rs.getString("student_name"),
                            rs.getString("student_id"),
                            rs.getDate("attendance_date").toLocalDate(),
                            in == null ? null : in.toLocalTime(),
                            out == null ? null : out.toLocalTime(),
                            rs.getString("status")
                    );
                }
            }
        } catch (SQLException e) {
            System.out.println("Search failed: " + e.getMessage());
        }
        return null;
    }

    public boolean update(int id, Attendance a) {
        String sql = "UPDATE attendance SET student_name=?, student_id=?, " +
                "attendance_date=?, time_in=?, time_out=?, status=? WHERE id=?";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            setParams(ps, a);
            ps.setInt(7, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            System.out.println("Update failed: " + e.getMessage());
            return false;
        }
    }

    public boolean delete(int id) {
        String sql = "DELETE FROM attendance WHERE id=?";

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            System.out.println("Delete failed: " + e.getMessage());
            return false;
        }
    }

    private void setParams(PreparedStatement ps, Attendance a) throws SQLException {
        ps.setString(1, a.getStudentName());
        ps.setString(2, a.getStudentId());
        ps.setDate(3, Date.valueOf(a.getDate()));

        if (a.getTimeIn() == null) ps.setNull(4, Types.TIME);
        else ps.setTime(4, Time.valueOf(a.getTimeIn()));

        if (a.getTimeOut() == null) ps.setNull(5, Types.TIME);
        else ps.setTime(5, Time.valueOf(a.getTimeOut()));

        ps.setString(6, a.getStatus());
    }
}
