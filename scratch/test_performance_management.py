import sqlite3
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def setup_test_db(db_name='test_perf_system.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS tasks")
    cursor.execute("DROP TABLE IF EXISTS assignments")
    cursor.execute("DROP TABLE IF EXISTS submissions")
    cursor.execute("DROP TABLE IF EXISTS performance_history")
    cursor.execute("DROP TABLE IF EXISTS activity_log")

    cursor.execute("""
    CREATE TABLE employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        department TEXT,
        skills TEXT,
        performance REAL CHECK (performance >= 0.0 AND performance <= 10.0),
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
    CREATE TABLE submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        file_name TEXT,
        submission_date TEXT,
        status TEXT
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

def test_score_capping_math():
    print("\n--- TEST 1: Score Capping Math Bounds [0.0, 10.0] ---")
    s1 = app.clamp_performance(9.5 + 0.8)
    s2 = app.clamp_performance(9.8 + 0.5)
    s3 = app.clamp_performance(10.0 + 0.5)
    s4 = app.clamp_performance(0.2 - 0.5)
    s5 = app.clamp_performance(-2.0)

    print(f"9.5 + 0.8 -> {s1}")
    print(f"9.8 + 0.5 -> {s2}")
    print(f"10.0 + 0.5 -> {s3}")
    print(f"0.2 - 0.5 -> {s4}")
    print(f"-2.0 -> {s5}")

    assert s1 == 10.0, f"Expected 10.0, got {s1}"
    assert s2 == 10.0, f"Expected 10.0, got {s2}"
    assert s3 == 10.0, f"Expected 10.0, got {s3}"
    assert s4 == 0.0, f"Expected 0.0, got {s4}"
    assert s5 == 0.0, f"Expected 0.0, got {s5}"
    print("PASSED TEST 1: Score capping math bounds [0.0, 10.0] verified.")

def test_on_time_submission_and_availability():
    print("\n--- TEST 2: On-Time Task Submission & Availability Update ---")
    setup_test_db()
    conn = sqlite3.connect('test_perf_system.db')
    c = conn.cursor()

    c.execute("INSERT INTO employees (id, name, role, performance, availability) VALUES (1, 'Raj', 'Backend Developer', 8.0, 'Busy')")
    
    future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    c.execute("INSERT INTO tasks (id, title, priority, deadline, status) VALUES (201, 'Feature Auth', 'High', ?, 'In-Progress')", (future_date,))
    c.execute("INSERT INTO assignments (id, employee_id, task_id, assigned_date) VALUES (1, 1, 201, '2026-09-01')")
    c.execute("INSERT INTO submissions (id, assignment_id, file_name, submission_date, status) VALUES (1, 201, 'auth.zip', date('now'), 'Approved')")
    c.execute("UPDATE tasks SET status='Completed' WHERE id=201")
    conn.commit()

    app.process_task_completion(c, 1, 201)
    conn.commit()

    c.execute("SELECT performance, availability FROM employees WHERE id=1")
    perf, avail = c.fetchone()
    print(f"Raj New Score: {perf}, Availability: {avail}")

    assert perf == 8.8, f"Expected 8.8, got {perf}"
    assert avail == 'Available', f"Expected Available, got {avail}"

    c.execute("SELECT employee_id, task_id, old_score, new_score, reason FROM performance_history WHERE task_id=201")
    hist = c.fetchone()
    print(f"Performance History Record: {hist}")
    assert hist[0] == 1 and hist[1] == 201 and hist[2] == 8.0 and hist[3] == 8.8, "History record failed"
    conn.close()
    print("PASSED TEST 2: On-time submission increased score, updated availability to Available, and logged history.")

def test_late_submission_penalty():
    print("\n--- TEST 3: Late Submission Penalty ---")
    setup_test_db()
    conn = sqlite3.connect('test_perf_system.db')
    c = conn.cursor()

    c.execute("INSERT INTO employees (id, name, role, performance, availability) VALUES (2, 'Sam', 'QA Engineer', 7.5, 'Busy')")
    
    past_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    c.execute("INSERT INTO tasks (id, title, priority, deadline, status) VALUES (202, 'Smoke Tests', 'Low', ?, 'In-Progress')", (past_date,))
    c.execute("INSERT INTO assignments (id, employee_id, task_id, assigned_date) VALUES (2, 2, 202, '2026-09-01')")
    c.execute("INSERT INTO submissions (id, assignment_id, file_name, submission_date, status) VALUES (2, 202, 'test.zip', date('now'), 'Approved')")
    c.execute("UPDATE tasks SET status='Completed' WHERE id=202")
    conn.commit()

    app.process_task_completion(c, 2, 202)
    conn.commit()

    c.execute("SELECT performance, availability FROM employees WHERE id=2")
    perf, avail = c.fetchone()
    print(f"Sam New Score: {perf}, Availability: {avail}")

    assert perf == 7.1, f"Expected 7.1, got {perf}"
    assert avail == 'Available', f"Expected Available, got {avail}"

    c.execute("SELECT old_score, new_score, reason FROM performance_history WHERE task_id=202")
    hist = c.fetchone()
    print(f"Late Submission History: {hist}")
    assert hist[0] == 7.5 and hist[1] == 7.1, "Late history log failed"
    conn.close()
    print("PASSED TEST 3: Late submission applied penalty and recorded history.")

def test_duplicate_submission_protection():
    print("\n--- TEST 4: Duplicate Submission Protection ---")
    setup_test_db()
    conn = sqlite3.connect('test_perf_system.db')
    c = conn.cursor()

    c.execute("INSERT INTO employees (id, name, role, performance, availability) VALUES (3, 'Ziyad', 'Developer', 9.0, 'Busy')")
    future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    c.execute("INSERT INTO tasks (id, title, priority, deadline, status) VALUES (203, 'Widget UI', 'Medium', ?, 'In-Progress')", (future_date,))
    c.execute("INSERT INTO assignments (id, employee_id, task_id, assigned_date) VALUES (3, 3, 203, '2026-09-01')")
    conn.commit()

    # 1st Completion Process
    app.process_task_completion(c, 3, 203)
    conn.commit()

    c.execute("SELECT performance FROM employees WHERE id=3")
    score_after_first = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM performance_history WHERE task_id=203")
    history_count_1 = c.fetchone()[0]

    # 2nd Completion Attempt for SAME task & employee
    app.process_task_completion(c, 3, 203)
    conn.commit()

    c.execute("SELECT performance FROM employees WHERE id=3")
    score_after_second = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM performance_history WHERE task_id=203")
    history_count_2 = c.fetchone()[0]

    print(f"Score after 1st completion: {score_after_first}")
    print(f"Score after duplicate attempt: {score_after_second}")
    print(f"History records count: {history_count_2}")

    assert score_after_first == score_after_second, "FAILED: Duplicate completion altered score!"
    assert history_count_1 == history_count_2 == 1, "FAILED: Duplicate completion added duplicate history record!"
    conn.close()
    print("PASSED TEST 4: Duplicate submission protection prevented double-counting.")

def test_correct_employee_assignment_target():
    print("\n--- TEST 5: Correct Assigned Employee Target ---")
    setup_test_db()
    conn = sqlite3.connect('test_perf_system.db')
    c = conn.cursor()

    c.execute("INSERT INTO employees (id, name, role, performance, availability) VALUES (10, 'EmpA', 'Dev', 8.0, 'Busy')")
    c.execute("INSERT INTO employees (id, name, role, performance, availability) VALUES (20, 'EmpB', 'Dev', 8.0, 'Available')")

    future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    c.execute("INSERT INTO tasks (id, title, priority, deadline, status) VALUES (204, 'Task For A', 'Medium', ?, 'In-Progress')", (future_date,))
    c.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (10, 204, '2026-09-01')")
    conn.commit()

    c.execute("SELECT employee_id FROM assignments WHERE task_id=204")
    assigned_emp_id = c.fetchone()[0]
    app.process_task_completion(c, assigned_emp_id, 204)
    conn.commit()

    c.execute("SELECT performance, availability FROM employees WHERE id=10")
    perf_A, avail_A = c.fetchone()
    c.execute("SELECT performance, availability FROM employees WHERE id=20")
    perf_B, avail_B = c.fetchone()

    print(f"EmpA (Assigned): Score {perf_A}, Avail {avail_A}")
    print(f"EmpB (Unassigned): Score {perf_B}, Avail {avail_B}")

    assert perf_A > 8.0 and avail_A == 'Available', "EmpA should receive update"
    assert perf_B == 8.0 and avail_B == 'Available', "EmpB should remain unchanged"
    conn.close()
    print("PASSED TEST 5: Only the correctly assigned employee received performance update.")

if __name__ == '__main__':
    test_score_capping_math()
    test_on_time_submission_and_availability()
    test_late_submission_penalty()
    test_duplicate_submission_protection()
    test_correct_employee_assignment_target()
    print("\n==================================================")
    print("ALL PERFORMANCE SYSTEM VERIFICATION TESTS PASSED!")
    print("==================================================")
