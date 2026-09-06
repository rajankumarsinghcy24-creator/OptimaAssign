import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    curr_html = f.read()

with open('scratch/backups/index.html', 'r', encoding='utf-8') as f:
    back_html = f.read()

with open('static/app.js', 'r', encoding='utf-8') as f:
    curr_js = f.read()

with open('scratch/backups/app.js', 'r', encoding='utf-8') as f:
    back_js = f.read()

print("==================================================")
print("1. FORMS & INPUT IDS COMPARISON")
print("==================================================")

curr_forms = re.findall(r'<form.*?>', curr_html, re.DOTALL)
back_forms = re.findall(r'<form.*?>', back_html, re.DOTALL)

print("Current HTML forms:")
for f in curr_forms:
    print("  ", f)

print("Backup HTML forms:")
for f in back_forms:
    print("  ", f)

print("\n==================================================")
print("2. EMPLOYEE MODAL FORM & INPUTS")
print("==================================================")

def get_modal_snippet(html, modal_id):
    pos = html.find(f'id="{modal_id}"')
    if pos == -1:
        pos = html.find(f"id='{modal_id}'")
    if pos == -1:
        return "NOT FOUND"
    return html[pos:pos+1500]

print("--- Backup employeeModal snippet ---")
print(get_modal_snippet(back_html, 'employeeModal')[:800])

print("\n--- Current employeeModal snippet ---")
print(get_modal_snippet(curr_html, 'employeeModal')[:800])

print("\n==================================================")
print("3. JS FUNCTION DEFINITIONS & EVENT BINDINGS")
print("==================================================")

curr_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', curr_js))
back_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', back_js))

print("Functions in backup JS but missing in current JS:", sorted(list(back_funcs - curr_funcs)))
print("Functions added in current JS:", sorted(list(curr_funcs - back_funcs)))

print("\n==================================================")
print("4. ONCLICK / ONSUBMIT ATTRIBUTES IN HTML")
print("==================================================")

print("Backup HTML inline event attributes:")
for match in re.findall(r'on\w+=["\'][^"\']+["\']', back_html):
    print("  ", match)

print("Current HTML inline event attributes:")
for match in re.findall(r'on\w+=["\'][^"\']+["\']', curr_html):
    print("  ", match)

