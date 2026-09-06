# OptimaAssign ⚡
### Performance-Aware Workforce Optimization & Task Assignment System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.org/)
[![SQLite](https://img.shields.io/badge/SQLite3-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-Analytics-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.style=for-the-badge)](LICENSE)

**OptimaAssign** is an enterprise-grade workforce management and task optimization platform. It utilizes a **Tiered Greedy Allocation Engine** to evaluate team members based on domain role alignment, technical skill matching, performance capability, experience, and current workload.

---

## 📌 Executive Summary & Problem Statement

### The Problem
Traditional workforce management systems allocate jobs naively based on highest individual rating or seniority alone. This leads to critical operational flaws:
- **Role Misallocation**: A Backend task is assigned to a Frontend engineer simply because the Frontend engineer holds a slightly higher performance score.
- **Overloading High Performers**: The highest-rated employee is assigned all incoming tasks regardless of their current active workload.
- **Unbounded Metrics**: Performance scores fluctuate unnaturally above 10.0 or below 0.0 without strict mathematical bounds or streak compensation.

### The OptimaAssign Solution
OptimaAssign solves these challenges with a multi-layered allocation model:
1. **Role Matching Priority**: Direct domain role matching takes precedence over raw score.
2. **Dynamic Reallocation Engine**: Automatically re-evaluates active tasks when matching role candidates become available.
3. **Clamped Performance Scoring**: Performance ratings remain strictly within `[0.0, 10.0]` with automated streak bonuses and deadline tracking.
4. **Real-time Analytics Hub**: Visualizes workload distribution, performance history, status alignment, and efficiency trends.

---

## 🧠 Core Systems & Algorithms

### 1. Tiered Greedy Allocation Algorithm
When tasks are created or optimized, candidate employees are evaluated using a 5-element tuple comparison key:

$$\text{Sort Key} = \left(\text{RoleMatch}, \text{SkillMatchLevel}, \text{PerformanceScore}, \text{Experience}, -\text{ActiveWorkload}\right)$$

| Priority Tier | Criteria | Value Range / Logic |
| :--- | :--- | :--- |
| **Tier 1 (Highest)** | **Domain Role Match** | `1` if candidate role matches task domain (Backend, Frontend, DevOps, QA, Database, Data Science); `0` if conflicting. |
| **Tier 2** | **Technical Skill Match** | `2` for Exact Match; `1` for Similar/Related Skill; `0` for No Match. |
| **Tier 3** | **Performance Capability** | Clamped score from `0.0` to `10.0`. |
| **Tier 4** | **Years of Experience** | Numerical experience (used as tie-breaker when scores are equal). |
| **Tier 5 (Lowest)** | **Active Workload** | $-\text{Active Tasks Count}$ (prefers employees with lighter workloads). |

```python
def get_assignment_key(emp, task):
    role_match = 1 if is_role_match(emp['role'], emp['department'], get_task_category(task)) else 0
    skill_match_level = get_skill_match_level(emp['skills'], task['required_skill'])
    perf = float(emp['performance'])
    exp = float(emp['experience'])
    workload = get_active_workload(emp['id'])
    
    return (role_match, skill_match_level, perf, exp, -workload)
```

---

### 2. Clamped Performance Rating System
Performance ratings are bounded within `[0.0, 10.0]`:

$$\text{Score}_{\text{new}} = \max\left(0.0, \min\left(10.0, \text{Score}_{\text{current}} + \Delta_{\text{deadline}} + \Delta_{\text{priority}} + \Delta_{\text{streak}}\right)\right)$$

- **Early Submission**: $+0.5$ base increase
- **On-Time Submission**: $+0.3$ base increase
- **Late Submission**: $-0.5$ penalty
- **Priority Multiplier**: High Priority ($+0.3$), Medium ($+0.2$), Low ($+0.1$)
- **Streak Bonus**: $+1.0$ additional score bonus for every 5 consecutive on-time completions.
- **Reallocation Penalty**: $-1.0$ penalty applied if a task is reassigned away from an employee due to non-availability or poor role fit.

---

### 3. Dynamic Reallocation Workflow
1. When an employee completes a task, their status becomes `Available`.
2. The system evaluates all active `In-Progress` tasks.
3. If an `Available` employee has a strictly higher allocation key than the current assignee, the task is dynamically reassigned.
4. Completed tasks are permanently locked and **never** reassigned.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, Flask Web Framework, SQLite3 Database Engine
- **Frontend**: HTML5, Vanilla CSS3 (Custom Dark Neutral Design System), JavaScript (ES6+)
- **Data Visualization**: Chart.js 4.x (Line, Bar, Doughnut, Polar Area, Scatter Charts)
- **Icons & Typography**: Font Awesome 6.4, Google Fonts (*Plus Jakarta Sans*, *Inter*, *Outfit*)

---

## 📊 Analytics Dashboard & Reporting

OptimaAssign features **13 Real-time Analytics Indicators**:

1. **Average Workforce Performance**
2. **Top Performing Employee Summary**
3. **Most Active Employee Metrics**
4. **Available vs Busy Workforce Count**
5. **Completed Tasks Total**
6. **Pending Tasks Queue**
7. **Task Delivery Success Rate (%)**
8. **Workload Distribution** (*Bar Chart*)
9. **Employee Performance History** (*Line Chart*)
10. **Performance vs Experience Correlation** (*Scatter Chart*)
11. **Task Status Distribution** (*Doughnut Chart*)
12. **Task Priority Breakdown** (*Polar Area Chart*)
13. **Cumulative Completion Trend** (*Line Chart*)

---

## 🔍 Search, Multi-Criteria Filtering & Sorting

- **Global Search Bar**: Instant real-time filtering across Employee Name, Role, Skill, Task Title, Required Skill, Priority, and Status.
- **Employee Filters**: Availability (`Available`/`Busy`), Domain Role, Technical Skill, Performance Range (`High`/`Good`/`Moderate`), Experience Level (`Senior`/`Mid`/`Junior`).
- **Task Filters**: Status (`Pending`/`In-Progress`/`Completed`), Priority, Required Skill, Deadline (`Upcoming`/`Overdue`).
- **Sorting Engine**: Multi-field client-side sorting by Performance Rating, Experience Years, Active Tasks, Completed Tasks, Success Rate, Deadline Date, or Priority Order.

---

## 📂 Project Directory Structure

```
OptimaAssign/
│
├── app.py                      # Flask REST Application & Greedy Optimization Engine
├── database.db                 # SQLite Database Store
├── requirements.txt            # Python Dependencies
├── README.md                   # Project Documentation
├── .gitignore                  # Git Exclusion Rules
│
├── templates/
│   └── index.html              # Single Page Application Dashboard Shell
│
├── static/
│   ├── app.js                  # Frontend Application Logic & Chart Render Engine
│   └── styles.css              # Custom SaaS Dark Neutral CSS Design System
│
├── uploads/                    # Task Deliverable Storage
│   └── .gitkeep
│
└── scratch/                    # Test Verification Scripts
    ├── test_6_cases.py         # Verification Suite for Greedy Assignment & Reallocation
    ├── test_performance_management.py # Verification Suite for Clamped Scores & Streaks
    └── verify_analytics_system.py     # Verification Suite for Analytics Metrics & DB
```

---

## ⚙️ Installation & Running Locally

### Prerequisites
- Python 3.9 or higher installed
- Pip package manager

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/OptimaAssign.git
   cd OptimaAssign
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application**
   ```bash
   python app.py
   ```

5. **Access Dashboard**
   Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📡 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Renders main Single Page Application interface. |
| `/api/state` | `GET` | Returns JSON representation of employees, tasks, assignments, submissions, activities, and score logs. |
| `/run_optimization` | `GET` | Triggers the Tiered Greedy Optimization Algorithm and dynamic reallocation. |
| `/submit_work` | `POST` | Processes task deliverable submissions, marks tasks completed, and updates performance ratings. |
| `/api/add_employee` | `POST` | Registers a new workforce member. |
| `/api/add_task` | `POST` | Enqueues a new work task into the system. |
| `/api/reset_data` | `POST` | Resets SQLite tables to demo state. |

---

## 🧪 Verification & Testing

Run the included automated backend test suites:

```bash
# Test Greedy Allocation & Dynamic Reallocation Logic (6 Test Cases)
python scratch/test_6_cases.py

# Test Clamped Performance Rating Math [0.0, 10.0] & Streaks
python scratch/test_performance_management.py

# Test Analytics Engine & Database Query Layer
python scratch/verify_analytics_system.py
```

---

## 🚀 Future Scope & System Limitations

- **Multi-Tenant Authentication**: Role-based Access Control (RBAC) for Admin, Manager, and Employee portals.
- **Machine Learning Capability Prediction**: Predict completion time using historical assignment logs.
- **WebSockets Real-time Sync**: Upgrade HTTP polling to Socket.IO for multi-user live collaborative updates.

---

## 👨‍💻 Author

**Rajan Kumar Singh**

B.Tech Computer Science and Engineering  
RV College of Engineering, Bengaluru

GitHub: [@rajankumarsinghcy24-creator](https://github.com/rajankumarsinghcy24-creator)
