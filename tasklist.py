# -*- coding: utf-8 -*-
"""
Created Feb 2022

@author: Niraj
#TODO:
    due date
    recurring tasks
    server controllable from phone
    voice control (cool)

"""
import pickle
from os.path import exists
from datetime import datetime, timedelta

class Task:
    def __init__(self, name, parentlists, desc=None, duedate=None, recurring = False):
        self.name = name.strip()
        self.desc = desc
        self.lists = {}
        for l in parentlists:
            l.addtask(self)
        self.duedate = duedate
        self.done = False
        self.recurring = recurring
    
    def __str__(self):
        return ("DONE " if self.done else "") + self.name + ("" if self.desc is None else " "+ self.desc)
    def __getstate__(self):
        state = self.__dict__.copy()
        state['lists'] = list(state["lists"].keys())
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lists = {n: None for n in self.lists}
    
class Tasklist:
    def __init__(self, name, parent = None, loaded_list = None):
        """if parent is not None, this tasklist will inherit all the tasks from its parent that have this task's name in their list of lists.
        loaded_list is the list of tasks loaded from a saved pickle file"""
        self.name = name
        self.tasks = []
        if loaded_list is not None:
            for task in loaded_list:
                newtask = Task(task.name, [], desc=task.desc, duedate=task.duedate, recurring = task.recurring)
                newtask.lists = task.lists
                newtask.done = task.done
                self.addtask(newtask)
        if not parent is None:
            for task in parent:
                if self.name in task.lists:
                    self.addtask(task)
    
    def newtask(self, name, desc = None, duedate = None, recurring = False):
        self.addtask(Task(name, [self], desc, duedate, recurring))
    
    def addtask(self, task):
        if not task in self.tasks:
            self.tasks.append(task)
            task.lists[self.name] = self
    
    def removetask(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            del task.lists[self.name]
            return True
        return False
    
    def print(self):
        for i in range(len(self)):
            print(i, self[i].__str__())
            
    def clean(self, expire_hours = 12):
        cleandate = datetime.now() - timedelta(hours=-expire_hours)
        i = 0
        while i < len(self):
            if self[i].done and self[i].done < cleandate:
                self.removetask(self[i])
            else:
                i += 1

    @staticmethod
    def load(name):
        """static method that returns the Tasklist saved at filename or None on fail"""
        if exists(name + ".tasklist"):
            with open(name + ".tasklist", "rb") as file:
                return Tasklist(name, loaded_list = pickle.load(file))
        else:
            return None
    
    def save(self):
        with open(self.name + ".tasklist", "wb") as file:
            pickle.dump(self.tasks, file)
    
    def __getitem__(self, key):
        return self.tasks[key]
    def __len__(self):
        return len(self.tasks)
    def __iter__(self):
        self._index = 0
        return self
    def __next__(self):
        self._index += 1
        if self._index <= len(self):
            return self[self._index - 1]
        raise StopIteration


#load saved data
alltasks = Tasklist.load("alltasks")
if alltasks is None:
    ret = input("No saved alltasks list was found. Create blank one y/n? ").lower()
    if ret == "y":
        alltasks = Tasklist("alltasks")
else:
    print("Tracking", len(alltasks))
today = Tasklist("today", parent = alltasks)
todo = Tasklist("todo", parent = alltasks)
hard = Tasklist("hard", parent = alltasks)
fun = Tasklist("fun", parent = alltasks)
lists = {"today": today, "todo": todo, "alltasks": alltasks, "hard": hard, "fun": fun}

def main():
    thistask = None
    thislist = alltasks
    
    while True:
        args = input(">>> ").split()
        command = args[0] if len(args) > 0 else "" #command is first, the rest of the args are available if needed
        command = command.strip().lower()
        if command == "":
            continue
        elif command.startswith("exit"):
            break
        elif command in lists:
            thislist = lists[command]
            thislist.print()
        elif command == "new":
            name = input("name: ") #TODO multiple add
            thistask = Task(name, [alltasks])
            for i in range(1, len(args)):
                try:
                    lists[args[i]].addtask(thistask)
                except KeyError:
                    print("No list named", args[i])
        elif command == "task":
            if len(args) > 1: #pick from list
                try:
                    thistask = thislist[int(args[1])]
                except:
                    print("what is", args[1])
            if thistask is None:
                print("None")
            else:
                print(thistask, "in", list(thistask.lists))
        elif command == "add":
            for i in range(1, len(args)):
                try:
                    lists[args[i]].addtask(thistask)
                except KeyError:
                    print("No list named", args[i])
        elif command == "done":
            thistask.done = datetime.now()
        elif command == "undone":
            thistask.done = False
        elif command == "clean":
            if len(args) > 1 and args[1] == "all":
                for l in lists.values():
                    l.clean(expire_hours=0)
            else:
                for l in lists.values():
                    l.clean()
        elif command == "due":
            #TODO
            pass
        elif command == "remove":
            print(thistask)
            if len(args) > 1:
                removelist = [lists[l] for l in args[1:] if l in lists]
            else:
                removelist = list(thistask.lists.values())
            for l in removelist:
                if l.removetask(thistask):
                    print("REMOVED from", l.name)
        alltasks.save()

if __name__ == '__main__':
    main()
