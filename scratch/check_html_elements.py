with open('templates/index.html', 'r', encoding='utf-8') as f:
    curr_html = f.read()

with open('scratch/backups/index.html', 'r', encoding='utf-8') as f:
    back_html = f.read()

def print_section(html, title, search_str, length=1500):
    print(f"=== {title} ===")
    pos = html.find(search_str)
    if pos != -1:
        print(html[max(0, pos-100):pos+length])
    else:
        print(f"'{search_str}' NOT FOUND")

print_section(curr_html, "CURRENT HTML addEmployeeForm", "addEmployeeForm")
print_section(back_html, "BACKUP HTML addEmployeeForm", "addEmployeeForm")

