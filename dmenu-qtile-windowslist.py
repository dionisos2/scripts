#!/usr/bin/env python

from libqtile.command import Client
import subprocess
import re

# connect to Qtile
c = Client()

# get info of windows
wins = []
id_map = {}
id = 0
win_properties = subprocess.getoutput("wmctrl -lx")
win_properties = [win.split(maxsplit=4) for win in win_properties.split("\n")]
win_dict = {}
for win in win_properties:
    win_title = win[4]
    win_dict[win_title] = win[2].split(".")[1] + "-" + win_title[-10:]

for win in c.windows():
    if win["group"]:
        if win["name"] in win_dict:
            name = win_dict[win["name"]]
        else:
            name = win["name"]

        wins.append(bytes("%i: %s (%s)" % (id, name, win["group"]),
            'utf-8'))
        id_map[id] = {
                'id' : win['id'],
                'group' : win['group']
                }
        id = id +1

# call dmenu
DMENU='dmenu -i -p ">>>" -nb #000 -nf #fff -sb #00BF32 -sf #fff'
p = subprocess.Popen(DMENU.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
out = p.communicate(b"\n".join(wins))[0]

# get selected window info
win_selected = re.match(b"^\d+", out)

if win_selected:
    id = int(re.match(b"^\d+", out).group())
else:
    quit(1)

win = id_map[id]

# focusing selected window
g = c.group[win["group"]]
g.toscreen()
w = g.window[win["id"]]
for i in range(len(g.info()["windows"])):
    insp = w.inspect()
    if insp['attributes']['map_state']:
        break

g.next_window()
