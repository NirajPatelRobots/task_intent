# -*- coding: utf-8 -*-
"""
Task_Intent
Task tracking and planning app
Created Apr 2022 by Niraj
TODO:
    settings instructions

    server controllable from phone
    voice control (cool)
"""
from datetime import datetime
import tasklist

lists = tasklist.loadSavedLists()
try:
    print("Tracking", len(lists["alltasks"]))
    thislist: tasklist.Tasklist = lists["alltasks"]
except:
    print("Couldn't load alltasks")
    thislist: tasklist.Tasklist = None
thistask: tasklist.Task = None
        
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
        if len(name) == 0: #TODO check already exists
            return
        thistask = tasklist.Task(name, [])
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
            else:
                if len(args) > 2:
                    UI_action(args[2:])
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
        thistask.save_lists()
    elif command == "undone":
        thistask.done = False
        thistask.save_lists()
    elif command == "recurring":
        thistask.recurring = True
        thistask.save_lists()
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
