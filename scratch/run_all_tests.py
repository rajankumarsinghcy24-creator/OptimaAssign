import os
import sys
import glob
import subprocess

scratch_dir = os.path.dirname(__file__)
test_files = glob.glob(os.path.join(scratch_dir, "*.py"))

print(f"Found {len(test_files)} python scripts in scratch:")
for tf in test_files:
    fname = os.path.basename(tf)
    if fname in ['diagnose_regression.py', 'diagnose_forms.py', 'diagnose_emp_modal.py', 'check_html_elements.py', 'test_syntax_fix.py', 'check_missing_ids.py', 'check_app_py_diff.py', 'check_backup_submit.py', 'run_all_tests.py']:
        continue
    print(f"\n==================================================")
    print(f"RUNNING: {fname}")
    print(f"==================================================")
    res = subprocess.run([sys.executable, tf], capture_output=True, text=True)
    print("RETURN CODE:", res.returncode)
    if res.stdout:
        print("STDOUT:\n", res.stdout[:500])
    if res.stderr:
        print("STDERR:\n", res.stderr[:500])

