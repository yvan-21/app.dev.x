from flask import Flask, request, jsonify, send_file
import sqlite3
import os
from pathlib import Path
from datetime import date, datetime, time, timedelta


def parse_time(value):
    if value in (None, ''):
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, '%H:%M').time()
        except ValueError:
            return None
    return value


def determine_status(login_time, logout_time, login_start, login_end, logout_start, logout_end):
    login_start = parse_time(login_start)
    login_end = parse_time(login_end)
    logout_start = parse_time(logout_start)
    logout_end = parse_time(logout_end)
    login_time = parse_time(login_time)
    logout_time = parse_time(logout_time)

    if login_time is None and logout_time is None:
        return 'Absent'

    if login_time is None:
        return 'Absent'

    if login_start is not None and login_end is not None:
        if login_start <= login_time <= login_end:
            login_status = 'Present'
        else:
            login_status = 'Late'
    else:
        login_status = 'Present'

    if logout_time is None:
        return 'Absent'

    if logout_start is not None and logout_end is not None:
        if logout_start <= logout_time <= logout_end:
            return login_status
        return 'Absent'

    return login_status

DB_PATH = Path(__file__).parent / 'attendance.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_name TEXT NOT NULL,
  student_id TEXT NOT NULL,
  attendance_date TEXT NOT NULL,
  time_in TEXT,
  time_out TEXT,
  login_start TEXT,
  login_end TEXT,
  logout_start TEXT,
  logout_end TEXT,
  status TEXT NOT NULL
);
'''

app = Flask(__name__)

USE_MYSQL = True  # Force MySQL by default


def get_conn_sqlite():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_conn_mysql():
    import mysql.connector
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'yvan22'),
        database=os.getenv('DB_NAME', 'attendance_db'),
        autocommit=True,
    )


def get_conn():
    return get_conn_mysql() if USE_MYSQL else get_conn_sqlite()


def ensure_sqlite_columns():
    with get_conn_sqlite() as conn:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(attendance)")]
        for col_name in ['login_start', 'login_end', 'logout_start', 'logout_end']:
            if col_name not in columns:
                conn.execute(f'ALTER TABLE attendance ADD COLUMN {col_name} TEXT')
        conn.commit()


def init_db():
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
          id INT AUTO_INCREMENT PRIMARY KEY,
          student_name VARCHAR(255) NOT NULL,
          student_id VARCHAR(255) NOT NULL,
          attendance_date DATE NOT NULL,
          time_in TIME,
          time_out TIME,
          login_start TIME,
          login_end TIME,
          logout_start TIME,
          logout_end TIME,
          status VARCHAR(50) NOT NULL
        )
        ''')
        cur.close()
        conn.close()
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with get_conn() as conn:
            conn.execute(SCHEMA)
        ensure_sqlite_columns()


def normalize_record(row):
    if not row:
        return row
    return {
        'id': row.get('id'),
        'studentName': row.get('student_name'),
        'studentId': row.get('student_id'),
        'date': row.get('attendance_date'),
        'timeIn': row.get('time_in'),
        'timeOut': row.get('time_out'),
        'loginStart': row.get('login_start'),
        'loginEnd': row.get('login_end'),
        'logoutStart': row.get('logout_start'),
        'logoutEnd': row.get('logout_end'),
        'status': row.get('status'),
    }


def query_all(sql, params=()):
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            for k, v in d.items():
                if isinstance(v, (datetime, date, time, timedelta)):
                    d[k] = str(v)
            result.append(d)
        return result
    else:
        with get_conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]


def query_one(sql, params=()):
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        last = cur.lastrowid
        cur.close()
        conn.close()
        return last
    else:
        with get_conn() as conn:
            cur = conn.execute(sql, params)
            return cur.lastrowid


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/api/attendances', methods=['GET'])
def list_attendances():
    rows = query_all('SELECT * FROM attendance ORDER BY attendance_date DESC, id DESC')
    return jsonify([normalize_record(row) for row in rows])


