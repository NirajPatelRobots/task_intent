"""Test Tasklist class for task_intent
TODO:
    test save and load
    test loaded_list
    test child Tasklist inherit tasks
    test removetask
    test clean
    test iteration dunders
    test loadSavedLists
"""
import unittest
import tasklist
from mock import Mock, patch, mock_open
Tasklist = tasklist.Tasklist


class TestTasklist(unittest.TestCase):
    def setUp(self):
        self.tasklist = Tasklist("test_list")
        self.open_patch = patch("builtins.open", new_callable=mock_open, read_data="data")

    def tearDown(self):
        self.open_patch.stop()


    def test_create_new(self):
        self.assertEqual("test_list", self.tasklist.name)
        self.assertEqual(0, len(self.tasklist))

    def test_create_child_empty(self):
        child_list = Tasklist("child", self.tasklist)
        self.assertEqual("child", child_list.name)
        self.assertEqual("test_list", child_list.parent.name)
        self.assertEqual(0, len(child_list))

    def test_load_nonexistent(self):
        self.tasklist = Tasklist.load("doesnt_exist")
        self.assertIsNone(self.tasklist)

    def test_new_task(self):
        self.tasklist.newtask("test_task", desc="desc")
        self.assertEqual(1, len(self.tasklist))
        self.assertEqual("test_task", self.tasklist[0].name)

    def test_add_task(self):
        task = tasklist.Task("test_task", [], desc="desc")
        self.tasklist.addtask(task)
        self.tasklist.addtask(task)
        self.assertEqual(1, len(self.tasklist))
        self.assertIn(task, self.tasklist)

    def test_remove_nonexistent(self):
        task = tasklist.Task("test_task", [])
        self.assertFalse(self.tasklist.removetask(task))
