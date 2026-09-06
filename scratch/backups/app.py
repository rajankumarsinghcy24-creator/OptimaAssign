from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Create Employees Table with availability column
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        skills TEXT,
        performance REAL,
        experience INTEGER,
        availability TEXT DEFAULT 'Available'
    )
    """)

    # Create Tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        required_skill TEXT,
        priority TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'Pending'
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

    conn.commit()

    # Seed with initial mockup data if employees table is empty
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        employees = [
            (1, 'Sarah Connor', 'Lead DevOps Architect', 'Docker, AWS, Kubernetes, Python', 9.6, 8, 'Busy'),
            (2, 'Marcus Wright', 'Senior Backend Engineer', 'Python, SQL, Django, API', 8.8, 6, 'Busy'),
            (3, 'Kyle Reese', 'Frontend Developer', 'JavaScript, CSS, React, HTML', 8.2, 4, 'Available'),
            (4, 'John Connor', 'Machine Learning Specialist', 'Python, PyTorch, SQL, Math', 9.4, 5, 'Available'),
            (5, 'Kate Brewster', 'QA Automation Engineer', 'Python, Selenium, CSS, JavaScript', 7.9, 3, 'Available'),
            (6, 'Grace Harper', 'Database Administrator', 'SQL, Postgres, AWS, Optimization', 8.5, 7, 'Available')
        ]
        cursor.executemany("""
        INSERT INTO employees (id, name, role, skills, performance, experience, availability)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, employees)

        tasks = [
            (1, 'Deploy Kubernetes Cluster', 'Set up multi-region high-availability EKS cluster for staging environment.', 'Kubernetes', 'High', '2026-06-15', 'In-Progress'),
            (2, 'Optimize SQL Query Performance', 'Profile and index main reporting tables to reduce load time under 200ms.', 'SQL', 'High', '2026-06-12', 'Pending'),
            (3, 'Implement CSS Glassmorphism UI', 'Create a modern, clean visual look with blurred backdrops and custom scrollbars.', 'CSS', 'Medium', '2026-06-18', 'Pending'),
            (4, 'Refactor Django Authentication Rest API', 'Migrate old session endpoints to secure JWT and OAuth2 integration.', 'API', 'High', '2026-06-10', 'In-Progress'),
            (5, 'Build React Dashboard Widgets', 'Implement interactive SVG charts for the executive operations board.', 'React', 'Medium', '2026-06-20', 'Completed'),
            (6, 'Configure Selenium Smoke Tests', 'Automate user checkout flow verification on mobile and desktop viewports.', 'Selenium', 'Low', '2026-06-25', 'Pending')
        ]
        cursor.executemany("""
        INSERT INTO tasks (id, title, description, required_skill, priority, deadline, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tasks)

        assignments = [
            (1, 1, 1, '2026-06-05'),
            (2, 2, 4, '2026-06-04')
        ]
        cursor.executemany("""
        INSERT INTO assignments (id, employee_id, task_id, assigned_date)
        VALUES (?, ?, ?, ?)
        """, assignments)

        submissions = [
            (1, 5, 'dashboard-widgets-react.zip', '2026-06-06 14:30', 'Approved')
        ]
        cursor.executemany("""
        INSERT INTO submissions (id, assignment_id, file_name, submission_date, status)
        VALUES (?, ?, ?, ?, ?)
        """, submissions)

        conn.commit()

    conn.close()

# Run table creations and seed mockups on application setup
init_db()

def calculate_priority_score(emp_performance, emp_experience, emp_skills, task_skill):
    # Match skills case-insensitively
    emp_skills_list = [s.strip().lower() for s in emp_skills.split(',') if s.strip()]
    task_skill_clean = task_skill.strip().lower()
    
    skill_match = 10.0 if task_skill_clean in emp_skills_list else 0.0
    
    score = (emp_performance * 0.6) + (emp_experience * 0.2) + (skill_match * 0.2)
    return score

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/run_optimization')
def run_optimization():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all active (non-completed) tasks
    cursor.execute("SELECT * FROM tasks WHERE status != 'Completed'")
    all_tasks = cursor.fetchall()

    pending_tasks = [t for t in all_tasks if t['status'] == 'Pending']
    in_progress_tasks = [t for t in all_tasks if t['status'] == 'In-Progress']

    # Sort tasks by priority weight: High -> Medium -> Low
    priority_weight = {'High': 3, 'Medium': 2, 'Low': 1}
    pending_tasks.sort(key=lambda t: priority_weight.get(t['priority'], 1), reverse=True)
    in_progress_tasks.sort(key=lambda t: priority_weight.get(t['priority'], 1), reverse=True)

    # 1. Process Pending tasks first
    for task in pending_tasks:
        task_id = task['id']
        required_skill = task['required_skill']

        # Find available candidates
        cursor.execute("SELECT * FROM employees WHERE availability='Available'")
        available_employees = cursor.fetchall()

        if not available_employees:
            continue

        candidates = []
        for emp in available_employees:
            score = calculate_priority_score(emp['performance'], emp['experience'], emp['skills'], required_skill)
            candidates.append({
                'id': emp['id'],
                'performance': emp['performance'],
                'priority_score': score
            })

        # Choose best candidate (Priority Score desc, tie-breaker: Performance Score desc)
        candidates.sort(key=lambda x: (x['priority_score'], x['performance']), reverse=True)
        best_candidate = candidates[0]

        # Insert assignment
        cursor.execute("""
        INSERT INTO assignments (employee_id, task_id, assigned_date)
        VALUES (?, ?, date('now'))
        """, (best_candidate['id'], task_id))

        # Mark task status as In-Progress (Assigned)
        cursor.execute("UPDATE tasks SET status='In-Progress' WHERE id=?", (task_id,))

        # Set employee to Busy
        cursor.execute("UPDATE employees SET availability='Busy' WHERE id=?", (best_candidate['id'],))

    # 2. Reallocate In-Progress tasks if a better available employee is found
    for task in in_progress_tasks:
        task_id = task['id']
        required_skill = task['required_skill']

        # Get current assignee
        cursor.execute("""
        SELECT e.* FROM employees e
        JOIN assignments a ON a.employee_id = e.id
        WHERE a.task_id = ?
        """, (task_id,))
        curr_emp = cursor.fetchone()

        if not curr_emp:
            continue

        curr_score = calculate_priority_score(curr_emp['performance'], curr_emp['experience'], curr_emp['skills'], required_skill)

        # Find available candidates
        cursor.execute("SELECT * FROM employees WHERE availability='Available'")
        available_employees = cursor.fetchall()

        if not available_employees:
            continue

        candidates = []
        for emp in available_employees:
            score = calculate_priority_score(emp['performance'], emp['experience'], emp['skills'], required_skill)
            candidates.append({
                'id': emp['id'],
                'performance': emp['performance'],
                'priority_score': score
            })

        # Choose best candidate among available employees
        candidates.sort(key=lambda x: (x['priority_score'], x['performance']), reverse=True)
        best_avail = candidates[0]

        # Reallocate if the best available candidate's score is strictly higher than current assignee's score
        if best_avail['priority_score'] > curr_score:
            cursor.execute("""
            UPDATE assignments
            SET employee_id = ?, assigned_date = date('now')
            WHERE task_id = ?
            """, (best_avail['id'], task_id))

            # Set old employee status to Available
            cursor.execute("UPDATE employees SET availability='Available' WHERE id=?", (curr_emp['id'],))

            # Set new employee status to Busy
            cursor.execute("UPDATE employees SET availability='Busy' WHERE id=?", (best_avail['id'],))

    conn.commit()
    conn.close()

    if request.args.get('format') == 'json':
        return jsonify({"status": "success"})
    return redirect('/')

@app.route('/submit_work', methods=['POST'])
def submit_work():
    task_id_str = request.form.get('task_id')
    if not task_id_str:
        return jsonify({"error": "No task ID provided"}), 400

    task_id = int(task_id_str.replace('task-', ''))
    file = request.files.get('file')

    if file:
        filename = file.filename
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check task deadline (compare YYYY-MM-DD strings lexicographically)
        cursor.execute("SELECT deadline FROM tasks WHERE id=?", (task_id,))
        deadline_row = cursor.fetchone()
        perf_change = 0.5
        if deadline_row:
            deadline = deadline_row[0]
            current_date = datetime.now().strftime('%Y-%m-%d')
            if current_date > deadline:
                perf_change = -0.5

        # Store submission
        cursor.execute("""
        INSERT INTO submissions (assignment_id, file_name, submission_date, status)
        VALUES (?, ?, date('now'), ?)
        """, (task_id, filename, "Submitted"))

        # Mark task completed
        cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))

        # Find assigned employee
        cursor.execute("SELECT employee_id FROM assignments WHERE task_id=?", (task_id,))
        emp_row = cursor.fetchone()
        if emp_row:
            employee_id = emp_row[0]

            # Adjust performance score & free employee (set status to Available)
            cursor.execute("SELECT performance FROM employees WHERE id=?", (employee_id,))
            perf_row = cursor.fetchone()
            if perf_row:
                curr_perf = perf_row[0]
                new_perf = max(0.0, min(10.0, round(curr_perf + perf_change, 1)))
                cursor.execute("""
                UPDATE employees
                SET performance = ?, availability = 'Available'
                WHERE id = ?
                """, (new_perf, employee_id))

        conn.commit()
        conn.close()

    if request.args.get('format') == 'json':
        return jsonify({"status": "success"})
    return redirect('/')

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check task deadline
    cursor.execute("SELECT deadline FROM tasks WHERE id=?", (task_id,))
    deadline_row = cursor.fetchone()
    perf_change = 0.5
    if deadline_row:
        deadline = deadline_row[0]
        current_date = datetime.now().strftime('%Y-%m-%d')
        if current_date > deadline:
            perf_change = -0.5

    # Update task to Completed
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))

    # Find assigned employee
    cursor.execute("SELECT employee_id FROM assignments WHERE task_id=?", (task_id,))
    emp_row = cursor.fetchone()
    if emp_row:
        employee_id = emp_row[0]

        # Adjust performance score & set status to Available
        cursor.execute("SELECT performance FROM employees WHERE id=?", (employee_id,))
        perf_row = cursor.fetchone()
        if perf_row:
            curr_perf = perf_row[0]
            new_perf = max(0.0, min(10.0, round(curr_perf + perf_change, 1)))
            cursor.execute("""
            UPDATE employees
            SET performance = ?, availability = 'Available'
            WHERE id = ?
            """, (new_perf, employee_id))

    conn.commit()
    conn.close()

    if request.args.get('format') == 'json':
        return jsonify({"status": "success"})
    return redirect('/')

@app.route('/api/state')
def get_state():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Fetch Employees
    cursor.execute("SELECT * FROM employees")
    employees_rows = cursor.fetchall()
    employees = []
    for r in employees_rows:
        skills_list = [s.strip() for s in r['skills'].split(',') if s.strip()]
        employees.append({
            'id': f"emp-{r['id']}",
            'name': r['name'],
            'role': r['role'],
            'score': r['performance'],
            'experience': r['experience'],
            'skills': skills_list,
            'availability': r['availability']
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
            'status': r['status']
        })

    # 3. Fetch Assignments (Only active ones - task status is not Completed)
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

    # 4. Fetch Submissions (Join with tasks and assignments to match employee names)
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
            'employeeName': r['name'] if r['name'] else "Kyle Reese", # Kyle Reese is seeded for task 5
            'fileName': r['file_name'],
            'date': r['submission_date'],
            'status': r['status']
        })

    conn.close()

    return jsonify({
        'employees': employees,
        'tasks': tasks,
        'assignments': assignments,
        'submissions': submissions,
        'theme': 'dark'
    })

@app.route('/api/add_employee', methods=['POST'])
def add_employee():
    data = request.json
    name = data['name']
    role = data['role']
    performance = data['score']
    experience = data['experience']
    skills = ", ".join(data['skills'])

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO employees (name, role, skills, performance, experience, availability)
    VALUES (?, ?, ?, ?, ?, 'Available')
    """, (name, role, skills, performance, experience))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/api/add_task', methods=['POST'])
def add_task():
    data = request.json
    title = data['title']
    description = data['desc']
    priority = data['priority']
    deadline = data['deadline']
    required_skill = data['skill']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tasks (title, description, required_skill, priority, deadline, status)
    VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (title, description, required_skill, priority, deadline))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

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