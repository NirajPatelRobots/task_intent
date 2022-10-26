# task_intent
Task planning app

## Code
To run the app as a UI, run `python3 task_intent/tasklist.py`.

The first time it is run, it creates new `settings.settings` and `alltasks.tasklist` files.

## Instructions
Tasks are contained in task lists. alltasks exists by default, and other lists can have alltasks as a parent or be stored separately.
For example, alltasks could contain the 'todo' list, which can contain a 'today' list. A 'shopping' list can be separate.

The UI works by commands. The commands are new, task, add, done, undone, clean, due, remove and exit.

To select a task list, enter the list name.
~~~~
>>> today
0 DONE lazy vacuum room
2 DONE dishes
1 learn markdown
~~~~

To select a task from that list, enter `task` and its number. To see the selected task, enter `task` without a number.
Use `new` to create a new task.
```
>>>task 2
DONE dishes in ['today', 'todo', 'alltasks']
>>>new today
name: write task_intent instructions
>>>task
write task_intent instructions in ['today', 'todo', 'alltasks']
>>> task 0 remove today
REMOVED from today
DONE lazy vacuum room in ['todo', 'alltasks']
```
After a task is selected, use `add [listname]`, `done`, `undone`, or `remove [listname]` to change it. 
You can do this on the same line as a task selection or at any time until another task is selected.

`clean` will remove all tasks that have been done longer than 12 hours, and `clean all` will remove all done tasks.
