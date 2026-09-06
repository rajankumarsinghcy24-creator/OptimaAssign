with open('scratch/backups/app.py', 'r', encoding='utf-8') as f:
    back_py = f.read()

def print_snippet(py, search, length=1500):
    pos = py.find(search)
    if pos != -1:
        print(py[pos:pos+length])

print("=== BACKUP submit_work ROUTE ===")
print_snippet(back_py, "def submit_work")

