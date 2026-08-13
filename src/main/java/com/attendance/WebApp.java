package com.attendance;

import static spark.Spark.*;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class WebApp {
    private static final AttendanceDAO dao = new AttendanceDAO();
    private static final Gson gson = new Gson();

    public static void main(String[] args) {
        port(8080);
        staticFiles.location("/public");

        // API
        get("/api/attendances", (req, res) -> {
            res.type("application/json");
            List<Attendance> list = dao.readAll();
            return gson.toJson(list.stream().map(WebApp::toMap).collect(Collectors.toList()));
        });

        get("/api/attendances/:id", (req, res) -> {
            res.type("application/json");
            Attendance a = dao.findById(Integer.parseInt(req.params("id")));
            if (a == null) { res.status(404); return "{}"; }
            return gson.toJson(toMap(a));
        });

        post("/api/attendances", (req, res) -> {
            res.type("application/json");
            JsonObject json = gson.fromJson(req.body(), JsonObject.class);
            Attendance a = fromJson(json);
            boolean ok = dao.create(a);
            return gson.toJson(Map.of("ok", ok));
        });

        put("/api/attendances/:id", (req, res) -> {
            res.type("application/json");
            int id = Integer.parseInt(req.params("id"));
            JsonObject json = gson.fromJson(req.body(), JsonObject.class);
            Attendance a = fromJson(json);
            boolean ok = dao.update(id, a);
            return gson.toJson(Map.of("ok", ok));
        });

        delete("/api/attendances/:id", (req, res) -> {
            res.type("application/json");
            int id = Integer.parseInt(req.params("id"));
            boolean ok = dao.delete(id);
            return gson.toJson(Map.of("ok", ok));
        });
    }

    private static Attendance fromJson(JsonObject json) {
        String name = json.has("studentName") ? json.get("studentName").getAsString() : "";
        String studentId = json.has("studentId") ? json.get("studentId").getAsString() : "";
        String dateText = json.has("date") ? json.get("date").getAsString() : null;
        String inText = json.has("timeIn") ? json.get("timeIn").getAsString() : "";
        String outText = json.has("timeOut") ? json.get("timeOut").getAsString() : "";
        String status = json.has("status") ? json.get("status").getAsString() : "Present";

        LocalDate date = dateText == null ? LocalDate.now() : LocalDate.parse(dateText);
        LocalTime timeIn = inText == null || inText.isBlank() ? null : LocalTime.parse(inText);
        LocalTime timeOut = outText == null || outText.isBlank() ? null : LocalTime.parse(outText);

        return new Attendance(name, studentId, date, timeIn, timeOut, status);
    }

    private static Map<String, Object> toMap(Attendance a) {
        return Map.of(
                "id", a.getId(),
                "studentName", a.getStudentName(),
                "studentId", a.getStudentId(),
                "date", a.getDate().toString(),
                "timeIn", a.getTimeIn() == null ? "" : a.getTimeIn().toString(),
                "timeOut", a.getTimeOut() == null ? "" : a.getTimeOut().toString(),
                "status", a.getStatus()
        );
    }
}
