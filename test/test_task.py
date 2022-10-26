""" test Task class for task_intent
TODO:
    test save with junk member to show reload deletes junk member
    mock datetime?
"""

import unittest
from datetime import datetime
from typing import List, Callable
from mock import Mock
import pickle
import tasklist
Task = tasklist.Task


class TestTask(unittest.TestCase):
    @staticmethod
    def tasklist_addtask_side_effect(mock_tasklist: Mock) -> Callable[[Task], None]:
        def ret_fcn(task: Task):
            task.lists[mock_tasklist.name] = mock_tasklist
        return ret_fcn

    def setUp(self):
        self.mockTasklists = [Mock() for _ in range(2)]
        for mockTasklist in self.mockTasklists:
            mockTasklist.name = "mocklist" + str(id(mockTasklist))
            mockTasklist.addtask.side_effect = self.tasklist_addtask_side_effect(mockTasklist)


    def test_create(self):
        task = Task("test_task", self.mockTasklists)
        for mockTasklist in self.mockTasklists:
            mockTasklist.addtask.assert_called_once_with(task)
            self.assertIn(mockTasklist, task.lists.values())

    def test_save_lists(self):
        task = Task("test_task", self.mockTasklists)
        task.save_lists()
        for mockTasklist in self.mockTasklists:
            mockTasklist.save.assert_called_once_with(False)

    def test_str_shows_changes(self):
        task = Task("test_task", self.mockTasklists)
        plain_txt = str(task)
        task.done = datetime.now()
        done_txt = str(task)
        self.assertNotEqual(plain_txt, done_txt)
        task.recurring = True
        recurring_done_txt = str(task)
        self.assertNotEqual(plain_txt, recurring_done_txt)
        self.assertNotEqual(done_txt, recurring_done_txt)
        task.done = False
        recurring_txt = str(task)
        # self.assertNotEqual(plain_txt, recurring_txt)  # does not print whether undone is recurring
        self.assertNotEqual(done_txt, recurring_txt)
        self.assertNotEqual(recurring_done_txt, recurring_txt)
        for txt in [plain_txt, done_txt, recurring_txt, recurring_done_txt]:
            self.assertIn("test_task", txt)

    def test_pickle_no_junk(self):
        task = Task("test_task", self.mockTasklists, desc="description", recurring=True)
        task.junk = "This is junk"
        pickled_task = pickle.dumps(task)
        print(f"Pickled task with 2 tasklists is {len(pickled_task)} bytes. ", end='')
        unpickled_task: Task = pickle.loads(pickled_task)
        self.assertEqual(task.name, unpickled_task.name)
        self.assertEqual(task.desc, unpickled_task.desc)
        self.assertEqual(task.done, unpickled_task.done)
        self.assertEqual(task.duedate, unpickled_task.duedate)
        self.assertEqual(task.recurring, unpickled_task.recurring)
        for tasklist_name, tasklist_value in unpickled_task.lists.items():
            self.assertIn(tasklist_name, task.lists)
            self.assertIsNone(tasklist_value)
        self.assertFalse(hasattr(unpickled_task, "junk"))

