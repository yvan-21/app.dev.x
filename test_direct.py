import sys
sys.path.insert(0, '.')

import app as a

print("Testing Dual-Period Attendance System\n")

# Clear old test records
a.execute('DELETE FROM attendance WHERE student_id LIKE "T-%"')

client = a.app.test_client()

# Test 1: Morning Present (on time), Afternoon Absent
print("Test 1 - Morning Present (7:30), Afternoon Absent (no data):")
r1 = client.post('/api/attendances', json={
    'studentName': 'Test1 OnTime',
    'studentId': 'T-001',
    'date': '2026-08-14',
    'morningTimeIn': '07:30',
    'morningTimeOut': '11:30',
})
result1 = r1.get_json()
print(f"  Expected: Morning=Present, Afternoon=Absent")
print(f"  Actual:   Morning={result1.get('morning_status', '?')}, Afternoon={result1.get('afternoon_status', '?')}")
status1 = result1.get('morning_status') == 'Present' and result1.get('afternoon_status') == 'Absent'
print(f"  {'PASS' if status1 else 'FAIL'}\n")

# Test 2: Morning Late (8:15, after 7:50 window), Afternoon Present
print("Test 2 - Morning Late (8:15 after 7:50 window), Afternoon Present (13:30):")
r2 = client.post('/api/attendances', json={
    'studentName': 'Test2 Late',
    'studentId': 'T-002',
    'date': '2026-08-14',
    'morningTimeIn': '08:15',
    'morningTimeOut': '11:30',
    'afternoonTimeIn': '13:30',
    'afternoonTimeOut': '17:30',
})
result2 = r2.get_json()
print(f"  Expected: Morning=Late, Afternoon=Present")
print(f"  Actual:   Morning={result2.get('morning_status', '?')}, Afternoon={result2.get('afternoon_status', '?')}")
status2 = result2.get('morning_status') == 'Late' and result2.get('afternoon_status') == 'Present'
print(f"  {'PASS' if status2 else 'FAIL'}\n")

# Test 3: Absent morning (no login), Present afternoon
print("Test 3 - Morning Absent (no login), Afternoon Present (13:30):")
r3 = client.post('/api/attendances', json={
    'studentName': 'Test3 NoMorning',
    'studentId': 'T-003',
    'date': '2026-08-14',
    'afternoonTimeIn': '13:30',
    'afternoonTimeOut': '17:30',
})
result3 = r3.get_json()
print(f"  Expected: Morning=Absent, Afternoon=Present")
print(f"  Actual:   Morning={result3.get('morning_status', '?')}, Afternoon={result3.get('afternoon_status', '?')}")
status3 = result3.get('morning_status') == 'Absent' and result3.get('afternoon_status') == 'Present'
print(f"  {'PASS' if status3 else 'FAIL'}\n")

# Test 4: Afternoon Late
print("Test 4 - Morning Absent (no data), Afternoon Late (14:00 after 13:50 window):")
r4 = client.post('/api/attendances', json={
    'studentName': 'Test4 AfternoonLate',
    'studentId': 'T-004',
    'date': '2026-08-14',
    'afternoonTimeIn': '14:00',
    'afternoonTimeOut': '17:30',
})
result4 = r4.get_json()
print(f"  Expected: Morning=Absent, Afternoon=Late")
print(f"  Actual:   Morning={result4.get('morning_status', '?')}, Afternoon={result4.get('afternoon_status', '?')}")
status4 = result4.get('morning_status') == 'Absent' and result4.get('afternoon_status') == 'Late'
print(f"  {'PASS' if status4 else 'FAIL'}\n")

# Summary
tests = [status1, status2, status3, status4]
passed = sum(tests)
print(f"{'='*60}")
print(f"Summary: {passed}/{len(tests)} tests PASSED")
print(f"{'='*60}\n")

# Show test records
r_all = client.get('/api/attendances')
all_records = r_all.get_json()
print("Test Records Created:")
for rec in all_records:
    if rec['studentId'].startswith('T-'):
        print(f"  {rec['studentName']} ({rec['studentId']}): "
              f"Morning {rec['morningStatus']}, Afternoon {rec['afternoonStatus']}")
