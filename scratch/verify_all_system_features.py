import os
import sys
import sqlite3
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def test_full_system_workflow():
    print("==================================================")
    print("INTEGRATION TEST: FULL WORKFLOW & API VERIFICATION")
    print("==================================================")

    flask_app = app.app
    flask_app.testing = True
    client = flask_app.test_client()

    # 1. Reset database to clean initial state
    res_reset = client.post('/api/reset_data')
    assert res_reset.status_code == 200, "Reset data failed"
    print("Database reset to initial demo dataset.")

    # 2. Test /api/state
    res = client.get('/api/state')
    assert res.status_code == 200, f"Failed /api/state: {res.status_code}"
    state = json.loads(res.data.decode('utf-8'))
    print(f"State fetched: {len(state['employees'])} employees, {len(state['tasks'])} tasks.")

    # 3. Insert Raj, Ram, Ziyad to explicitly test the User Request Scenario!
    conn = app.get_db_connection()
    c = conn.cursor()

    # Clear existing employees and tasks for controlled test
    c.execute("DELETE FROM employees")
    c.execute("DELETE FROM tasks")
    c.execute("DELETE FROM assignments")
    c.execute("DELETE FROM submissions")

    employees = [
        (10, 'Raj', 'Backend Developer', 'Engineering', 'Python, SQL', 9.0, 5, 'Available', '', 'Online'),
        (11, 'Ram', 'Backend Developer', 'Engineering', 'Python', 8.0, 4, 'Available', '', 'Online'),
        (12, 'Ziyad', 'Frontend Developer', 'Engineering', 'Python, JavaScript', 9.5, 3, 'Available', '', 'Online')
    ]
    c.executemany("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability, avatar_url, online_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees)

    tasks = [
        (100, 'Backend API Development', 'Build REST endpoints for auth.', 'Python', 'High', '2026-12-31', 'Pending', 'Backend')
    ]
    c.executemany("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tasks)

    conn.commit()
    conn.close()

    # 4. Trigger optimization via API
    res_opt = client.get('/run_optimization?format=json')
    assert res_opt.status_code == 200, f"Optimization failed: {res_opt.status_code}"
    opt_data = json.loads(res_opt.data.decode('utf-8'))
    print(f"Optimization Result: {opt_data}")

    # Check assignment in DB
    conn = app.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT employee_id FROM assignments WHERE task_id=100")
    assigned_emp_id = c.fetchone()[0]

    c.execute("SELECT name, role FROM employees WHERE id=?", (assigned_emp_id,))
    assignee_name, assignee_role = c.fetchone()
    conn.close()

    print(f"Assigned Employee: {assignee_name} ({assignee_role})")
    assert assignee_name == 'Raj', f"ERROR: Task assigned to {assignee_name} instead of Raj!"
    print("SUCCESS: Greedy Algorithm correctly assigned Backend task to Raj over Ziyad (9.5 score Frontend Developer).")

    # 5. Test task completion & performance score capping
    conn = app.get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE employees SET performance=9.8 WHERE id=10")
    conn.commit()
    conn.close()

    res_sub = client.post('/submit_work?format=json', data={'task_id': 'task-100'})
    assert res_sub.status_code == 200, f"Task submission failed: {res_sub.status_code}"

    # Verify score clamped to 10.0 and task status Completed and employee Available
    conn = app.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT performance, availability FROM employees WHERE id=10")
    raj_perf, raj_avail = c.fetchone()
    c.execute("SELECT status FROM tasks WHERE id=100")
    task_status = c.fetchone()[0]
    conn.close()

    print(f"Raj New Performance: {raj_perf} (Availability: {raj_avail})")
    print(f"Task 100 Status: {task_status}")

    assert raj_perf == 10.0, f"ERROR: Performance score was {raj_perf}, expected capped at 10.0!"
    assert raj_avail == 'Available', f"ERROR: Employee availability was {raj_avail}, expected Available!"
    assert task_status == 'Completed', f"ERROR: Task status was {task_status}, expected Completed!"

    print("SUCCESS: Task Submission, Capping Score at 10.0, and Availability Auto-Refresh verified!")

    # Restore default demo dataset
    client.post('/api/reset_data')
    print("Database restored to demo dataset.")

if __name__ == '__main__':
    test_full_system_workflow()
    print("\nALL SYSTEM INTEGRATION TESTS PASSED SUCCESSFULLY!")
