import mysql.connector

conn = mysql.connector.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    password='yvan22', 
    database='attendance_db'
)
cur = conn.cursor(dictionary=True)

# Check records
cur.execute('SELECT COUNT(*) as cnt FROM attendance')
print('Records in DB:', cur.fetchone()['cnt'])

# Check settings
cur.execute('SELECT * FROM settings WHERE id=1')
s = cur.fetchone()
print('Settings:', 'OK' if s else 'NOT FOUND')

# Show sample records
cur.execute('SELECT student_name, student_id, morning_status, afternoon_status FROM attendance ORDER BY id DESC LIMIT 3')
print('\nRecent records:')
for row in cur.fetchall():
    print(f"  {row['student_name']} ({row['student_id']}): Morning={row['morning_status']}, Afternoon={row['afternoon_status']}")

conn.close()
