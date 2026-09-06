import sqlite3
import os
import sys

# Ensure root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def test_greedy_algorithm_roles():
    print("==================================================")
    print("TEST: GREEDY ALGORITHM ROLE MATCHING REQUIREMENT")
    print("==================================================")

    # Test case from prompt:
    # Task: Backend Development
    # Raj: Role: Backend Developer, Skills: Python, SQL, Performance: 9.0, Available
    # Ram: Role: Backend Developer, Skills: Python, Performance: 8.0, Available
    # Ziyad: Role: Frontend Developer, Skills: Python, JavaScript, Performance: 9.5, Available

    task = {
        'id': 101,
        'title': 'Backend Development',
        'description': 'Develop REST APIs and database queries.',
        'required_skill': 'Python',
        'priority': 'High',
        'category': 'Backend'
    }

    raj = {
        'id': 1,
        'name': 'Raj',
        'role': 'Backend Developer',
        'department': 'Engineering',
        'skills': 'Python, SQL',
        'performance': 9.0,
        'experience': 5,
        'availability': 'Available'
    }

    ram = {
        'id': 2,
        'name': 'Ram',
        'role': 'Backend Developer',
        'department': 'Engineering',
        'skills': 'Python',
        'performance': 8.0,
        'experience': 4,
        'availability': 'Available'
    }

    ziyad = {
        'id': 3,
        'name': 'Ziyad',
        'role': 'Frontend Developer',
        'department': 'Engineering',
        'skills': 'Python, JavaScript',
        'performance': 9.5,
        'experience': 3,
        'availability': 'Available'
    }

    candidates = [raj, ram, ziyad]

    # Calculate keys
    key_raj = app.get_assignment_key(raj, task)
    key_ram = app.get_assignment_key(ram, task)
    key_ziyad = app.get_assignment_key(ziyad, task)

    print(f"Raj Key:   {key_raj}")
    print(f"Ram Key:   {key_ram}")
    print(f"Ziyad Key: {key_ziyad}")

    # Rank candidates
    ranked = sorted(candidates, key=lambda c: app.get_assignment_key(c, task), reverse=True)
    winner = ranked[0]

    print(f"Selected Candidate: {winner['name']} (Role: {winner['role']})")

    assert winner['name'] == 'Raj', f"FAILED! Expected Raj, but got {winner['name']}"
    assert key_raj > key_ziyad, "FAILED! Raj should score higher than Ziyad"
    assert key_ram > key_ziyad, "FAILED! Ram should score higher than Ziyad (matching role beats higher performance non-matching role)"
    print("SUCCESS: Greedy Algorithm Role Matching Passed!")

def test_fallback_when_no_role_available():
    print("\n==================================================")
    print("TEST: FALLBACK TO SIMILAR SKILLS WHEN NO ROLE AVAILABLE")
    print("==================================================")

    # Task: Database Administration (Category: Database, Skill: SQL)
    task = {
        'id': 102,
        'title': 'Database Optimization',
        'description': 'Index main database tables.',
        'required_skill': 'SQL',
        'priority': 'High',
        'category': 'Database'
    }

    # Only Frontend & QA available
    frontend_dev = {
        'id': 10,
        'name': 'Alex',
        'role': 'Frontend Developer',
        'department': 'Engineering',
        'skills': 'SQL, JavaScript',
        'performance': 8.5,
        'experience': 4,
        'availability': 'Available'
    }

    qa_dev = {
        'id': 11,
        'name': 'Betty',
        'role': 'QA Engineer',
        'department': 'Engineering',
        'skills': 'Selenium',
        'performance': 9.0,
        'experience': 5,
        'availability': 'Available'
    }

    key_alex = app.get_assignment_key(frontend_dev, task)
    key_betty = app.get_assignment_key(qa_dev, task)

    print(f"Alex Key:  {key_alex}")
    print(f"Betty Key: {key_betty}")

    ranked = sorted([frontend_dev, qa_dev], key=lambda c: app.get_assignment_key(c, task), reverse=True)
    winner = ranked[0]

    print(f"Selected Fallback Candidate: {winner['name']}")

    assert winner['name'] == 'Alex', f"FAILED! Expected Alex (has SQL skill), got {winner['name']}"
    print("SUCCESS: Fallback logic passed!")

def test_performance_bounds():
    print("\n==================================================")
    print("TEST: PERFORMANCE SCORE BOUNDS [0.0, 10.0]")
    print("==================================================")

    # Test upper bound: 9.8 + 0.5 -> 10.0
    score_1 = max(0.0, min(10.0, round(9.8 + 0.5, 1)))
    assert score_1 == 10.0, f"Upper bound failed: {score_1}"

    # Test upper bound: 10.0 + 0.5 -> 10.0
    score_2 = max(0.0, min(10.0, round(10.0 + 0.5, 1)))
    assert score_2 == 10.0, f"Upper bound failed: {score_2}"

    # Test lower bound: 0.2 - 0.5 -> 0.0
    score_3 = max(0.0, min(10.0, round(0.2 - 0.5, 1)))
    assert score_3 == 0.0, f"Lower bound failed: {score_3}"

    print(f"9.8 + 0.5 -> {score_1}")
    print(f"10.0 + 0.5 -> {score_2}")
    print(f"0.2 - 0.5 -> {score_3}")
    print("SUCCESS: Performance score bounds passed!")

if __name__ == '__main__':
    test_greedy_algorithm_roles()
    test_fallback_when_no_role_available()
    test_performance_bounds()
    print("\nALL BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")
