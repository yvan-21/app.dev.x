import json
import sqlite3

from app import app


def reset_db():
    conn = sqlite3.connect('attendance.db')
    conn.execute('DELETE FROM attendance')
    conn.execute(
        "INSERT INTO attendance (student_name, student_id, attendance_date, time_in, time_out, status) VALUES (?, ?, ?, ?, ?, ?)",
        ('Test User', 'T-001', '2026-08-13', '08:00', '17:00', 'Present'),
    )
    conn.commit()
    conn.close()


def test_homepage_has_crud_controls():
    reset_db()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    body = response.get_data(as_text=True).lower()
    assert 'create' in body or 'student name' in body
    assert 'update' in body
    assert 'delete' in body


def test_crud_flow():
    reset_db()
    client = app.test_client()

    create_response = client.post(
        '/api/attendances',
        json={
            'studentName': 'Alice Smith',
            'studentId': 'A-100',
            'date': '2026-08-14',
            'timeIn': '09:00',
            'timeOut': '17:30',
            'status': 'Late',
        },
    )
    assert create_response.status_code == 200
    created = create_response.get_json()
    assert created['ok'] is True

    records_response = client.get('/api/attendances')
    assert records_response.status_code == 200
    rows = records_response.get_json()
    assert any(r['studentId'] == 'A-100' for r in rows)

    item_id = next(r['id'] for r in rows if r['studentId'] == 'A-100')
    update_response = client.put(
        f'/api/attendances/{item_id}',
        json={
            'studentName': 'Alice Updated',
            'studentId': 'A-100',
            'date': '2026-08-14',
            'timeIn': '08:45',
            'timeOut': '17:15',
            'status': 'Present',
        },
    )
    assert update_response.status_code == 200
    updated = update_response.get_json()
    assert updated['ok'] is True

    delete_response = client.delete(f'/api/attendances/{item_id}')
    assert delete_response.status_code == 200
    deleted = delete_response.get_json()
    assert deleted['ok'] is True
