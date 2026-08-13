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
            # Try HH:MM:SS format first (from MySQL TIME type)
            return datetime.strptime(value, '%H:%M:%S').time()
        except ValueError:
            try:
                # Fall back to HH:MM format (from form inputs)
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
        else:
            return 'Absent'

    return login_status


def get_settings():
    """Fetch current time window settings from database."""
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM settings WHERE id = 1')
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {
                'morning_login_start': '07:00',
                'morning_login_end': '07:50',
                'morning_logout_start': '11:00',
                'morning_logout_end': '12:00',
                'afternoon_login_start': '13:00',
                'afternoon_login_end': '13:50',
                'afternoon_logout_start': '17:00',
                'afternoon_logout_end': '18:00',
            }
        return {k: str(v) for k, v in row.items()}
    else:
        with get_conn_sqlite() as conn:
            cur = conn.execute('SELECT * FROM settings WHERE id = 1')
            row = cur.fetchone()
            if not row:
                return {
                    'morning_login_start': '07:00',
                    'morning_login_end': '07:50',
                    'morning_logout_start': '11:00',
                    'morning_logout_end': '12:00',
                    'afternoon_login_start': '13:00',
                    'afternoon_login_end': '13:50',
                    'afternoon_logout_start': '17:00',
                    'afternoon_logout_end': '18:00',
                }
            return dict(row)


DB_PATH = Path(__file__).parent / 'attendance.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    morning_login_start TEXT DEFAULT '07:00',
    morning_login_end TEXT DEFAULT '07:50',
    morning_logout_start TEXT DEFAULT '11:00',
    morning_logout_end TEXT DEFAULT '12:00',
    afternoon_login_start TEXT DEFAULT '13:00',
    afternoon_login_end TEXT DEFAULT '13:50',
    afternoon_logout_start TEXT DEFAULT '17:00',
    afternoon_logout_end TEXT DEFAULT '18:00'
);

CREATE TABLE IF NOT EXISTS attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_name TEXT NOT NULL,
  student_id TEXT NOT NULL,
  attendance_date TEXT NOT NULL,
  morning_time_in TEXT,
  morning_time_out TEXT,
  morning_status TEXT DEFAULT 'Absent',
  afternoon_time_in TEXT,
  afternoon_time_out TEXT,
  afternoon_status TEXT DEFAULT 'Absent'
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
        needed = ['morning_time_in', 'morning_time_out', 'morning_status', 'afternoon_time_in', 'afternoon_time_out', 'afternoon_status']
        for col_name in needed:
            if col_name not in columns:
                if 'morning_status' in col_name or 'afternoon_status' in col_name:
                    conn.execute(f"ALTER TABLE attendance ADD COLUMN {col_name} TEXT DEFAULT 'Absent'")
                else:
                    conn.execute(f'ALTER TABLE attendance ADD COLUMN {col_name} TEXT')
        conn.commit()


