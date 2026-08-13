import app as a


def setup_function():
    if a.USE_MYSQL:
        conn = a.get_conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM attendance')
        cur.close()
        conn.close()
    else:
        conn = a.get_conn_sqlite()
        conn.execute('DELETE FROM attendance')
        conn.commit()
        conn.close()


def test_login_and_logout_windows_mark_present():
    client = a.app.test_client()
    resp = client.post(
        '/api/attendances',
        json={
            'studentName': 'Ana',
            'studentId': 'S-100',
            'date': '2026-08-13',
            'timeIn': '07:30',
            'timeOut': '11:30',
            'loginStart': '07:00',
            'loginEnd': '07:50',
            'logoutStart': '11:00',
            'logoutEnd': '12:00',
        },
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['ok'] is True
    row = a.query_all('SELECT status FROM attendance WHERE student_id=%s', ('S-100',))[0]
    assert row['status'] == 'Present'


def test_late_login_marks_late_and_missing_logout_marks_absent():
    client = a.app.test_client()

    late_resp = client.post(
        '/api/attendances',
        json={
            'studentName': 'Ben',
            'studentId': 'S-101',
            'date': '2026-08-13',
            'timeIn': '08:10',
            'timeOut': '11:30',
            'loginStart': '07:00',
            'loginEnd': '07:50',
            'logoutStart': '11:00',
            'logoutEnd': '12:00',
        },
    )
    assert late_resp.status_code == 200
    late_row = a.query_all('SELECT status FROM attendance WHERE student_id=%s', ('S-101',))[0]
    assert late_row['status'] == 'Late'

    absent_resp = client.post(
        '/api/attendances',
        json={
            'studentName': 'Cara',
            'studentId': 'S-102',
            'date': '2026-08-13',
            'timeIn': '07:25',
            'timeOut': None,
            'loginStart': '07:00',
            'loginEnd': '07:50',
            'logoutStart': '11:00',
            'logoutEnd': '12:00',
        },
    )
    assert absent_resp.status_code == 200
    absent_row = a.query_all('SELECT status FROM attendance WHERE student_id=%s', ('S-102',))[0]
    assert absent_row['status'] == 'Absent'
