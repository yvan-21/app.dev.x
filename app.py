from flask import Flask, request, jsonify, send_file
import sqlite3
import os
from pathlib import Path
from datetime import date, datetime, time, timedelta

DB_PATH = Path(__file__).parent / 'attendance.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_name TEXT NOT NULL,
  student_id TEXT NOT NULL,
  attendance_date TEXT NOT NULL,
  time_in TEXT,
  time_out TEXT,
  status TEXT NOT NULL
);
'''

app = Flask(__name__)

USE_MYSQL = bool(os.getenv('DB_HOST'))


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
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'attendance_db'),
        autocommit=True,
    )


def get_conn():
    return get_conn_mysql() if USE_MYSQL else get_conn_sqlite()


def init_db():
    if USE_MYSQL:
        # ensure table exists in MySQL
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
          status VARCHAR(50) NOT NULL
        )
        ''')
        cur.close()
        conn.close()
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with get_conn() as conn:
            conn.executescript(SCHEMA)


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
    return jsonify(rows)


@app.route('/api/attendances/<int:item_id>', methods=['GET'])
def get_attendance(item_id):
    r = query_one('SELECT * FROM attendance WHERE id=%s' if USE_MYSQL else 'SELECT * FROM attendance WHERE id=?', (item_id,))
    return (jsonify(r) if r else ('', 404))


@app.route('/api/attendances', methods=['POST'])
def create_attendance():
    data = request.get_json() or {}
    name = data.get('studentName', '').strip()
    sid = data.get('studentId', '').strip()
    date_text = data.get('date') or str(date.today())
    time_in = data.get('timeIn') or None
    time_out = data.get('timeOut') or None
    status = data.get('status') or 'Present'

    if not name or not sid:
        return jsonify({'ok': False, 'error': 'studentName and studentId required'}), 400

    if USE_MYSQL:
        last = execute('INSERT INTO attendance (student_name, student_id, attendance_date, time_in, time_out, status) VALUES (%s,%s,%s,%s,%s,%s)',
                       (name, sid, date_text, time_in, time_out, status))
    else:
        last = execute('INSERT INTO attendance (student_name, student_id, attendance_date, time_in, time_out, status) VALUES (?,?,?,?,?,?)',
                       (name, sid, date_text, time_in, time_out, status))
    return jsonify({'ok': True, 'id': last})


@app.route('/api/attendances/<int:item_id>', methods=['PUT'])
def update_attendance(item_id):
    data = request.get_json() or {}
    name = data.get('studentName', '').strip()
    sid = data.get('studentId', '').strip()
    date_text = data.get('date') or str(date.today())
    time_in = data.get('timeIn') or None
    time_out = data.get('timeOut') or None
    status = data.get('status') or 'Present'

    if not name or not sid:
        return jsonify({'ok': False, 'error': 'studentName and studentId required'}), 400

    if USE_MYSQL:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('UPDATE attendance SET student_name=%s, student_id=%s, attendance_date=%s, time_in=%s, time_out=%s, status=%s WHERE id=%s',
                    (name, sid, date_text, time_in, time_out, status, item_id))
        ok = cur.rowcount > 0
        cur.close()
        conn.close()
    else:
        conn = get_conn()
        cur = conn.execute('UPDATE attendance SET student_name=?, student_id=?, attendance_date=?, time_in=?, time_out=?, status=? WHERE id=?',
                           (name, sid, date_text, time_in, time_out, status, item_id))
        ok = cur.rowcount > 0
        conn.commit()
        conn.close()

    return jsonify({'ok': ok})


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
