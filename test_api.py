import requests
import json

print("Testing Dual-Period Attendance System\n")

# Clear old test records
import mysql.connector
conn = mysql.connector.connect(host='localhost', port=3306, user='root', password='yvan22', database='attendance_db')
cur = conn.cursor()
cur.execute("DELETE FROM attendance WHERE student_id LIKE 'T-%'")
conn.commit()
conn.close()
print("Cleared test records\n")

# Test 1: Morning Present (on time), Afternoon Absent
print("Test 1 - Morning Present (7:30), Afternoon Absent (no data):")
r1 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Test1 OnTime',
    'studentId': 'T-001',
    'date': '2026-08-14',
    'morningTimeIn': '07:30',
    'morningTimeOut': '11:30',
})
result1 = r1.json()
print(f"  Expected: Morning=Present, Afternoon=Absent")
print(f"  Actual:   Morning={result1.get('morning_status', '?')}, Afternoon={result1.get('afternoon_status', '?')}")
status1 = result1.get('morning_status') == 'Present' and result1.get('afternoon_status') == 'Absent'
print(f"  {'✓ PASS' if status1 else '✗ FAIL'}\n")

# Test 2: Morning Late (8:15, after 7:50 window), Afternoon Present
print("Test 2 - Morning Late (8:15 after 7:50 window), Afternoon Present (13:30):")
r2 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Test2 Late',
    'studentId': 'T-002',
    'date': '2026-08-14',
    'morningTimeIn': '08:15',
    'morningTimeOut': '11:30',
    'afternoonTimeIn': '13:30',
    'afternoonTimeOut': '17:30',
})
result2 = r2.json()
print(f"  Expected: Morning=Late, Afternoon=Present")
print(f"  Actual:   Morning={result2.get('morning_status', '?')}, Afternoon={result2.get('afternoon_status', '?')}")
status2 = result2.get('morning_status') == 'Late' and result2.get('afternoon_status') == 'Present'
print(f"  {'✓ PASS' if status2 else '✗ FAIL'}\n")

# Test 3: Absent morning (no login), Present afternoon
print("Test 3 - Morning Absent (no login), Afternoon Present (13:30):")
r3 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Test3 NoMorning',
    'studentId': 'T-003',
    'date': '2026-08-14',
    'afternoonTimeIn': '13:30',
    'afternoonTimeOut': '17:30',
})
result3 = r3.json()
print(f"  Expected: Morning=Absent, Afternoon=Present")
print(f"  Actual:   Morning={result3.get('morning_status', '?')}, Afternoon={result3.get('afternoon_status', '?')}")
status3 = result3.get('morning_status') == 'Absent' and result3.get('afternoon_status') == 'Present'
print(f"  {'✓ PASS' if status3 else '✗ FAIL'}\n")

# Summary
tests = [status1, status2, status3]
passed = sum(tests)
print(f"\n{'='*50}")
print(f"Summary: {passed}/{len(tests)} tests PASSED")
print(f"{'='*50}\n")

# Show all test records
r_all = requests.get('http://localhost:8080/api/attendances')
all_records = r_all.json()
print("Test Records in System:")
for rec in all_records:
    if rec['studentId'].startswith('T-'):
        print(f"  {rec['studentName']} ({rec['studentId']}): "
              f"Morning {rec['morningStatus']}, Afternoon {rec['afternoonStatus']}")
