import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    curr_html = f.read()

with open('scratch/backups/index.html', 'r', encoding='utf-8') as f:
    back_html = f.read()

with open('static/app.js', 'r', encoding='utf-8') as f:
    curr_js = f.read()

with open('scratch/backups/app.js', 'r', encoding='utf-8') as f:
    back_js = f.read()

print("=== SEARCH FOR addEmployeeForm IN JS ===")
for line in curr_js.splitlines():
    if 'addEmployeeForm' in line or 'addEmployeeModal' in line or 'openEmployeeModal' in line or 'emp' in line.lower() and 'modal' in line.lower() or 'emp' in line.lower() and 'form' in line.lower():
        print("CURR JS:", line)

print("\n=== SEARCH FOR addEmployeeForm IN BACKUP JS ===")
for line in back_js.splitlines():
    if 'addEmployeeForm' in line or 'addEmployeeModal' in line or 'openEmployeeModal' in line or 'emp' in line.lower() and 'modal' in line.lower() or 'emp' in line.lower() and 'form' in line.lower():
        print("BACK JS:", line)

