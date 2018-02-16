#!/usr/bin/python
from PyOrgMode import PyOrgMode

base = PyOrgMode.OrgDataStructure()

base.load_from_file("/home/dionisos/organisation/agenda.org")

todo_list = base.extract_todo_list()

# print([base.root.content[0].content])
# print(len(todo_list))
todo_list = [task for task in todo_list if task.priority == 'A']

for task in todo_list:
    print(str(task))
    print(task.heading)
    print(task.priority)
    print(task.scheduled)
    print(task.tags)

print(len(todo_list))
