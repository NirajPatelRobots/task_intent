#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Feb 2022

@author: Niraj
TODO:
    backup
    due date
    recurring task scheduling
    subtasks
    rename
    Share tasks between unconnected lists
    recent recurring tasks show hours
    settings list filepath
    figure out when to save
    restructure loadSavedLists
    be more careful when loading pickle
"""
from __future__ import annotations
import pickle
from os.path import exists, join, dirname
from datetime import datetime, timedelta
from typing import List, Dict, Any


class Task:
    def __init__(self, name: str, parentlists: List, desc: str = None, duedate=None, recurring=False):
        self.name: str = name.strip()
        self.desc: str = desc
        self.duedate: datetime = duedate
        self.done: datetime = False
        self.recurring: bool = recurring
        self.lists: Dict[str, Tasklist] = {}
        for l in parentlists:
            l.addtask(self)
        
    def save_lists(self):
        for l in self.lists.values():
            if l is not None:
                l.save(False)
    
    def __str__(self):
        if self.recurring:
            return self.name \
                   + (" (LAST: {} days)".format((datetime.now() - self.done).days) if self.done else "") \
                   + ("" if self.desc is None else " "+ self.desc)
        return ("DONE " if self.done else "") \
               + self.name + ("" if self.desc is None else " "+ self.desc)

    def __getstate__(self) -> Dict[str, Any]:
        state = {"name": self.name, "desc": self.desc, "duedate": self.duedate, "recurring": self.recurring,
                 "done": self.done, 'lists': list(self.lists.keys())}
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lists = {n: None for n in self.lists}


class Tasklist:
    def __init__(self, name: str, parent: Tasklist = None, loaded_list: List[Task] = None):
        """if parent is not None, this tasklist will inherit all the tasks from its parent that have this task's name in their list of lists.
        loaded_list is the list of tasks loaded from a saved pickle file"""
        self.name = name
        self.tasks = []
        self.parent = parent
        if loaded_list is not None:
            for task in loaded_list:
                if type(task) is Task:
                    self.addtask(task)
                else:
                    print("couldn't add to list:", task)
        if parent is not None:
            for task in parent:
                if self.name in task.lists:
                    self.addtask(task)
    
    def newtask(self, name: str, desc: str = None, duedate = None, recurring = False):
        self.addtask(Task(name, [self], desc, duedate, recurring))
        self.save()
    
    def addtask(self, task: Task):
        if task not in self.tasks:
            self.tasks.append(task)
            task.lists[self.name] = self
            if self.parent is not None:
                self.parent.addtask(task)
            else:
                self.save()
    
    def removetask(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)
            del task.lists[self.name]
            self.save()
            return True
        return False
    
    def print(self):
        for i in range(len(self)):  # print done tasks first
            if self[i].done and not self[i].recurring:
                print(i, str(self[i]))
        for i in range(len(self)): 
            if not self[i].done or self[i].recurring:
                print(i, str(self[i]))
            
    def clean(self, expire_hours: int = 12):
        cleandate = datetime.now() - timedelta(hours=expire_hours)
        i = 0
        while i < len(self):
            if self[i].done and not self[i].recurring and self[i].done < cleandate:
                self.removetask(self[i])
            else:
                i += 1
        self.save()

    @staticmethod
    def load(name: str):
        """static method that returns the Tasklist saved at filename or None on fail"""
        filename = join(dirname(__file__), name + ".tasklist")
        if exists(filename):
            with open(filename, "rb") as file:
                return Tasklist(name, loaded_list = pickle.load(file))
        else:
            return None
    
    def save(self, chainparent: bool = True):
        if self.parent is None:
            with open(join(dirname(__file__), self.name + ".tasklist"), "wb") as file:
                pickle.dump(self.tasks, file)
        elif chainparent:
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
    settingsfilename = join(dirname(__file__), "settings.settings")
    if not exists(settingsfilename):
        ret = input("No saved settings were found. Create new default one and erase saved lists y/n? ").lower()
        if ret == "y":
            with open(settingsfilename) as settings:
                settings.write("list alltasks \n" + "list todo parent alltasks \n\n" +"list shopping\n")
            lists["alltasks"] = Tasklist("alltasks")
            lists["shopping"] = Tasklist("shopping")
        return lists
    with open(settingsfilename) as settings:
        for line in settings:
            words = line.split()
            if len(words) <= 1 or words[0].startswith('#'):
                continue
            if words[0] == "list":
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
                        ret = input("Couldn't find saved list "+ newname +", make new saved list y/n? ")
                        if ret.lower() == "y":
                            lists[newname] = Tasklist(newname)
                            lists[newname].save()
    return lists



