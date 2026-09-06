import sqlite3
import os
import sys

# Append the root directory to path to import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import check_role_match, check_skill_match, calculate_priority_score, get_assignment_key

def verify_greedy_algorithm():
    print("=== STARTING GREEDY ALGORITHM VERIFICATION ===")
    
    # 1. Test case-insensitivity and similar skills
    print("Testing skill matching:")
    assert check_skill_match("Python, SQL, Django", "Python") == 10.0, "Exact match failed"
    assert check_skill_match("Java", "Python") == 0.0, "Incorrect match returned non-zero"
    assert check_skill_match("Django", "Python") == 5.0, "Similar skill match failed"
    print("[OK] Skill matching verified.")

    # 2. Test Role Matching
    print("Testing role matching:")
    assert check_role_match("Backend Developer", "Backend Development", "Python task", "Python") == 10.0, "Role match failed"
    assert check_role_match("Frontend Developer", "Backend Development", "Python task", "Python") == 0.0, "Incorrect role match returned non-zero"
    print("[OK] Role matching verified.")

    # 3. Test Priority Score calculation
    print("Testing Priority Score Calculation:")
    raj = {'role': 'Backend Developer', 'skills': 'Python, SQL, Django', 'performance': 9.0, 'experience': 5}
    ram = {'role': 'Backend Developer', 'skills': 'Java', 'performance': 8.0, 'experience': 6}
    ziyad = {'role': 'Frontend Developer', 'skills': 'Python, JavaScript', 'performance': 9.5, 'experience': 4}
    task = {'title': 'Backend Development', 'description': 'Backend Development Task', 'required_skill': 'Python'}
    
    raj_score = calculate_priority_score(raj, task)
    ram_score = calculate_priority_score(ram, task)
    ziyad_score = calculate_priority_score(ziyad, task)
    
    print(f"Raj (Backend + Python): {raj_score} (Expected 9.3)")
    print(f"Ram (Backend + Java): {ram_score} (Expected 6.2)")
    print(f"Ziyad (Frontend + Python): {ziyad_score} (Expected 5.3)")
    
    assert raj_score == 9.3, "Raj score calculated incorrectly"
    assert ram_score == 6.2, "Ram score calculated incorrectly"
    assert ziyad_score == 5.3, "Ziyad score calculated incorrectly"
    print("[OK] Priority scores verified.")

    # 4. End-to-end database simulation
    print("Testing end-to-end assignments:")
    db_path = 'test_database.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE employees(
        id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        skills TEXT,
        performance REAL,
        experience INTEGER,
        availability TEXT DEFAULT 'Available'
    )""")
    
    cursor.execute("""
    CREATE TABLE tasks(
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        required_skill TEXT,
        priority TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'Pending'
    )""")
    
    cursor.execute("""
    CREATE TABLE assignments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        task_id INTEGER,
        assigned_date TEXT
    )""")
    
    # Insert Test Employees
    cursor.executemany("""
    INSERT INTO employees (id, name, role, skills, performance, experience, availability)
    VALUES (?, ?, ?, ?, ?, ?, ?)""", [
        (1, 'Raj', 'Backend Developer', 'Python, SQL, Django', 9.0, 5, 'Available'),
        (2, 'Ram', 'Backend Developer', 'Java', 8.0, 6, 'Available'),
        (3, 'Ziyad', 'Frontend Developer', 'Python, JavaScript', 9.5, 4, 'Available')
    ])
    
    # Insert Test Task
    cursor.execute("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)""", (1, 'Backend Development', 'Backend Development', 'Python', 'High', '2026-07-20', 'Pending'))
    
    conn.commit()
    
    # Simulation of pending task allocation
    cursor.execute("SELECT * FROM tasks WHERE status = 'Pending'")
    pending_tasks = cursor.fetchall()
    
    for t_row in pending_tasks:
        task_id, title, desc, req_skill, priority, deadline, status = t_row
        task_dict = {'title': title, 'description': desc, 'required_skill': req_skill}
        
        cursor.execute("SELECT * FROM employees WHERE availability='Available'")
        available_employees = cursor.fetchall()
        
        candidate_keys = []
        for emp_row in available_employees:
            emp_dict = {
                'id': emp_row[0],
                'name': emp_row[1],
                'role': emp_row[2],
                'skills': emp_row[3],
                'performance': emp_row[4],
                'experience': emp_row[5],
                'availability': emp_row[6]
            }
            key = get_assignment_key(emp_dict, task_dict)
            score = calculate_priority_score(emp_dict, task_dict)
            candidate_keys.append((emp_row[0], emp_row[1], key, score))
            
        candidate_keys.sort(key=lambda x: x[2], reverse=True)
        best_emp_id, best_emp_name, best_key, best_score = candidate_keys[0]
        
        print(f"Assigned task to: {best_emp_name} with key {best_key}")
        assert best_emp_name == 'Raj', "Expected Raj to be assigned"
        
        # Update assignment
        cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (?, ?, '2026-07-11')", (best_emp_id, 1))
        cursor.execute("UPDATE tasks SET status='In-Progress' WHERE id=?", (1,))
        cursor.execute("UPDATE employees SET availability='Busy' WHERE id=?", (best_emp_id,))
        
    conn.commit()
    
    # 5. Test Dynamic Reallocation
    print("\nTesting Dynamic Reallocation scenario:")
    
    # Amit joins and is Available
    cursor.execute("""
    INSERT INTO employees (id, name, role, skills, performance, experience, availability)
    VALUES (?, ?, ?, ?, ?, ?, ?)""", (4, 'Amit', 'Backend Developer', 'Python, SQL', 8.5, 5, 'Available'))
    conn.commit()
    
    # Reset assignment: set Task 1 assignee to Ziyad (id=3), set Ziyad to Busy, set Raj to Available
    cursor.execute("DELETE FROM assignments")
    cursor.execute("INSERT INTO assignments (employee_id, task_id, assigned_date) VALUES (?, ?, '2026-07-11')", (3, 1))
    cursor.execute("UPDATE employees SET availability='Available' WHERE id=1") # Raj
    cursor.execute("UPDATE employees SET availability='Busy' WHERE id=3") # Ziyad
    cursor.execute("UPDATE employees SET availability='Available' WHERE id=4") # Amit
    conn.commit()
    
    # Run reallocation step
    cursor.execute("SELECT * FROM tasks WHERE status = 'In-Progress'")
    in_progress = cursor.fetchall()
    
    for t_row in in_progress:
        task_id, title, desc, req_skill, priority, deadline, status = t_row
        task_dict = {'title': title, 'description': desc, 'required_skill': req_skill}
        
        # Current assignee
        cursor.execute("SELECT e.* FROM employees e JOIN assignments a ON a.employee_id = e.id WHERE a.task_id = ?", (task_id,))
        curr_row = cursor.fetchone()
        curr_dict = {
            'id': curr_row[0],
            'name': curr_row[1],
            'role': curr_row[2],
            'skills': curr_row[3],
            'performance': curr_row[4],
            'experience': curr_row[5],
            'availability': curr_row[6]
        }
        curr_key = get_assignment_key(curr_dict, task_dict)
        curr_score = calculate_priority_score(curr_dict, task_dict)
        
        # Available employees
        cursor.execute("SELECT * FROM employees WHERE availability='Available'")
        available = cursor.fetchall()
        
        candidate_keys = []
        for emp_row in available:
            emp_dict = {
                'id': emp_row[0],
                'name': emp_row[1],
                'role': emp_row[2],
                'skills': emp_row[3],
                'performance': emp_row[4],
                'experience': emp_row[5],
                'availability': emp_row[6]
            }
            key = get_assignment_key(emp_dict, task_dict)
            score = calculate_priority_score(emp_dict, task_dict)
            candidate_keys.append((emp_row[0], emp_row[1], key, score))
            
        if candidate_keys:
            candidate_keys.sort(key=lambda x: x[2], reverse=True)
            best_avail_id, best_avail_name, best_avail_key, best_avail_score = candidate_keys[0]
            print(f"Current assignee: {curr_dict['name']} (Key {curr_key}, Score {curr_score})")
            print(f"Best available: {best_avail_name} (Key {best_avail_key}, Score {best_avail_score})")
            
            if best_avail_key > curr_key:
                print(f"Reassigning task to {best_avail_name}!")
                assert best_avail_name == 'Amit' or best_avail_name == 'Raj', "Expected Amit or Raj to be chosen"
                print(f"[OK] Reallocation prioritised the absolute best match: {best_avail_name} over Ziyad.")
                
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("=== GREEDY ALGORITHM VERIFICATION SUCCESSFUL ===")

if __name__ == '__main__':
    verify_greedy_algorithm()
