import re
import difflib

with open('templates/index.html', 'r', encoding='utf-8') as f:
    curr_html = f.read()

with open('scratch/backups/index.html', 'r', encoding='utf-8') as f:
    back_html = f.read()

with open('static/app.js', 'r', encoding='utf-8') as f:
    curr_js = f.read()

with open('scratch/backups/app.js', 'r', encoding='utf-8') as f:
    back_js = f.read()

with open('app.py', 'r', encoding='utf-8') as f:
    curr_py = f.read()

with open('scratch/backups/app.py', 'r', encoding='utf-8') as f:
    back_py = f.read()

print("==================================================")
print("1. MISSING DOM ELEMENT IDS")
print("==================================================")

js_ids = set(re.findall(r"document\.getElementById\(['\"](.*?)['\"]\)", curr_js))
html_ids = set(re.findall(r"id=['\"](.*?)['\"]", curr_html))

missing_ids = js_ids - html_ids
print("Referenced IDs in app.js missing from index.html:", sorted(list(missing_ids)))

print("\n==================================================")
print("2. CHECKING FORMS & MODALS IN HTML")
print("==================================================")

forms_to_check = ['employeeForm', 'taskForm', 'submissionForm', 'editEmployeeForm', 'editTaskForm', 'empForm', 'tskForm']
for fid in forms_to_check:
    print(f"Form ID '{fid}': in curr HTML? {fid in curr_html} | in backup HTML? {fid in back_html} | in curr JS? {fid in curr_js} | in backup JS? {fid in back_js}")

modals_to_check = ['employeeModal', 'taskModal', 'editEmployeeModal', 'editTaskModal', 'addEmployeeModal', 'addTaskModal']
for mid in modals_to_check:
    print(f"Modal ID '{mid}': in curr HTML? {mid in curr_html} | in backup HTML? {mid in back_html} | in curr JS? {mid in curr_js} | in backup JS? {mid in back_js}")

buttons_to_check = ['openEmployeeModal', 'openTaskModal', 'runOptimizationBtn', 'resetDataBtn', 'quickAddEmpBtn', 'quickAddTaskBtn']
for bid in buttons_to_check:
    print(f"Button ID '{bid}': in curr HTML? {bid in curr_html} | in backup HTML? {bid in back_html} | in curr JS? {bid in curr_js} | in backup JS? {bid in back_js}")

print("\n==================================================")
print("3. CHECKING JS EVENT LISTENERS & HANDLERS")
print("==================================================")

listeners_curr = re.findall(r"document\.getElementById\(['\"](.*?)['\"]\)\.addEventListener\(['\"](.*?)['\"]", curr_js)
listeners_back = re.findall(r"document\.getElementById\(['\"](.*?)['\"]\)\.addEventListener\(['\"](.*?)['\"]", back_js)

print("Current app.js event listeners count:", len(listeners_curr))
print("Backup app.js event listeners count:", len(listeners_back))

curr_target_ids = set(t[0] for t in listeners_curr)
back_target_ids = set(t[0] for t in listeners_back)

print("\nListeners in Backup app.js but missing/changed in Current app.js:")
for t in sorted(list(back_target_ids - curr_target_ids)):
    print(" - Missing event listener on ID:", t)

print("\n==================================================")
print("4. CHECKING API ENDPOINTS IN APP.PY vs APP.JS")
print("==================================================")

py_routes_curr = set(re.findall(r"@app\.route\(['\"](.*?)['\"]", curr_py))
py_routes_back = set(re.findall(r"@app\.route\(['\"](.*?)['\"]", back_py))

js_fetches_curr = set(re.findall(r"fetch\(['\"](.*?)['\"]", curr_js))
js_fetches_back = set(re.findall(r"fetch\(['\"](.*?)['\"]", back_js))

print("Routes removed from app.py:", sorted(list(py_routes_back - py_routes_curr)))
print("Routes added to app.py:", sorted(list(py_routes_curr - py_routes_back)))

print("Fetches in backup JS:", sorted(list(js_fetches_back)))
print("Fetches in current JS:", sorted(list(js_fetches_curr)))

