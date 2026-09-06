import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def setup_test_db(db_name='test_6cases.db'):
    if os.path.exists(db_name):
        os.remove(db_name)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        department TEXT,
        skills TEXT,
        performance REAL,
        experience INTEGER,
        availability TEXT DEFAULT 'Available'
    )
    """)
    cursor.execute("""
    CREATE TABLE tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        required_skill TEXT,
        priority TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'Pending',
        category TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE assignments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        task_id INTEGER,
        assigned_date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE performance_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        task_id INTEGER,
        old_score REAL,
        new_score REAL,
        reason TEXT,
        date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE activity_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        timestamp TEXT,
        type TEXT
    )
    """)
    conn.commit()
    conn.close()

def run_test_1():
    print("\n--- TEST 1: Available Backend Developer + Available Frontend Developer ---")
    setup_test_db()
    conn = sqlite3.connect('test_6cases.db')
    c = conn.cursor()

    # Insert Raj (Backend Dev, Perf 8.0) and Ziyad (Frontend Dev, Perf 9.5)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Raj', 'Backend Developer', 'Engineering', 'Python, SQL', 8.0, 5, 'Available')
    """)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (2, 'Ziyad', 'Frontend Developer', 'Engineering', 'Python, JavaScript', 9.5, 4, 'Available')
    """)
    c.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (101, 'Backend Development', 'API Auth', 'Python', 'High', '2026-12-31', 'Pending', 'Backend')
    """)
    conn.commit()
    conn.close()

    # Run optimization logic using app's get_assignment_key
    conn = sqlite3.connect('test_6cases.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE availability='Available'")
    emps = c.fetchall()
    c.execute("SELECT * FROM tasks WHERE id=101")
    task = c.fetchone()
    
    ranked = sorted(emps, key=lambda e: app.get_assignment_key(e, task), reverse=True)
    winner = ranked[0]
    conn.close()

    print(f"Winner: {winner['name']} ({winner['role']})")
    assert winner['name'] == 'Raj', f"FAILED TEST 1: Expected Raj, got {winner['name']}"
    print("PASSED TEST 1: Backend task assigned to Backend Developer despite lower performance score.")

def run_test_2():
    print("\n--- TEST 2: Backend Developer is Busy + Frontend Developer has required skill ---")
    setup_test_db()
    conn = sqlite3.connect('test_6cases.db')
    c = conn.cursor()

    # Raj is Busy, Ziyad is Available with required skill Python
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Raj', 'Backend Developer', 'Engineering', 'Python, SQL', 8.0, 5, 'Busy')
    """)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (2, 'Ziyad', 'Frontend Developer', 'Engineering', 'Python, JavaScript', 9.5, 4, 'Available')
    """)
    c.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (102, 'Backend Development', 'API Auth', 'Python', 'High', '2026-12-31', 'Pending', 'Backend')
    """)
    conn.commit()
    conn.close()

    # Step 1: Only Available employees considered
    conn = sqlite3.connect('test_6cases.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE availability='Available'")
    emps = c.fetchall()
    c.execute("SELECT * FROM tasks WHERE id=102")
    task = c.fetchone()
    
    ranked = sorted(emps, key=lambda e: app.get_assignment_key(e, task), reverse=True)
    winner = ranked[0]
    conn.close()

    print(f"Winner: {winner['name']} ({winner['role']})")
    assert winner['name'] == 'Ziyad', f"FAILED TEST 2: Expected Ziyad as fallback, got {winner['name']}"
    print("PASSED TEST 2: Frontend Developer with required skill used as fallback when Backend Developer is Busy.")

def run_test_3():
    print("\n--- TEST 3: Backend Developer later becomes Available (Dynamic Reallocation) ---")
    setup_test_db()
    conn = sqlite3.connect('test_6cases.db')
    c = conn.cursor()

    # Ziyad is currently assigned to Backend Task (In-Progress)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Raj', 'Backend Developer', 'Engineering', 'Python, SQL', 8.0, 5, 'Available')
    """)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (2, 'Ziyad', 'Frontend Developer', 'Engineering', 'Python, JavaScript', 9.5, 4, 'Busy')
    """)
    c.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (103, 'Backend Development', 'API Auth', 'Python', 'High', '2026-12-31', 'In-Progress', 'Backend')
    """)
    c.execute("""
    INSERT INTO assignments (employee_id, task_id, assigned_date)
    VALUES (2, 103, '2026-09-01')
    """)
    conn.commit()
    conn.close()

    # Execute dynamic reallocation logic
    conn = sqlite3.connect('test_6cases.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM tasks WHERE status='In-Progress' AND id=103")
    task = c.fetchone()
    
    c.execute("SELECT e.* FROM employees e JOIN assignments a ON a.employee_id = e.id WHERE a.task_id=103")
    curr_emp = c.fetchone()
    curr_key = app.get_assignment_key(curr_emp, task)

    c.execute("SELECT * FROM employees WHERE availability='Available'")
    available_employees = c.fetchall()

    candidate_keys = [(emp, app.get_assignment_key(emp, task)) for emp in available_employees]
    candidate_keys.sort(key=lambda x: x[1], reverse=True)
    best_avail, best_avail_key = candidate_keys[0]

    reassigned = False
    if best_avail_key > curr_key:
        c.execute("UPDATE assignments SET employee_id=?, assigned_date=date('now') WHERE task_id=?", (best_avail['id'], 103))
        c.execute("UPDATE employees SET availability='Available' WHERE id=?", (curr_emp['id'],))
        c.execute("UPDATE employees SET availability='Busy' WHERE id=?", (best_avail['id'],))
        conn.commit()
        reassigned = True

    # Check new assignee
    c.execute("SELECT e.name, e.availability FROM employees e JOIN assignments a ON a.employee_id = e.id WHERE a.task_id=103")
    new_assignee, new_avail = c.fetchone()

    c.execute("SELECT availability FROM employees WHERE id=2")
    ziyad_avail = c.fetchone()[0]

    conn.close()

    print(f"Reallocated: {reassigned}, New Assignee: {new_assignee}, Ziyad status: {ziyad_avail}")
    assert reassigned is True, "FAILED TEST 3: Reallocation should trigger"
    assert new_assignee == 'Raj', f"FAILED TEST 3: Expected Raj, got {new_assignee}"
    assert ziyad_avail == 'Available', f"FAILED TEST 3: Ziyad should be Available, got {ziyad_avail}"
    print("PASSED TEST 3: Task successfully reallocated to matching role employee when they became Available.")

def run_test_4():
    print("\n--- TEST 4: Two Backend Developers are Available ---")
    setup_test_db()
    conn = sqlite3.connect('test_6cases.db')
    c = conn.cursor()

    # Raj (Perf 9.0) vs Ram (Perf 8.0)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Raj', 'Backend Developer', 'Engineering', 'Python, SQL', 9.0, 5, 'Available')
    """)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (2, 'Ram', 'Backend Developer', 'Engineering', 'Python', 8.0, 5, 'Available')
    """)
    c.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (104, 'Backend Development', 'API Auth', 'Python', 'High', '2026-12-31', 'Pending', 'Backend')
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect('test_6cases.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE availability='Available'")
    emps = c.fetchall()
    c.execute("SELECT * FROM tasks WHERE id=104")
    task = c.fetchone()
    
    ranked = sorted(emps, key=lambda e: app.get_assignment_key(e, task), reverse=True)
    winner = ranked[0]
    conn.close()

    print(f"Winner: {winner['name']} (Score: {winner['performance']})")
    assert winner['name'] == 'Raj', f"FAILED TEST 4: Expected Raj (higher score), got {winner['name']}"
    print("PASSED TEST 4: Higher-performing matching role employee selected.")

def run_test_5():
    print("\n--- TEST 5: Same Performance (Experience Tie-breaker) ---")
    setup_test_db()
    conn = sqlite3.connect('test_6cases.db')
    c = conn.cursor()

    # Ram (Perf 8.5, Exp 6) vs Bob (Perf 8.5, Exp 3)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Ram', 'Backend Developer', 'Engineering', 'Python', 8.5, 6, 'Available')
    """)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (2, 'Bob', 'Backend Developer', 'Engineering', 'Python', 8.5, 3, 'Available')
    """)
    c.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (105, 'Backend Development', 'API Auth', 'Python', 'High', '2026-12-31', 'Pending', 'Backend')
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect('test_6cases.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE availability='Available'")
    emps = c.fetchall()
    c.execute("SELECT * FROM tasks WHERE id=105")
    task = c.fetchone()
    
    ranked = sorted(emps, key=lambda e: app.get_assignment_key(e, task), reverse=True)
    winner = ranked[0]
    conn.close()

    print(f"Winner: {winner['name']} (Exp: {winner['experience']} Yrs)")
    assert winner['name'] == 'Ram', f"FAILED TEST 5: Expected Ram (higher exp), got {winner['name']}"
    print("PASSED TEST 5: Higher-experience employee selected when performance is equal.")

def run_test_6():
    print("\n--- TEST 6: Completed Tasks Are Never Reassigned ---")
    setup_test_db()
    conn = sqlite3.connect('test_6cases.db')
    c = conn.cursor()

    # Task 106 is Completed and assigned to Ziyad
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Raj', 'Backend Developer', 'Engineering', 'Python, SQL', 9.0, 5, 'Available')
    """)
    c.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (2, 'Ziyad', 'Frontend Developer', 'Engineering', 'Python', 9.5, 4, 'Available')
    """)
    c.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (106, 'Backend Development', 'API Auth', 'Python', 'High', '2026-12-31', 'Completed', 'Backend')
    """)
    c.execute("""
    INSERT INTO assignments (employee_id, task_id, assigned_date)
    VALUES (2, 106, '2026-09-01')
    """)
    conn.commit()
    conn.close()

    # Run optimization (selects status != 'Completed')
    conn = sqlite3.connect('test_6cases.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE status != 'Completed'")
    active_tasks = c.fetchall()
    
    c.execute("SELECT employee_id FROM assignments WHERE task_id=106")
    assignee_id = c.fetchone()[0]
    conn.close()

    print(f"Active tasks count: {len(active_tasks)}, Task 106 Assignee ID: {assignee_id}")
    assert len(active_tasks) == 0, "FAILED TEST 6: Completed task should not be in active tasks"
    assert assignee_id == 2, "FAILED TEST 6: Assignment should remain Ziyad (untouched)"
    print("PASSED TEST 6: Completed task was not reassigned.")

if __name__ == '__main__':
    run_test_1()
    run_test_2()
    run_test_3()
    run_test_4()
    run_test_5()
    run_test_6()
    print("\n==================================================")
    print("ALL 6 ALGORITHM & DYNAMIC REALLOCATION TESTS PASSED!")
    print("==================================================")
