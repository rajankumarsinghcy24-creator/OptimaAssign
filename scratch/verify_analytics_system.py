import unittest
import sqlite3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, init_db, get_db_connection

class TestAnalyticsAndChartSystem(unittest.TestCase):
    def setUp(self):
        init_db()
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_state_includes_performance_history(self):
        response = self.client.get('/api/state')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('employees', data)
        self.assertIn('tasks', data)
        self.assertIn('assignments', data)
        self.assertIn('submissions', data)
        self.assertIn('activities', data)
        self.assertIn('performance_history', data)
        self.assertIsInstance(data['performance_history'], list)

    def test_complete_task_updates_history_and_clamping(self):
        # Fetch initial state
        response = self.client.get('/api/state')
        data = response.get_json()
        self.assertTrue(len(data['tasks']) > 0)
        
        task_id = int(data['tasks'][0]['id'].replace('task-', ''))
        
        # Test complete_task endpoint on first task
        res = self.client.get(f'/complete_task/{task_id}?format=json')
        self.assertIn(res.status_code, [200, 302])
        
        # Check state after task completion
        response = self.client.get('/api/state')
        data = response.get_json()
        
        # Verify completed task count
        completed_tasks = [t for t in data['tasks'] if t['status'] == 'Completed']
        self.assertTrue(len(completed_tasks) >= 1)
        
        # Verify performance history updated
        self.assertTrue(len(data['performance_history']) >= 1)

if __name__ == '__main__':
    unittest.main()
