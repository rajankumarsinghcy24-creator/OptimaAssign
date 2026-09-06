import sqlite3
import os
from datetime import datetime, timedelta
import sys

# Add root folder to sys.path so we can import app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def setup_test_db():
    # Remove existing test db
    if os.path.exists('test_performance.db'):
        os.remove('test_performance.db')
        
    conn = sqlite3.connect('test_performance.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
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
    CREATE TABLE IF NOT EXISTS tasks(
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
    CREATE TABLE IF NOT EXISTS assignments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        task_id INTEGER,
        assigned_date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        file_name TEXT,
        submission_date TEXT,
        status TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance_history(
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
    CREATE TABLE IF NOT EXISTS activity_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        timestamp TEXT,
        type TEXT
    )
    """)
    
    # Insert test employee
    cursor.execute("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability)
    VALUES (1, 'Test Employee', 'Developer', 'Engineering', 'Python', 8.0, 5, 'Available')
    """)
    
    conn.commit()
    conn.close()

def test_performance_logic():
    print("=== STARTING PERFORMANCE SYSTEM TEST ===")
    setup_test_db()
    
    conn = sqlite3.connect('test_performance.db')
    cursor = conn.cursor()
    
    # --- TEST 1: Task completed before deadline (High Priority) ---
    print("\nTEST 1: Task completed before deadline (High Priority)")
    # Task deadline in future
    future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    cursor.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
    VALUES (1, 'Future Task', 'Desc', 'Python', 'High', ?, 'In-Progress')
    """, (future_date,))
    cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (1, 1, '2026-07-01')")
    cursor.execute("""
    INSERT INTO submissions (assignment_id, file_name, submission_date, status)
    VALUES (1, 'file.zip', date('now'), 'Approved')
    """)
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=1")
    
    # Process completion
    app.process_task_completion(cursor, 1, 1)
    
    # Check new performance score
    # Expected: 8.0 + 0.5 (before deadline) + 0.3 (High priority) = 8.8
    cursor.execute("SELECT performance FROM employees WHERE id=1")
    perf_1 = cursor.fetchone()[0]
    print(f"Old score: 8.0, Expected score: 8.8, Actual score: {perf_1}")
    assert perf_1 == 8.8, "Test 1 failed!"
    
    # Check performance history entry
    cursor.execute("SELECT old_score, new_score, reason FROM performance_history WHERE task_id=1")
    hist_1 = cursor.fetchone()
    print(f"History reason: {hist_1[2]}")
    assert hist_1[0] == 8.0 and hist_1[1] == 8.8, "History log 1 failed!"
    
    # --- TEST 2: Task completed exactly on deadline (Medium Priority) ---
    print("\nTEST 2: Task completed exactly on deadline (Medium Priority)")
    today_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
    VALUES (2, 'Today Task', 'Desc', 'Python', 'Medium', ?, 'In-Progress')
    """, (today_date,))
    cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (1, 2, '2026-07-01')")
    cursor.execute("""
    INSERT INTO submissions (assignment_id, file_name, submission_date, status)
    VALUES (2, 'file2.zip', date('now'), 'Approved')
    """)
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=2")
    
    app.process_task_completion(cursor, 1, 2)
    
    # Expected: 8.8 + 0.3 (on deadline) + 0.2 (Medium priority) = 9.3
    cursor.execute("SELECT performance FROM employees WHERE id=1")
    perf_2 = cursor.fetchone()[0]
    print(f"Old score: 8.8, Expected score: 9.3, Actual score: {perf_2}")
    assert perf_2 == 9.3, "Test 2 failed!"
    
    # --- TEST 3: Task completed after deadline (Low Priority) ---
    print("\nTEST 3: Task completed after deadline (Low Priority)")
    past_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    cursor.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
    VALUES (3, 'Past Task', 'Desc', 'Python', 'Low', ?, 'In-Progress')
    """, (past_date,))
    cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (1, 3, '2026-07-01')")
    cursor.execute("""
    INSERT INTO submissions (assignment_id, file_name, submission_date, status)
    VALUES (3, 'file3.zip', date('now'), 'Approved')
    """)
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=3")
    
    app.process_task_completion(cursor, 1, 3)
    
    # Expected: 9.3 - 0.5 (after deadline) + 0.1 (Low priority) = 8.9
    cursor.execute("SELECT performance FROM employees WHERE id=1")
    perf_3 = cursor.fetchone()[0]
    print(f"Old score: 9.3, Expected score: 8.9, Actual score: {perf_3}")
    assert perf_3 == 8.9, "Test 3 failed!"
    
    # --- TEST 4: Score Range Cap bounds [0.0, 10.0] ---
    print("\nTEST 4: Score capping bounds test")
    # Reset employee score to 9.8
    cursor.execute("UPDATE employees SET performance=9.8 WHERE id=1")
    cursor.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
    VALUES (4, 'Cap Task', 'Desc', 'Python', 'High', ?, 'In-Progress')
    """, (future_date,))
    cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (1, 4, '2026-07-01')")
    cursor.execute("""
    INSERT INTO submissions (assignment_id, file_name, submission_date, status)
    VALUES (4, 'file4.zip', date('now'), 'Approved')
    """)
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=4")
    
    app.process_task_completion(cursor, 1, 4)
    
    # Expected: 9.8 + 0.8 = 10.6 -> capped at 10.0
    cursor.execute("SELECT performance FROM employees WHERE id=1")
    perf_4 = cursor.fetchone()[0]
    print(f"Old score: 9.8, Expected score: 10.0, Actual score: {perf_4}")
    assert perf_4 == 10.0, "Test 4 failed!"
    
    # --- TEST 5: Consecutive completions Streak Bonus ---
    print("\nTEST 5: Streak bonus test")
    # Reset score to 5.0
    cursor.execute("UPDATE employees SET performance=5.0 WHERE id=1")
    
    # Insert 5 successful completions in submissions
    # Note: employee 1 has completed tasks 1, 2, 3 (late), 4. Let's delete them all and insert 5 on-time tasks!
    cursor.execute("DELETE FROM assignments")
    cursor.execute("DELETE FROM submissions")
    
    for i in range(1, 6):
        t_id = 10 + i
        cursor.execute("""
        INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
        VALUES (?, 'Streak Task', 'Desc', 'Python', 'Low', ?, 'Completed')
        """, (t_id, future_date))
        cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (1, ?, '2026-07-01')", (t_id,))
        cursor.execute("""
        INSERT INTO submissions (assignment_id, file_name, submission_date, status)
        VALUES (?, 'file.zip', date('now'), 'Approved')
        """, (t_id,))
        
        # Process the completion of the ith task
        app.process_task_completion(cursor, 1, t_id)
        
    # Each on-time Low priority task adds +0.5 + 0.1 = +0.6
    # 5 tasks * 0.6 = +3.0
    # Plus at task 5, a streak of 5 consecutive successes is completed -> Bonus +1.0
    # Total expected score = 5.0 + 3.0 + 1.0 = 9.0
    cursor.execute("SELECT performance FROM employees WHERE id=1")
    perf_5 = cursor.fetchone()[0]
    print(f"Old score: 5.0, Expected score: 9.0, Actual score: {perf_5}")
    assert perf_5 == 9.0, "Streak bonus test failed!"
    
    conn.commit()
    conn.close()
    
    # Cleanup test db
    if os.path.exists('test_performance.db'):
        os.remove('test_performance.db')
        
    print("\n=== ALL PERFORMANCE SYSTEM TESTS PASSED SUCCESSFULLY ===")

if __name__ == '__main__':
    test_performance_logic()