def init_db():
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('''
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
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
          id INT AUTO_INCREMENT PRIMARY KEY,
          student_name VARCHAR(255) NOT NULL,
          student_id VARCHAR(255) NOT NULL,
          attendance_date DATE NOT NULL,
          morning_time_in TIME,
          morning_time_out TIME,
          morning_status VARCHAR(50) DEFAULT 'Absent',
          afternoon_time_in TIME,
          afternoon_time_out TIME,
          afternoon_status VARCHAR(50) DEFAULT 'Absent'
        )
        ''')
        cur.execute('INSERT IGNORE INTO settings (id) VALUES (1)')
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
        'morningTimeIn': row.get('morning_time_in'),
        'morningTimeOut': row.get('morning_time_out'),
        'morningStatus': row.get('morning_status'),
        'afternoonTimeIn': row.get('afternoon_time_in'),
        'afternoonTimeOut': row.get('afternoon_time_out'),
        'afternoonStatus': row.get('afternoon_status'),
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
    
    morning_time_in = data.get('morningTimeIn') or None
    morning_time_out = data.get('morningTimeOut') or None
    afternoon_time_in = data.get('afternoonTimeIn') or None
    afternoon_time_out = data.get('afternoonTimeOut') or None
    
    if not name or not sid:
        return jsonify({'ok': False, 'error': 'studentName and studentId required'}), 400
    
    settings = get_settings()
    morning_status = determine_status(morning_time_in, morning_time_out, settings['morning_login_start'], settings['morning_login_end'], settings['morning_logout_start'], settings['morning_logout_end'])
    afternoon_status = determine_status(afternoon_time_in, afternoon_time_out, settings['afternoon_login_start'], settings['afternoon_login_end'], settings['afternoon_logout_start'], settings['afternoon_logout_end'])

    if USE_MYSQL:
        last = execute('INSERT INTO attendance (student_name, student_id, attendance_date, morning_time_in, morning_time_out, morning_status, afternoon_time_in, afternoon_time_out, afternoon_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                       (name, sid, date_text, morning_time_in, morning_time_out, morning_status, afternoon_time_in, afternoon_time_out, afternoon_status))
    else:
        last = execute('INSERT INTO attendance (student_name, student_id, attendance_date, morning_time_in, morning_time_out, morning_status, afternoon_time_in, afternoon_time_out, afternoon_status) VALUES (?,?,?,?,?,?,?,?,?)',
                       (name, sid, date_text, morning_time_in, morning_time_out, morning_status, afternoon_time_in, afternoon_time_out, afternoon_status))
    return jsonify({'ok': True, 'id': last, 'morning_status': morning_status, 'afternoon_status': afternoon_status})



@app.route('/api/attendances/<int:item_id>', methods=['PUT'])
def update_attendance(item_id):
    data = request.get_json() or {}
    name = data.get('studentName', '').strip()
    sid = data.get('studentId', '').strip()
    date_text = data.get('date') or str(date.today())
    
    morning_time_in = data.get('morningTimeIn') or None
    morning_time_out = data.get('morningTimeOut') or None
    afternoon_time_in = data.get('afternoonTimeIn') or None
    afternoon_time_out = data.get('afternoonTimeOut') or None

    if not name or not sid:
        return jsonify({'ok': False, 'error': 'studentName and studentId required'}), 400

    settings = get_settings()
    morning_status = determine_status(morning_time_in, morning_time_out, settings['morning_login_start'], settings['morning_login_end'], settings['morning_logout_start'], settings['morning_logout_end'])
    afternoon_status = determine_status(afternoon_time_in, afternoon_time_out, settings['afternoon_login_start'], settings['afternoon_login_end'], settings['afternoon_logout_start'], settings['afternoon_logout_end'])

    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('UPDATE attendance SET student_name=%s, student_id=%s, attendance_date=%s, morning_time_in=%s, morning_time_out=%s, morning_status=%s, afternoon_time_in=%s, afternoon_time_out=%s, afternoon_status=%s WHERE id=%s',
                    (name, sid, date_text, morning_time_in, morning_time_out, morning_status, afternoon_time_in, afternoon_time_out, afternoon_status, item_id))
        ok = cur.rowcount > 0
        cur.close()
        conn.close()
    else:
        conn = get_conn()
        cur = conn.execute('UPDATE attendance SET student_name=?, student_id=?, attendance_date=?, morning_time_in=?, morning_time_out=?, morning_status=?, afternoon_time_in=?, afternoon_time_out=?, afternoon_status=? WHERE id=?',
                           (name, sid, date_text, morning_time_in, morning_time_out, morning_status, afternoon_time_in, afternoon_time_out, afternoon_status, item_id))
        ok = cur.rowcount > 0
        conn.commit()
        conn.close()

    return jsonify({'ok': ok, 'morning_status': morning_status, 'afternoon_status': afternoon_status})



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


@app.route('/api/settings', methods=['GET'])
def get_settings_endpoint():
    return jsonify(get_settings())


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    data = request.get_json() or {}
    
    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('''UPDATE settings SET 
            morning_login_start=%s, morning_login_end=%s, 
            morning_logout_start=%s, morning_logout_end=%s,
            afternoon_login_start=%s, afternoon_login_end=%s,
            afternoon_logout_start=%s, afternoon_logout_end=%s
            WHERE id=1''',
            (data.get('morning_login_start'), data.get('morning_login_end'),
             data.get('morning_logout_start'), data.get('morning_logout_end'),
             data.get('afternoon_login_start'), data.get('afternoon_login_end'),
             data.get('afternoon_logout_start'), data.get('afternoon_logout_end')))
        ok = cur.rowcount > 0
        cur.close()
        conn.close()
    else:
        with get_conn() as conn:
            cur = conn.execute('''UPDATE settings SET 
                morning_login_start=?, morning_login_end=?, 
                morning_logout_start=?, morning_logout_end=?,
                afternoon_login_start=?, afternoon_login_end=?,
                afternoon_logout_start=?, afternoon_logout_end=?
                WHERE id=1''',
                (data.get('morning_login_start'), data.get('morning_login_end'),
                 data.get('morning_logout_start'), data.get('morning_logout_end'),
                 data.get('afternoon_login_start'), data.get('afternoon_login_end'),
                 data.get('afternoon_logout_start'), data.get('afternoon_logout_end')))
            ok = cur.rowcount > 0
            conn.commit()
    
    return jsonify({'ok': ok})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
else:
    init_db()
