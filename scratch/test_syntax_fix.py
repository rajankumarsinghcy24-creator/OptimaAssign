import re
import subprocess

with open('static/app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Fix the duplicate block at line 2064-2071 in test memory
dup_pattern = """  backdrop.classList.add('show');
  drawer.classList.add('show');
}
  
  // Show drawer
  backdrop.classList.add('show');
  drawer.classList.add('show');
}"""

if dup_pattern in js_content:
    print("Found exact duplicate block in openEmployeeProfile!")
    fixed_js = js_content.replace(dup_pattern, """  backdrop.classList.add('show');
  drawer.classList.add('show');
}""")
    with open('scratch/temp_app.js', 'w', encoding='utf-8') as f:
        f.write(fixed_js)
    
    res = subprocess.run(['node', '--check', 'scratch/temp_app.js'], capture_output=True, text=True)
    if res.returncode == 0:
        print("node --check passed on fixed temp_app.js! Syntax is clean.")
    else:
        print("node --check failed:", res.stderr)
else:
    print("Exact dup pattern not found, checking with regex...")