@app.route('/api/attendances/<int:item_id>', methods=['GET'])
def get_attendance(item_id):
    row = query_one('SELECT * FROM attendance WHERE id=%s' if USE_MYSQL else 'SELECT * FROM attendance WHERE id=?', (item_id,))
    return (jsonify(normalize_record(row)) if row else ('', 404))


@app.route('/api/attendances', methods=['POST'])
def create_attendance():
    data = request.get_json() or {}
    name = data.get('studentName', '').strip()
    sid = data.get('studentId', '').strip()
    date_text = data.get('date') or str(date.today())
    time_in = data.get('timeIn') or None
    time_out = data.get('timeOut') or None
    login_start = data.get('loginStart') or None
    login_end = data.get('loginEnd') or None
    logout_start = data.get('logoutStart') or None
    logout_end = data.get('logoutEnd') or None
    status = determine_status(time_in, time_out, login_start, login_end, logout_start, logout_end)

    if not name or not sid:
        return jsonify({'ok': False, 'error': 'studentName and studentId required'}), 400

    if USE_MYSQL:
        last = execute('INSERT INTO attendance (student_name, student_id, attendance_date, time_in, time_out, login_start, login_end, logout_start, logout_end, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                       (name, sid, date_text, time_in, time_out, login_start, login_end, logout_start, logout_end, status))
    else:
        last = execute('INSERT INTO attendance (student_name, student_id, attendance_date, time_in, time_out, login_start, login_end, logout_start, logout_end, status) VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (name, sid, date_text, time_in, time_out, login_start, login_end, logout_start, logout_end, status))
    return jsonify({'ok': True, 'id': last, 'status': status})


@app.route('/api/attendances/<int:item_id>', methods=['PUT'])
def update_attendance(item_id):
    data = request.get_json() or {}
    name = data.get('studentName', '').strip()
    sid = data.get('studentId', '').strip()
    date_text = data.get('date') or str(date.today())
    time_in = data.get('timeIn') or None
    time_out = data.get('timeOut') or None
    login_start = data.get('loginStart') or None
    login_end = data.get('loginEnd') or None
    logout_start = data.get('logoutStart') or None
    logout_end = data.get('logoutEnd') or None
    status = determine_status(time_in, time_out, login_start, login_end, logout_start, logout_end)

    if not name or not sid:
        return jsonify({'ok': False, 'error': 'studentName and studentId required'}), 400

    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('UPDATE attendance SET student_name=%s, student_id=%s, attendance_date=%s, time_in=%s, time_out=%s, login_start=%s, login_end=%s, logout_start=%s, logout_end=%s, status=%s WHERE id=%s',
                    (name, sid, date_text, time_in, time_out, login_start, login_end, logout_start, logout_end, status, item_id))
        ok = cur.rowcount > 0
        cur.close()
        conn.close()
    else:
        conn = get_conn()
        cur = conn.execute('UPDATE attendance SET student_name=?, student_id=?, attendance_date=?, time_in=?, time_out=?, login_start=?, login_end=?, logout_start=?, logout_end=?, status=? WHERE id=?',
                           (name, sid, date_text, time_in, time_out, login_start, login_end, logout_start, logout_end, status, item_id))
        ok = cur.rowcount > 0
        conn.commit()
        conn.close()

    return jsonify({'ok': ok, 'status': status})


@app.route('/api/attendances/<int:item_id>', methods=['DELETE'])
def delete_attendance(item_id):
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM attendance WHERE id=%s', (item_id,))
        ok = cur.rowcount > 0
        cur.close()
        conn.close()
    else:
        with get_conn() as conn:
            cur = conn.execute('DELETE FROM attendance WHERE id=?', (item_id,))
            ok = cur.rowcount > 0
    return jsonify({'ok': ok})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
else:
    init_db()
