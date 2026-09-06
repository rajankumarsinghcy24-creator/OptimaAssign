import sqlite3
import os
from datetime import datetime

def test_submit(task_id):
    filename = "test_file.zip"
    perf_change = 0.5
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    current_date = datetime.now().strftime('%Y-%m-%d')
    # Check task deadline
    cursor.execute("SELECT deadline FROM tasks WHERE id=?", (task_id,))
    deadline_row = cursor.fetchone()
    if deadline_row:
        deadline = deadline_row[0]
        if current_date > deadline:
            perf_change = -0.5

    print(f"Task ID: {task_id}, Deadline: {deadline_row[0] if deadline_row else 'None'}, Current Date: {current_date}, Perf Change: {perf_change}")

    # Mark task completed
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))

    # Find assigned employee
    cursor.execute("SELECT employee_id FROM assignments WHERE task_id=?", (task_id,))
    emp_row = cursor.fetchone()
    print(f"Assigned Employee Row: {emp_row}")
    if emp_row:
        employee_id = emp_row[0]

        # Adjust performance score & free employee
        cursor.execute("SELECT performance, availability FROM employees WHERE id=?", (employee_id,))
        perf_row = cursor.fetchone()
        print(f"Before Update - Performance: {perf_row[0]}, Availability: {perf_row[1]}")
        if perf_row:
            curr_perf = perf_row[0]
            new_perf = max(0.0, min(10.0, curr_perf + perf_change))
            cursor.execute("""
            UPDATE employees
            SET performance = ?, availability = 'Available'
            WHERE id = ?
            """, (new_perf, employee_id))
        # Verify in DB
        cursor.execute("SELECT performance, availability FROM employees WHERE id=?", (employee_id,))
        perf_row_after = cursor.fetchone()
        print(f"Verified in DB - Performance: {perf_row_after[0]}, Availability: {perf_row_after[1]}")
        
    conn.commit()
    
    # Verify task status
    cursor.execute("SELECT status FROM tasks WHERE id=?", (task_id,))
    task_status = cursor.fetchone()
    print(f"Verified Task Status: {task_status[0]}")
    
    conn.close()

if __name__ == '__main__':
    test_submit(2)
