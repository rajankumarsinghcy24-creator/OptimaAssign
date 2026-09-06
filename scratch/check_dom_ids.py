import re

with open('static/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

matches = re.findall(r'document\.getElementById\([\'\"](.*?)[\'\"]\)', code)
print('Total getElementById calls:', len(matches))

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_ids = set(re.findall(r'id=[\'\"](.*?)[\'\"]', html))

missing = []
for el_id in sorted(set(matches)):
    if el_id not in html_ids:
        missing.append(el_id)

print('Referenced IDs missing from index.html:', missing)
