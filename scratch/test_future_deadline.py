import sqlite3
from datetime import datetime

def test():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Reset employee 4 performance to 8.0 and status to Busy
    c.execute("UPDATE employees SET performance=8.0, availability='Busy' WHERE id=4")
    # Reset task 2 status to In-Progress and set deadline to a future date
    c.execute("UPDATE tasks SET status='In-Progress', deadline='2026-07-20' WHERE id=2")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    test()
