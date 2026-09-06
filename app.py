from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection(db_name='database.db'):
    return sqlite3.connect(db_name, timeout=15)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Employees Table with new columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        department TEXT,
        skills TEXT,
        performance REAL,
        experience INTEGER,
        availability TEXT DEFAULT 'Available',
        avatar_url TEXT,
        online_status TEXT DEFAULT 'Online'
    )
    """)

    # Create Tasks Table with category column
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

    # Create Assignments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        task_id INTEGER,
        assigned_date TEXT
    )
    """)

    # Create Submissions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        file_name TEXT,
        submission_date TEXT,
        status TEXT
    )
    """)

    # Create Activity Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        timestamp TEXT,
        type TEXT
    )
    """)

    # Create Performance History Table
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

    conn.commit()

    # Dynamic migrations: ensure columns exist
    cursor.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'department' not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN department TEXT DEFAULT 'Engineering'")
    if 'avatar_url' not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN avatar_url TEXT")
    if 'online_status' not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN online_status TEXT DEFAULT 'Online'")

    cursor.execute("PRAGMA table_info(tasks)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'General'")

    conn.commit()

    # Seed with initial mockup data if employees table is empty
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        seed_db_data(cursor)
        conn.commit()

    conn.close()

def seed_db_data(cursor):
    # Reset all tables
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM assignments")
    cursor.execute("DELETE FROM submissions")
    cursor.execute("DELETE FROM activity_log")

    employees = [
        (1, 'Sarah Connor', 'Lead DevOps Architect', 'DevOps', 'Docker, AWS, Kubernetes, Python', 9.6, 8, 'Busy', 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&h=150&q=80', 'Online'),
        (2, 'Marcus Wright', 'Senior Backend Engineer', 'Backend', 'Python, SQL, Django, API', 8.8, 6, 'Busy', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&h=150&q=80', 'Online'),
        (3, 'Kyle Reese', 'Frontend Developer', 'Frontend', 'JavaScript, CSS, React, HTML', 8.2, 4, 'Available', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&h=150&q=80', 'Offline'),
        (4, 'John Connor', 'Machine Learning Specialist', 'Data Science', 'Python, PyTorch, SQL, Math', 9.4, 5, 'Available', 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&h=150&q=80', 'Online'),
        (5, 'Kate Brewster', 'QA Automation Engineer', 'Quality Assurance', 'Python, Selenium, CSS, JavaScript', 7.9, 3, 'Available', 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=150&h=150&q=80', 'Online'),
        (6, 'Grace Harper', 'Database Administrator', 'Database', 'SQL, Postgres, AWS, Optimization', 8.5, 7, 'Available', 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&h=150&q=80', 'Offline')
    ]
    cursor.executemany("""
    INSERT INTO employees (id, name, role, department, skills, performance, experience, availability, avatar_url, online_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees)

    tasks = [
        (1, 'Deploy Kubernetes Cluster', 'Set up multi-region high-availability EKS cluster for staging environment.', 'Kubernetes', 'High', '2026-07-20', 'In-Progress', 'DevOps'),
        (2, 'Optimize SQL Query Performance', 'Profile and index main reporting tables to reduce load time under 200ms.', 'SQL', 'High', '2026-07-15', 'Pending', 'Database'),
        (3, 'Implement CSS Glassmorphism UI', 'Create a modern, clean visual look with blurred backdrops and custom scrollbars.', 'CSS', 'Medium', '2026-07-25', 'Pending', 'Frontend'),
        (4, 'Refactor Django Authentication Rest API', 'Migrate old session endpoints to secure JWT and OAuth2 integration.', 'API', 'High', '2026-07-14', 'In-Progress', 'Backend'),
        (5, 'Build React Dashboard Widgets', 'Implement interactive SVG charts for the executive operations board.', 'React', 'Medium', '2026-07-28', 'Completed', 'Frontend'),
        (6, 'Configure Selenium Smoke Tests', 'Automate user checkout flow verification on mobile and desktop viewports.', 'Selenium', 'Low', '2026-07-30', 'Pending', 'QA')
    ]
    cursor.executemany("""
    INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status, category)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tasks)

    assignments = [
        (1, 1, 1, '2026-07-05'),
        (2, 2, 4, '2026-07-04')
    ]
    cursor.executemany("""
    INSERT INTO assignments (id, employee_id, task_id, assigned_date)
    VALUES (?, ?, ?, ?)
    """, assignments)

    submissions = [
        (1, 5, 'dashboard-widgets-react.zip', '2026-07-06 14:30', 'Approved')
    ]
    cursor.executemany("""
    INSERT INTO submissions (id, assignment_id, file_name, submission_date, status)
    VALUES (?, ?, ?, ?, ?)
    """, submissions)

    # Pre-populate activity logs
    logs = [
        ("System initialised with default demo dataset.", '2026-07-11 09:00:00', 'system'),
        ("Sarah Connor assigned to Deploy Kubernetes Cluster.", '2026-07-11 09:05:00', 'assignment'),
        ("Marcus Wright assigned to Refactor Django Authentication Rest API.", '2026-07-11 09:10:00', 'assignment'),
        ("Kyle Reese completed Build React Dashboard Widgets. Performance rating increased.", '2026-07-11 09:15:00', 'completion')
    ]
    cursor.executemany("""
    INSERT INTO activity_log (message, timestamp, type)
    VALUES (?, ?, ?)
    """, logs)

# Run database setup
init_db()

def log_activity(message, type="info", cursor=None):
    try:
        if cursor:
            cursor.execute("""
            INSERT INTO activity_log (message, timestamp, type)
            VALUES (?, datetime('now', 'localtime'), ?)
            """, (message, type))
        else:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
            INSERT INTO activity_log (message, timestamp, type)
            VALUES (?, datetime('now', 'localtime'), ?)
            """, (message, type))
            conn.commit()
            conn.close()
    except Exception as e:
        print("Error logging activity:", e)

def check_role_match(emp_role, task_title, task_desc, required_skill):
    emp_role_lower = emp_role.lower() if emp_role else ""
    task_title_lower = task_title.lower() if task_title else ""
    task_desc_lower = task_desc.lower() if task_desc else ""
    task_skill_lower = required_skill.lower() if required_skill else ""
    
    # Classify task
    is_backend = any(kw in task_title_lower or kw in task_desc_lower or kw in task_skill_lower 
                     for kw in ["backend", "api", "django", "server", "django rest", "java", "sql query", "database rest api"])
    is_frontend = any(kw in task_title_lower or kw in task_desc_lower or kw in task_skill_lower 
                      for kw in ["frontend", "css", "react", "html", "ui", "ux", "glassmorphism", "widget", "dashboard widgets"])
    is_db = any(kw in task_title_lower or kw in task_desc_lower or kw in task_skill_lower 
                for kw in ["database", "sql", "postgres", "query", "dba", "index main reporting"])
    is_qa = any(kw in task_title_lower or kw in task_desc_lower or kw in task_skill_lower 
                for kw in ["qa", "selenium", "test", "automation", "smoke tests"])
    is_devops = any(kw in task_title_lower or kw in task_desc_lower or kw in task_skill_lower 
                    for kw in ["devops", "kubernetes", "docker", "eks", "aws", "deploy"])
    is_ml = any(kw in task_title_lower or kw in task_desc_lower or kw in task_skill_lower 
                for kw in ["machine learning", "ml", "ai", "pytorch", "tensorflow", "math"])

    # Match specific role keywords
    if is_backend and "backend" in emp_role_lower:
        return 10.0
    if is_frontend and "frontend" in emp_role_lower:
        return 10.0
    if is_db and any(kw in emp_role_lower for kw in ["database", "dba"]):
        return 10.0
    if is_qa and any(kw in emp_role_lower for kw in ["qa", "test"]):
        return 10.0
    if is_devops and any(kw in emp_role_lower for kw in ["devops", "architect", "infrastructure"]):
        return 10.0
    if is_ml and any(kw in emp_role_lower for kw in ["machine learning", "ml", "specialist"]):
        return 10.0

    # Generic developers fallback (if role is developer or engineer but has no direct conflict)
    if "developer" in emp_role_lower or "engineer" in emp_role_lower:
        categories = ["backend", "frontend", "database", "dba", "qa", "test", "devops", "machine learning", "ml"]
        has_other_category = any(cat in emp_role_lower for cat in categories if (
            (cat == "backend" and not is_backend) or
            (cat == "frontend" and not is_frontend) or
            ((cat == "database" or cat == "dba") and not is_db) or
            ((cat == "qa" or cat == "test") and not is_qa) or
            (cat == "devops" and not is_devops) or
            ((cat == "machine learning" or cat == "ml") and not is_ml)
        ))
        if not has_other_category:
            return 5.0
            
    return 0.0

def check_skill_match(emp_skills, required_skill):
    if not emp_skills or not required_skill:
        return 0.0
    emp_skills_list = [s.strip().lower() for s in emp_skills.split(',') if s.strip()]
    req_skill_clean = required_skill.strip().lower()
    
    if req_skill_clean in emp_skills_list:
        return 10.0
        
    related = {
        "python": ["django", "sql", "api", "pytorch", "math", "kubernetes"],
        "sql": ["postgres", "django", "api", "optimization", "python"],
        "postgres": ["sql", "optimization", "aws"],
        "django": ["python", "sql", "api"],
        "api": ["python", "django", "sql", "javascript"],
        "kubernetes": ["docker", "aws"],
        "docker": ["kubernetes", "aws", "python"],
        "aws": ["docker", "kubernetes", "postgres"],
        "javascript": ["react", "html", "css", "selenium"],
        "react": ["javascript", "html", "css"],
        "css": ["html", "javascript", "react"],
        "html": ["css", "javascript", "react"],
        "selenium": ["python", "javascript", "css"],
        "pytorch": ["python", "math"],
        "math": ["pytorch", "python"]
    }
    
    if req_skill_clean in related:
        for sim_skill in related[req_skill_clean]:
            if sim_skill in emp_skills_list:
                return 5.0
                
    for s in emp_skills_list:
        if s in req_skill_clean or req_skill_clean in s:
            return 5.0
            
    return 0.0

def calculate_priority_score(emp, task):
    role_match = check_role_match(emp['role'], task['title'], task['description'], task['required_skill'])
    skill_match = check_skill_match(emp['skills'], task['required_skill'])
    perf = float(emp['performance'])
    exp = min(float(emp['experience']), 10.0)
    
    # Priority Score = (Role Match * 40%) + (Skill Match * 30%) + (Performance * 20%) + (Experience * 10%)
    score = (role_match * 0.4) + (skill_match * 0.3) + (perf * 0.2) + (exp * 0.1)
    return round(score, 2)

def get_task_category(task):
    category = None
    if isinstance(task, dict):
        category = task.get('category')
    elif hasattr(task, 'keys') and 'category' in task.keys():
        category = task['category']
        
    if category and category != 'General':
        return category
        
    title = ""
    desc = ""
    skill = ""
    if isinstance(task, dict):
        title = task.get('title', '')
        desc = task.get('description', '') or task.get('desc', '')
        skill = task.get('required_skill', '') or task.get('skill', '')
    elif hasattr(task, 'keys'):
        title = task['title'] if 'title' in task.keys() else ""
        desc = task['description'] if 'description' in task.keys() else ""
        skill = task['required_skill'] if 'required_skill' in task.keys() else ""

    title_lower = title.lower() if title else ""
    desc_lower = desc.lower() if desc else ""
    skill_lower = skill.lower() if skill else ""
    combined = f"{title_lower} {desc_lower} {skill_lower}"
    
    if any(kw in combined for kw in ["backend", "api", "django", "server", "django rest", "python"]):
        return "Backend"
    elif any(kw in combined for kw in ["frontend", "css", "react", "html", "glassmorphism", "widget", "ui", "ux"]):
        return "Frontend"
    elif any(kw in combined for kw in ["database", "sql", "postgres", "query", "dba"]):
        return "Database"
    elif any(kw in combined for kw in ["qa", "test", "selenium", "automation"]):
        return "QA"
    elif any(kw in combined for kw in ["devops", "kubernetes", "docker", "deploy", "eks", "aws"]):
        return "DevOps"
    return "General"

def is_role_match(emp_role, emp_dept, task_category):
    emp_role_lower = (emp_role or "").lower()
    emp_dept_lower = (emp_dept or "").lower()
    task_cat_lower = (task_category or "").lower()
    
    # Check direct role domain keywords first (Primary Match)
    if task_cat_lower == "backend":
        if "backend" in emp_role_lower: return True
    elif task_cat_lower == "frontend":
        if any(kw in emp_role_lower for kw in ["frontend", "ui", "ux", "web developer"]): return True
    elif task_cat_lower in ["database", "db"]:
        if any(kw in emp_role_lower for kw in ["database", "dba", "data engineer"]): return True
    elif task_cat_lower in ["qa", "quality assurance"]:
        if any(kw in emp_role_lower for kw in ["qa", "test", "quality"]): return True
    elif task_cat_lower == "devops":
        if any(kw in emp_role_lower for kw in ["devops", "sre", "infrastructure", "architect"]): return True
    elif task_cat_lower in ["data science", "machine learning", "ml"]:
        if any(kw in emp_role_lower for kw in ["data science", "machine learning", "ml", "specialist"]): return True

    # Conflicting keywords: if task is Backend, a Frontend/QA/Database/DevOps developer does NOT match the role
    conflicting_keywords = {
        "backend": ["frontend", "qa", "test", "devops", "database", "dba"],
        "frontend": ["backend", "qa", "test", "devops", "database", "dba"],
        "database": ["frontend", "backend", "qa", "test", "devops"],
        "qa": ["frontend", "backend", "devops", "database", "dba"],
        "devops": ["frontend", "backend", "qa", "test", "database", "dba"]
    }
    
    if task_cat_lower in conflicting_keywords:
        if any(k in emp_role_lower for k in conflicting_keywords[task_cat_lower]):
            return False
            
    # Department matching fallback only if no role conflict exists
    if task_cat_lower == "backend" and "backend" in emp_dept_lower: return True
    if task_cat_lower == "frontend" and "frontend" in emp_dept_lower: return True
    if task_cat_lower in ["database", "db"] and "database" in emp_dept_lower: return True
    if task_cat_lower in ["qa", "quality assurance"] and ("qa" in emp_dept_lower or "quality" in emp_dept_lower): return True
    if task_cat_lower == "devops" and "devops" in emp_dept_lower: return True

    return False

def get_assignment_key(emp, task):
    try:
        emp_dept = emp['department']
    except Exception:
        emp_dept = None
        
    task_cat = get_task_category(task)
    role_match = 1 if is_role_match(emp['role'], emp_dept, task_cat) else 0
    
    required_skill = ""
    if isinstance(task, dict):
        required_skill = task.get('required_skill') or task.get('skill', '')
    elif hasattr(task, 'keys'):
        if 'required_skill' in task.keys():
            required_skill = task['required_skill']
        elif 'skill' in task.keys():
            required_skill = task['skill']
            
    skills_list = [s.strip().lower() for s in (emp['skills'] or "").split(',') if s.strip()]
    req_skill_clean = (required_skill or "").strip().lower()
    
    if req_skill_clean and req_skill_clean in skills_list:
        skill_match_level = 2  # Exact skill match
    elif check_skill_match(emp['skills'], required_skill) > 0.0:
        skill_match_level = 1  # Similar skill match
    else:
        skill_match_level = 0  # No skill match
        
    perf = float(emp['performance'])
    exp = float(emp['experience'])
    
    db_name = 'database.db'
    if os.path.exists('test_database.db'):
        db_name = 'test_database.db'
    elif os.path.exists('test_performance.db'):
        db_name = 'test_performance.db'
        
    try:
        conn = get_db_connection(db_name)
        c = conn.cursor()
        c.execute("""
        SELECT COUNT(*) FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        WHERE a.employee_id = ? AND t.status != 'Completed'
        """, (emp['id'],))
        workload = c.fetchone()[0]
        conn.close()
    except Exception:
        workload = 0
        
    return (role_match, skill_match_level, perf, exp, -workload)

@app.route('/')
@app.route('/index.html')
def home():
    return render_template("index.html")

@app.route('/app.js')
def serve_root_js():
    return app.send_static_file('app.js')

@app.route('/styles.css')
def serve_root_css():
    return app.send_static_file('styles.css')

@app.route('/run_optimization')
def run_optimization():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all active (non-completed) tasks
    cursor.execute("SELECT * FROM tasks WHERE status != 'Completed'")
    all_tasks = cursor.fetchall()

    pending_tasks = [t for t in all_tasks if t['status'] == 'Pending']
    in_progress_tasks = [t for t in all_tasks if t['status'] == 'In-Progress']

    # Sort tasks by priority: High -> Medium -> Low
    priority_weight = {'High': 3, 'Medium': 2, 'Low': 1}
    pending_tasks.sort(key=lambda t: priority_weight.get(t['priority'], 1), reverse=True)
    in_progress_tasks.sort(key=lambda t: priority_weight.get(t['priority'], 1), reverse=True)

    reallocated_count = 0
    assigned_count = 0

    # 1. Process Pending tasks first
    for task in pending_tasks:
        task_id = task['id']

        # Find available candidates
        cursor.execute("SELECT * FROM employees WHERE availability='Available'")
        available_employees = cursor.fetchall()

        if not available_employees:
            continue

        # Sort available employees using the new tiered matching logic key
        candidate_keys = []
        for emp in available_employees:
            key = get_assignment_key(emp, task)
            candidate_keys.append((emp, key))
            
        candidate_keys.sort(key=lambda x: x[1], reverse=True)
        best_candidate = candidate_keys[0][0]

        # Insert assignment
        cursor.execute("""
        INSERT INTO assignments (employee_id, task_id, assigned_date)
        VALUES (?, ?, date('now'))
        """, (best_candidate['id'], task_id))

        # Mark task status as In-Progress
        cursor.execute("UPDATE tasks SET status='In-Progress' WHERE id=?", (task_id,))

        # Set employee to Busy
        cursor.execute("UPDATE employees SET availability='Busy' WHERE id=?", (best_candidate['id'],))

        # Log Activity
        cursor.execute("SELECT title FROM tasks WHERE id=?", (task_id,))
        task_title = cursor.fetchone()[0]
        log_activity(f"Assigned task '{task_title}' to {best_candidate['name']}.", "assignment")
        assigned_count += 1

    # 2. Reallocate In-Progress tasks if a more suitable employee is found
    for task in in_progress_tasks:
        task_id = task['id']

        # Get current assignee
        cursor.execute("""
        SELECT e.* FROM employees e
        JOIN assignments a ON a.employee_id = e.id
        WHERE a.task_id = ?
        """, (task_id,))
        curr_emp = cursor.fetchone()

        if not curr_emp:
            continue

        curr_key = get_assignment_key(curr_emp, task)

        # Find available candidates
        cursor.execute("SELECT * FROM employees WHERE availability='Available'")
        available_employees = cursor.fetchall()

        if not available_employees:
            continue

        # Sort available employees using the new tiered matching logic key
        candidate_keys = []
        for emp in available_employees:
            key = get_assignment_key(emp, task)
            candidate_keys.append((emp, key))
            
        candidate_keys.sort(key=lambda x: x[1], reverse=True)
        best_avail, best_avail_key = candidate_keys[0]

        # Reallocate if the best available candidate's score is strictly higher than current assignee's score
        if best_avail_key > curr_key:
            cursor.execute("""
            UPDATE assignments
            SET employee_id = ?, assigned_date = date('now')
            WHERE task_id = ?
            """, (best_avail['id'], task_id))

            # Set old employee status to Available
            cursor.execute("UPDATE employees SET availability='Available' WHERE id=?", (curr_emp['id'],))

            # Set new employee status to Busy
            cursor.execute("UPDATE employees SET availability='Busy' WHERE id=?", (best_avail['id'],))

            # Fetch task title
            cursor.execute("SELECT title FROM tasks WHERE id=?", (task_id,))
            task_title = cursor.fetchone()[0]

            # Apply reallocation/failure penalty -1.0 to the previous assignee
            curr_perf = curr_emp['performance']
            new_perf = max(0.0, min(10.0, round(curr_perf - 1.0, 1)))
            cursor.execute("""
            UPDATE employees
            SET performance = ?
            WHERE id = ?
            """, (new_perf, curr_emp['id']))
            
            # Log in performance history
            cursor.execute("""
            INSERT INTO performance_history (employee_id, task_id, old_score, new_score, reason, date)
            VALUES (?, ?, ?, ?, ?, date('now'))
            """, (curr_emp['id'], task_id, curr_perf, new_perf, 'Task reassigned (reallocation penalty)'))

            # Log Reassignment Activity
            log_activity(f"Reassigned task '{task_title}' from {curr_emp['name']} to {best_avail['name']} (dynamic optimization).", "reassignment")
            log_activity(f"Performance decreased from {curr_perf} -> {new_perf} (-1.0 failure penalty) for {curr_emp['name']}.", "reassignment")
            reallocated_count += 1

    conn.commit()
    conn.close()

    if request.args.get('format') == 'json':
        return jsonify({
            "status": "success", 
            "assigned_count": assigned_count,
            "reallocated_count": reallocated_count
        })
    return redirect('/')

def clamp_performance(score):
    try:
        val = float(score)
    except (ValueError, TypeError):
        val = 0.0
    return max(0.0, min(10.0, round(val, 1)))

def process_task_completion(cursor, employee_id, task_id):
    # Fetch task details
    cursor.execute("SELECT title, deadline, priority FROM tasks WHERE id=?", (task_id,))
    task_row = cursor.fetchone()
    if not task_row:
        return
    task_title, deadline, priority = task_row
    
    # Duplicate submission protection: check if performance history already logged for this task & employee
    cursor.execute("SELECT COUNT(*) FROM performance_history WHERE employee_id=? AND task_id=? AND (reason LIKE '%Submit%' OR reason LIKE '%deadline%')", (employee_id, task_id))
    if cursor.fetchone()[0] > 0:
        return
    
    # Calculate base performance change based on deadline
    current_date = datetime.now().strftime('%Y-%m-%d')
    if current_date < deadline:
        perf_change = 0.5
        reason = "Submitted before deadline"
    elif current_date == deadline:
        perf_change = 0.3
        reason = "Submitted exactly on deadline"
    else:
        perf_change = -0.5
        reason = "Submitted after deadline"
        
    # Priority addition
    if priority == "High":
        perf_change += 0.3
        reason += " (High Priority)"
    elif priority == "Medium":
        perf_change += 0.2
        reason += " (Medium Priority)"
    elif priority == "Low":
        perf_change += 0.1
        reason += " (Low Priority)"
        
    # Get current employee performance score
    cursor.execute("SELECT name, performance FROM employees WHERE id=?", (employee_id,))
    emp_row = cursor.fetchone()
    if not emp_row:
        return
    emp_name, curr_perf = emp_row
    
    # Calculate streak count
    # Let's count consecutive successful completions.
    cursor.execute("""
    SELECT t.deadline, s.submission_date FROM assignments a
    JOIN tasks t ON a.task_id = t.id
    JOIN submissions s ON s.assignment_id = t.id
    WHERE a.employee_id = ? AND t.status = 'Completed'
    ORDER BY s.id DESC
    """, (employee_id,))
    completions = cursor.fetchall()
    
    streak = 0
    for dead_val, sub_val in completions:
        sub_date_clean = sub_val.split(' ')[0]
        if sub_date_clean <= dead_val:
            streak += 1
        else:
            break
            
    # Streak bonus
    # If the streak is a multiple of 5, add +1.0
    streak_bonus = 0.0
    if streak > 0 and streak % 5 == 0:
        streak_bonus = 1.0
        reason += f" + Streak Bonus (Streak: {streak})"
        
    final_perf_change = perf_change + streak_bonus
    new_perf = clamp_performance(curr_perf + final_perf_change)
    
    # Update performance and availability
    cursor.execute("""
    UPDATE employees
    SET performance = ?, availability = 'Available'
    WHERE id = ?
    """, (new_perf, employee_id))
    
    # Insert performance history
    cursor.execute("""
    INSERT INTO performance_history (employee_id, task_id, old_score, new_score, reason, date)
    VALUES (?, ?, ?, ?, ?, date('now'))
    """, (employee_id, task_id, curr_perf, new_perf, reason))
    
    # Log multiple activities with accurate event types
    perf_word = "increased" if new_perf >= curr_perf else "decreased"
    log_activity(f"{emp_name} completed task '{task_title}'.", "completion")
    log_activity(f"Performance {perf_word} for {emp_name}: {curr_perf} -> {new_perf} ({reason}).", "performance_update")
    log_activity(f"{emp_name} became Available.", "availability")

@app.route('/submit_work', methods=['POST'])
def submit_work():
    task_id_str = request.form.get('task_id')
    if not task_id_str and request.is_json:
        task_id_str = str(request.json.get('task_id', ''))
        
    if not task_id_str:
        return jsonify({"error": "No task ID provided"}), 400

    task_id = int(str(task_id_str).replace('task-', ''))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check task status to prevent duplicate processing
    cursor.execute("SELECT title, status FROM tasks WHERE id=?", (task_id,))
    t_row = cursor.fetchone()
    if not t_row:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
        
    task_title, current_status = t_row
    if current_status == 'Completed':
        conn.close()
        return jsonify({"status": "already_completed", "message": "Task is already completed"}), 200

    file = request.files.get('file')
    filename = "deliverable_package.zip"
    if file and file.filename:
        filename = file.filename
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Store submission
    cursor.execute("""
    INSERT INTO submissions (assignment_id, file_name, submission_date, status)
    VALUES (?, ?, date('now'), ?)
    """, (task_id, filename, "Approved"))

    # Mark task completed
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))

    # Find assigned employee and log submission + completion
    cursor.execute("SELECT employee_id FROM assignments WHERE task_id=?", (task_id,))
    emp_row = cursor.fetchone()
    if emp_row:
        employee_id = emp_row[0]
        cursor.execute("SELECT name FROM employees WHERE id=?", (employee_id,))
        e_row = cursor.fetchone()
        emp_name = e_row[0] if e_row else "Employee"
        log_activity(f"Submission received for '{task_title}' from {emp_name} ({filename}).", "submission")
        process_task_completion(cursor, employee_id, task_id)

    conn.commit()
    conn.close()

    if request.args.get('format') == 'json' or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success"})
    return redirect('/')

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM tasks WHERE id=?", (task_id,))
    t_row = cursor.fetchone()
    if not t_row:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
        
    if t_row[0] == 'Completed':
        conn.close()
        return jsonify({"status": "already_completed", "message": "Task is already completed"}), 200

    # Insert a dummy submission so that metrics and streaks are consistent
    cursor.execute("""
    INSERT INTO submissions (assignment_id, file_name, submission_date, status)
    VALUES (?, ?, date('now'), ?)
    """, (task_id, 'manual_completion.txt', "Approved"))

    # Update task to Completed
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))

    # Find assigned employee
    cursor.execute("SELECT employee_id FROM assignments WHERE task_id=?", (task_id,))
    emp_row = cursor.fetchone()
    if emp_row:
        employee_id = emp_row[0]
        process_task_completion(cursor, employee_id, task_id)

    conn.commit()
    conn.close()

    if request.args.get('format') == 'json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success"})
    return redirect('/')


@app.route('/api/state')
def get_state():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Fetch Employees
    cursor.execute("SELECT * FROM employees")
    employees_rows = cursor.fetchall()
    employees = []
    for r in employees_rows:
        skills_list = [s.strip() for s in r['skills'].split(',') if s.strip()]
        
        # Count active and completed tasks for this employee
        cursor.execute("""
        SELECT COUNT(*) FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        WHERE a.employee_id = ? AND t.status != 'Completed'
        """, (r['id'],))
        active_count = cursor.fetchone()[0]
        
        cursor.execute("""
        SELECT COUNT(*) FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        WHERE a.employee_id = ? AND t.status = 'Completed'
        """, (r['id'],))
        completed_count = cursor.fetchone()[0]

        # Count failed tasks for this employee
        cursor.execute("""
        SELECT COUNT(*) FROM performance_history
        WHERE employee_id = ? AND (new_score < old_score OR reason LIKE '%reassigned%' OR reason LIKE '%after deadline%')
        """, (r['id'],))
        failed_count = cursor.fetchone()[0]

        # Calculate Average Completion Time in days
        cursor.execute("""
        SELECT a.assigned_date, s.submission_date FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        JOIN submissions s ON s.assignment_id = t.id
        WHERE a.employee_id = ? AND t.status = 'Completed'
        """, (r['id'],))
        dates = cursor.fetchall()
        
        total_days = 0.0
        count = 0
        for assign_date, sub_date in dates:
            try:
                a_dt = datetime.strptime(assign_date.split(' ')[0], '%Y-%m-%d')
                s_dt = datetime.strptime(sub_date.split(' ')[0], '%Y-%m-%d')
                days = (s_dt - a_dt).days
                total_days += max(0.0, float(days))
                count += 1
            except Exception:
                pass
        avg_time = round(total_days / count, 1) if count > 0 else 0.0

        # Get Last Completed Task title
        cursor.execute("""
        SELECT t.title FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        JOIN submissions s ON s.assignment_id = t.id
        WHERE a.employee_id = ? AND t.status = 'Completed'
        ORDER BY s.id DESC
        LIMIT 1
        """, (r['id'],))
        last_completed_row = cursor.fetchone()
        last_completed = last_completed_row[0] if last_completed_row else "None"

        # Calculate success rate (completed on-time tasks vs total completed tasks)
        cursor.execute("""
        SELECT t.deadline, s.submission_date FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        JOIN submissions s ON s.assignment_id = t.id
        WHERE a.employee_id = ? AND t.status = 'Completed'
        """, (r['id'],))
        subs = cursor.fetchall()
        
        on_time_count = 0
        total_subs = len(subs)
        for sub in subs:
            deadline = sub[0]
            sub_date = sub[1].split(' ')[0] # Extract just YYYY-MM-DD
            if sub_date <= deadline:
                on_time_count += 1
                
        success_rate = 100
        if total_subs > 0:
            success_rate = int((on_time_count / total_subs) * 100)
            
        # Get current assigned task title
        cursor.execute("""
        SELECT t.title FROM assignments a
        JOIN tasks t ON a.task_id = t.id
        WHERE a.employee_id = ? AND t.status != 'Completed'
        LIMIT 1
        """, (r['id'],))
        curr_task_row = cursor.fetchone()
        curr_task_title = curr_task_row[0] if curr_task_row else "None"

        employees.append({
            'id': f"emp-{r['id']}",
            'name': r['name'],
            'role': r['role'],
            'department': r['department'] if r['department'] else 'Engineering',
            'score': r['performance'],
            'experience': r['experience'],
            'skills': skills_list,
            'availability': r['availability'],
            'avatar_url': r['avatar_url'] if r['avatar_url'] else "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150&q=80",
            'online_status': r['online_status'] if r['online_status'] else 'Online',
            'active_tasks': active_count,
            'completed_tasks': completed_count,
            'failed_tasks': failed_count,
            'success_rate': success_rate,
            'avg_completion_time': avg_time,
            'last_completed_task': last_completed,
            'current_task': curr_task_title
        })

    # 2. Fetch Tasks
    cursor.execute("SELECT * FROM tasks")
    tasks_rows = cursor.fetchall()
    tasks = []
    for r in tasks_rows:
        tasks.append({
            'id': f"task-{r['id']}",
            'title': r['title'],
            'desc': r['description'],
            'priority': r['priority'],
            'skill': r['required_skill'],
            'deadline': r['deadline'],
            'status': r['status'],
            'category': r['category'] if r['category'] else 'General'
        })

    # 3. Fetch Assignments (Only active ones)
    cursor.execute("""
    SELECT a.employee_id, a.task_id, a.assigned_date
    FROM assignments a
    JOIN tasks t ON a.task_id = t.id
    WHERE t.status != 'Completed'
    """)
    assignments_rows = cursor.fetchall()
    assignments = []
    for r in assignments_rows:
        assignments.append({
            'employeeId': f"emp-{r['employee_id']}",
            'taskId': f"task-{r['task_id']}",
            'assignedDate': r['assigned_date']
        })

    # 4. Fetch Submissions
    cursor.execute("""
    SELECT s.id, t.title, e.name, s.file_name, s.submission_date, s.status
    FROM submissions s
    JOIN tasks t ON s.assignment_id = t.id
    LEFT JOIN assignments a ON a.task_id = t.id
    LEFT JOIN employees e ON a.employee_id = e.id
    ORDER BY s.id DESC
    """)
    submissions_rows = cursor.fetchall()
    submissions = []
    for r in submissions_rows:
        submissions.append({
            'id': f"sub-{r['id']}",
            'taskTitle': r['title'],
            'employeeName': r['name'] if r['name'] else "Kyle Reese",
            'fileName': r['file_name'],
            'date': r['submission_date'],
            'status': r['status']
        })

    # 5. Fetch Activity Logs (recent 30 items)
    cursor.execute("SELECT * FROM activity_log ORDER BY id DESC LIMIT 30")
    activities_rows = cursor.fetchall()
    activities = []
    for r in activities_rows:
        activities.append({
            'id': r['id'],
            'message': r['message'],
            'timestamp': r['timestamp'],
            'type': r['type']
        })

    # 6. Fetch Performance History
    cursor.execute("""
    SELECT ph.id, ph.employee_id, e.name as employee_name, ph.task_id, ph.old_score, ph.new_score, ph.reason, ph.date
    FROM performance_history ph
    LEFT JOIN employees e ON ph.employee_id = e.id
    ORDER BY ph.id ASC
    """)
    perf_history_rows = cursor.fetchall()
    performance_history = []
    for r in perf_history_rows:
        performance_history.append({
            'id': r['id'],
            'employeeId': f"emp-{r['employee_id']}",
            'employeeName': r['employee_name'] if r['employee_name'] else "Employee",
            'taskId': f"task-{r['task_id']}" if r['task_id'] else None,
            'oldScore': r['old_score'],
            'newScore': r['new_score'],
            'reason': r['reason'],
            'date': r['date']
        })

    conn.close()

    return jsonify({
        'employees': employees,
        'tasks': tasks,
        'assignments': assignments,
        'submissions': submissions,
        'activities': activities,
        'performance_history': performance_history,
        'theme': 'dark'
    })

@app.route('/api/add_employee', methods=['POST'])
def add_employee():
    data = request.json
    name = data['name']
    role = data['role']
    department = data.get('department', 'Engineering')
    performance = max(0.0, min(10.0, float(data['score'])))
    experience = data['experience']
    skills = ", ".join(data['skills'])
    
    # Optional defaults
    avatar_url = data.get('avatar_url')
    if not avatar_url:
        avatars = [
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&h=150&q=80",
            "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=150&h=150&q=80",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&h=150&q=80",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&h=150&q=80",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=150&h=150&q=80",
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&h=150&q=80"
        ]
        avatar_url = avatars[len(name) % len(avatars)]
    online_status = data.get('online_status', 'Online')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO employees (name, role, department, skills, performance, experience, availability, avatar_url, online_status)
    VALUES (?, ?, ?, ?, ?, ?, 'Available', ?, ?)
    """, (name, role, department, skills, performance, experience, avatar_url, online_status))
    conn.commit()
    conn.close()

    log_activity(f"Added new team member: {name} ({role}) to {department}.", "employee_added")
    return jsonify({"status": "success"})

@app.route('/api/add_task', methods=['POST'])
def add_task():
    data = request.json
    title = data['title']
    description = data['desc']
    priority = data['priority']
    deadline = data['deadline']
    required_skill = data['skill']
    category = data.get('category')
    
    if not category:
        # Determine category automatically
        t_low = title.lower()
        d_low = description.lower()
        if any(kw in t_low or kw in d_low for kw in ["backend", "api", "django", "server"]):
            category = "Backend"
        elif any(kw in t_low or kw in d_low for kw in ["frontend", "css", "react", "html", "glassmorphism", "widget"]):
            category = "Frontend"
        elif any(kw in t_low or kw in d_low for kw in ["database", "sql", "postgres", "query"]):
            category = "Database"
        elif any(kw in t_low or kw in d_low for kw in ["qa", "test", "selenium"]):
            category = "QA"
        elif any(kw in t_low or kw in d_low for kw in ["devops", "kubernetes", "docker", "deploy"]):
            category = "DevOps"
        else:
            category = "General"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tasks (title, description, required_skill, priority, deadline, status, category)
    VALUES (?, ?, ?, ?, ?, 'Pending', ?)
    """, (title, description, required_skill, priority, deadline, category))
    conn.commit()
    conn.close()

    log_activity(f"Created new task: '{title}' under category {category}.", "task_created")
    return jsonify({"status": "success"})

@app.route('/api/reset_data', methods=['POST'])
def reset_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    seed_db_data(cursor)
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/backup_db')
def backup_db():
    from flask import send_file
    if os.path.exists('database.db'):
        return send_file('database.db', as_attachment=True, download_name='database_backup.db')
    return jsonify({"error": "Database not found"}), 404

@app.route('/api/export/<table_name>')
def export_csv(table_name):
    allowed_tables = ['employees', 'tasks', 'assignments', 'submissions', 'activity_log']
    if table_name not in allowed_tables:
        return jsonify({"error": "Invalid table name"}), 400
        
    import csv
    import io
    from flask import Response
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Get column headers
    cursor.execute(f"PRAGMA table_info({table_name})")
    headers = [col[1] for col in cursor.fetchall()]
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = f"attachment; filename={table_name}.csv"
    return response

@app.route('/api/import_employees', methods=['POST'])
def import_employees():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Please upload a CSV file"}), 400
        
    import csv
    import io
    
    csv_data = file.stream.read().decode("utf-8")
    stream = io.StringIO(csv_data)
    reader = csv.DictReader(stream)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    import_count = 0
    for row in reader:
        name = row.get('name')
        role = row.get('role', 'Developer')
        department = row.get('department', 'Engineering')
        skills = row.get('skills', '')
        performance = max(0.0, min(10.0, float(row.get('performance', 8.0))))
        experience = int(row.get('experience', 3))
        availability = row.get('availability', 'Available')
        avatar_url = row.get('avatar_url', '')
        online_status = row.get('online_status', 'Online')
        
        if not name:
            continue
            
        cursor.execute("""
        INSERT INTO employees (name, role, department, skills, performance, experience, availability, avatar_url, online_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, role, department, skills, performance, experience, availability, avatar_url, online_status))
        import_count += 1
        
    conn.commit()
    conn.close()
    
    log_activity(f"Imported {import_count} employees from CSV document.", "system")
    return jsonify({"status": "success", "count": import_count})

@app.route('/check_assignments')
def check_assignments():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assignments")
    data = cursor.fetchall()
    conn.close()
    return str(data)

@app.route('/check_employees')
def check_employees():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, performance FROM employees")
    data = cursor.fetchall()
    conn.close()
    return str(data)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)