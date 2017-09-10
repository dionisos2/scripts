#!/usr/bin/python2
from PyOrgMode import PyOrgMode

base = PyOrgMode.OrgDataStructure()

base.load_from_file("/home/dionisos/organisation/agenda.org")

todo_list = base.extract_todo_list()

# print([base.root.content[0].content])
# print(len(todo_list))

for task in todo_list:
    print(str(task))
    print(task.heading)
    print(task.priority)
    print(task.scheduled)
    print(task.tags)

todo_list = [task for task in todo_list if task.priority == 'A']

print(len(todo_list))
