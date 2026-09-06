with open('static/app.js', 'r', encoding='utf-8') as f:
    curr_js = f.read()

with open('scratch/backups/app.js', 'r', encoding='utf-8') as f:
    back_js = f.read()

def extract_snippet(js, pattern, num_lines=30):
    lines = js.splitlines()
    for i, line in enumerate(lines):
        if pattern in line:
            return '\n'.join(lines[i:i+num_lines])
    return "PATTERN NOT FOUND"

print("=== CURRENT addEmployeeForm SUBMIT HANDLER ===")
print(extract_snippet(curr_js, "document.getElementById('addEmployeeForm')", 35))

print("\n=== BACKUP addEmployeeForm SUBMIT HANDLER ===")
print(extract_snippet(back_js, "document.getElementById('addEmployeeForm')", 35))

