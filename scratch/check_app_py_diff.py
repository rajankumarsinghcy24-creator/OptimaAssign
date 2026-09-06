import difflib

with open('app.py', 'r', encoding='utf-8') as f1, open('scratch/backups/app.py', 'r', encoding='utf-8') as f2:
    curr_lines = f1.readlines()
    back_lines = f2.readlines()

diff = list(difflib.unified_diff(back_lines, curr_lines, fromfile='scratch/backups/app.py', tofile='app.py'))

print(f"Total diff lines in app.py: {len(diff)}")
for line in diff:
    if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
        print(line.strip())
    elif line.startswith('+') or line.startswith('-'):
        # Print function/route definitions or changes in SQL/logic
        if 'def ' in line or '@app.route' in line or 'SELECT' in line or 'UPDATE' in line or 'INSERT' in line or 'DELETE' in line or 'return' in line:
            print("  ", line.strip()[:100])

