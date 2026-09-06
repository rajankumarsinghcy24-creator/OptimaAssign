import re

with open('static/app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

with open('scratch/backups/index.html', 'r', encoding='utf-8') as f:
    back_html = f.read()

with open('scratch/backups/app.js', 'r', encoding='utf-8') as f:
    back_js = f.read()

print("=== SEARCH FOR leaderboardList IN JS & HTML ===")
for i, line in enumerate(js_content.splitlines()):
    if 'leaderboardList' in line:
        print(f"JS Line {i+1}: {line}")

print("\nIs leaderboardList in Backup HTML?", 'leaderboardList' in back_html)
print("Is leaderboardList in Current HTML?", 'leaderboardList' in html_content)

print("\n=== ALL getElementById CALLS IN JS THAT MAY MISS IN HTML ===")
js_ids = set(re.findall(r"document\.getElementById\(['\"](.*?)['\"]\)", js_content))
html_ids = set(re.findall(r"id=['\"](.*?)['\"]", html_content))

for el_id in sorted(js_ids):
    if el_id not in html_ids:
        print(f"Missing ID: {el_id}")
        # print context lines in JS
        for i, line in enumerate(js_content.splitlines()):
            if el_id in line:
                print(f"   Line {i+1}: {line}")

