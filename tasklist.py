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
        
    def save(self):
        list(self.lists.values())[0].save()
    
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
        self.parent = parent
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
        self.save()
    
    def addtask(self, task):
        if not task in self.tasks:
            self.tasks.append(task)
            task.lists[self.name] = self
            if self.parent is not None:
                self.parent.addtask(task)
            else:
                self.save()
    
    def removetask(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            del task.lists[self.name]
            self.save()
            return True
        return False
    
    def print(self):
        for i in range(len(self)): #print done tasks first
            if self[i].done:
                print(i, self[i].__str__())
        for i in range(len(self)): 
            if not self[i].done:
                print(i, self[i].__str__())
            
    def clean(self, expire_hours = 12):
        cleandate = datetime.now() - timedelta(hours = expire_hours)
        i = 0
        while i < len(self):
            if self[i].done and self[i].done < cleandate:
                self.removetask(self[i])
            else:
                i += 1
        self.save()

    @staticmethod
    def load(name):
        """static method that returns the Tasklist saved at filename or None on fail"""
        if exists(name + ".tasklist"):
            with open(name + ".tasklist", "rb") as file:
                return Tasklist(name, loaded_list = pickle.load(file))
        else:
            return None
    
    def save(self):
        if self.parent is None:
            with open(self.name + ".tasklist", "wb") as file:
                pickle.dump(self.tasks, file)
        else:
            self.parent.save()
    
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

def loadSavedLists():
    lists = {}
    if not exists("settings.settings"):
        ret = input("No saved settings were found. Create new default one and erase saved lists y/n? ").lower()
        if ret == "y":
            with open("settings.settings", 'w') as settings:
                settings.write("list alltasks \n" + "list todo parent alltasks \n\n" +"list shopping\n")
            lists["alltasks"] = Tasklist("alltasks")
            lists["shopping"] = Tasklist("shopping")
        return lists
    with open("settings.settings") as settings:
        for line in settings:
            words = line.split()
            if len(words) > 1 and words[0] == "list":
                newname = words[1]
                if len(words) > 3 and words[2] == "parent":
                    parentname = words[3]
                    if not parentname in lists:
                        print("Load error: list", newname, "has parent", parentname, "which was not found")
                    else:
                        lists[newname] = Tasklist(newname, lists[parentname])
                else:
                    lists[newname] = Tasklist.load(newname)
                    if lists[newname] is None:
                        print("Load error: Couldn't find saved list", newname)
    return lists


lists = loadSavedLists()
try:
    print("Tracking", len(lists["alltasks"]))
    thislist = lists["alltasks"]
except:
    print("Couldn't load alltasks")
    thislist = None
thistask = None
        
def UI_action(args):
    command = args[0] if len(args) > 0 else ""
    command = command.strip().lower()
    global thistask, thislist
    if command == "":
        return
    elif command.startswith("exit"):
        return True
    elif command in lists:
        thislist = lists[command]
        thislist.print()
    elif command == "new":
        name = input("name: ") #TODO multiple add
        if len(name) == 0:
            return
        thistask = Task(name, [])
        if len(args) == 1:
            args.append("alltasks")
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
        thistask.save()
    elif command == "undone":
        thistask.done = False
        thistask.save()
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


if __name__ == '__main__':
    while True:
        args = input(">>> ").split()
        if UI_action(args):
            break
