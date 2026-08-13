#!/usr/bin/env python3
import requests
import time
import json

# Wait for server to be ready
time.sleep(2)

print("Testing Dual-Period Attendance System\n")

# Test 1: Morning Present (on time), Afternoon Absent
print("Test 1 - Morning Present (7:30), Afternoon Absent (no data):")
r1 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'John Doe',
    'studentId': 'S-001',
    'date': '2026-08-13',
    'morningTimeIn': '07:30',
    'morningTimeOut': '11:30',
})
result1 = r1.json()
print(f"  Expected: Morning=Present, Afternoon=Absent")
print(f"  Actual:   Morning={result1['morning_status']}, Afternoon={result1['afternoon_status']}")
print(f"  ✓ PASS\n" if result1['morning_status'] == 'Present' and result1['afternoon_status'] == 'Absent' else f"  ✗ FAIL\n")

# Test 2: Morning Late, Afternoon Present
print("Test 2 - Morning Late (8:15 after 7:50 window), Afternoon Present (13:30):")
r2 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Jane Smith',
    'studentId': 'S-002',
    'date': '2026-08-13',
    'morningTimeIn': '08:15',
    'morningTimeOut': '11:30',
    'afternoonTimeIn': '13:30',
    'afternoonTimeOut': '17:30',
})
result2 = r2.json()
print(f"  Expected: Morning=Late, Afternoon=Present")
print(f"  Actual:   Morning={result2['morning_status']}, Afternoon={result2['afternoon_status']}")
print(f"  ✓ PASS\n" if result2['morning_status'] == 'Late' and result2['afternoon_status'] == 'Present' else f"  ✗ FAIL\n")

# Test 3: Absent morning (no login), Present afternoon
print("Test 3 - Morning Absent (no login), Afternoon Present (13:30):")
r3 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Bob Wilson',
    'studentId': 'S-003',
    'date': '2026-08-13',
    'afternoonTimeIn': '13:30',
    'afternoonTimeOut': '17:30',
})
result3 = r3.json()
print(f"  Expected: Morning=Absent, Afternoon=Present")
print(f"  Actual:   Morning={result3['morning_status']}, Afternoon={result3['afternoon_status']}")
print(f"  ✓ PASS\n" if result3['morning_status'] == 'Absent' and result3['afternoon_status'] == 'Present' else f"  ✗ FAIL\n")

# Test 4: Afternoon Late (after 13:50 window)
print("Test 4 - Morning Absent (no data), Afternoon Late (14:00 after 13:50 window):")
r4 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Alice Brown',
    'studentId': 'S-004',
    'date': '2026-08-13',
    'afternoonTimeIn': '14:00',
    'afternoonTimeOut': '17:30',
})
result4 = r4.json()
print(f"  Expected: Morning=Absent, Afternoon=Late")
print(f"  Actual:   Morning={result4['morning_status']}, Afternoon={result4['afternoon_status']}")
print(f"  ✓ PASS\n" if result4['morning_status'] == 'Absent' and result4['afternoon_status'] == 'Late' else f"  ✗ FAIL\n")

# Test 5: Absent afternoon (no logout)
print("Test 5 - Morning Present (7:30), Afternoon Absent (no logout):")
r5 = requests.post('http://localhost:8080/api/attendances', json={
    'studentName': 'Charlie Davis',
    'studentId': 'S-005',
    'date': '2026-08-13',
    'morningTimeIn': '07:30',
    'morningTimeOut': '11:30',
    'afternoonTimeIn': '13:30',
})
result5 = r5.json()
print(f"  Expected: Morning=Present, Afternoon=Absent")
print(f"  Actual:   Morning={result5['morning_status']}, Afternoon={result5['afternoon_status']}")
print(f"  ✓ PASS\n" if result5['morning_status'] == 'Present' and result5['afternoon_status'] == 'Absent' else f"  ✗ FAIL\n")

# Test 6: Settings GET
print("Test 6 - Get Current Settings:")
r_settings = requests.get('http://localhost:8080/api/settings')
settings = r_settings.json()
print(f"  Morning Login Window: {settings['morning_login_start']} - {settings['morning_login_end']}")
print(f"  Morning Logout Window: {settings['morning_logout_start']} - {settings['morning_logout_end']}")
print(f"  Afternoon Login Window: {settings['afternoon_login_start']} - {settings['afternoon_login_end']}")
print(f"  Afternoon Logout Window: {settings['afternoon_logout_start']} - {settings['afternoon_logout_end']}\n")

# Display all records
r_all = requests.get('http://localhost:8080/api/attendances')
all_records = r_all.json()
print(f"Total records in system: {len(all_records)}")
if all_records:
    print("\nAll Records:")
    for rec in all_records:
        print(f"  {rec['studentName']} ({rec['studentId']}): "
              f"Morning {rec['morningStatus']}, Afternoon {rec['afternoonStatus']}")
