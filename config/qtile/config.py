# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import libqtile.resources
from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

import subprocess
import os
import sys
import time
sys.path.append('/home/dionisos/projets/programmation/python/qtile/')
# from org_mode_widget import OrgMode

mod = "mod4"
terminal = guess_terminal()
# gmail_password = subprocess.getoutput("/home/dionisos/scripts/.psw -p gmail")
# widgetGmail = widget.GmailChecker(username="denis.baudouin@gmail.com", password=gmail_password, fmt="{%s}", status_only_unseen=True, update_interval=67)
widgetVolume = widget.Volume(update_interval=200)
# widgetOrgMode = OrgMode()

@hook.subscribe.startup_once
def autostart():
  start = os.path.expanduser('~/.config/qtile/autostart.sh')
  subprocess.call([start])


def updateVolume(qtile, args=None):
  time.sleep(.100)
  widgetVolume.update()

keys = [
  # Sound and Mpd
  Key([], "XF86AudioRaiseVolume",
      lazy.spawn("amixer sset Master 5%+"), lazy.function(updateVolume)),
  Key([], "XF86AudioLowerVolume",
      lazy.spawn("amixer sset Master 5%-"), lazy.function(updateVolume)),
  Key([], "XF86AudioMute",
      lazy.spawn("amixer sset Master toggle"), lazy.function(updateVolume)),

    # Switch between windows in current stack pane
    Key([mod], "s", lazy.layout.down()),
  Key([mod], "d", lazy.layout.up()),

    Key([mod], "v", lazy.window.toggle_floating()),
  Key([mod, "shift"], "v", lazy.window.toggle_fullscreen()),

    # size
    Key([mod, "shift"], "Right", lazy.layout.increase_ratio()),
  Key([mod, "shift"], "Left", lazy.layout.decrease_ratio()),

    # Move windows up or down in current stack
    Key([mod, "control"], "k", lazy.layout.shuffle_down()),
  Key([mod, "control"], "j", lazy.layout.shuffle_up()),

    # Switch window focus to other pane(s) of stack
  # Key([mod], "o", lazy.group.focus_next()),
    Key([mod], "r", lazy.layout.next()),
  Key([mod], "t", lazy.group.prev()),
  Key([mod], "Right", lazy.group.next_window()),
  Key([mod], "Left", lazy.group.prev_window()),


    # Swap panes of split stack
  # Key([mod, "shift"], "r", lazy.layout.rotate()),
    Key([mod, "shift"], "r", lazy.layout.client_to_next()),

    # Toggle between split and unsplit sides of stack.
  # Split = all windows displayed
  # Unsplit = 1 window displayed, like Max layout, but still with
  # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
  Key([mod], "Return", lazy.spawn("terminator")),
  Key([mod, "control"], "f", lazy.spawn("qutebrowser")),
  Key([mod], "t", lazy.spawn("rofi -show run")),
	Key([mod, "control"], "t", lazy.spawn("rofi -show combi")),
  Key([mod], "o", lazy.spawn("dunstctl history-pop")),
  Key([mod], "k", lazy.spawn("dunstctl close-all")),
  Key([mod, "control"], "o", lazy.spawn("dunstctl close")),
  Key([mod, "control"], "h", lazy.spawn("hexchat")),
  Key([mod, "control"], "c", lazy.spawn("element-desktop")),
  # Key([mod, "control"], "t", lazy.spawn("gnome-clocks")),
  Key([mod, "control"], "p", lazy.spawn("firefox --private-window")),
  Key([mod, "control"], "e", lazy.spawn("emacsclient -c")),
  Key([mod, "control"], "m", lazy.spawn("smplayer")),
  Key([mod, "control"], "k", lazy.spawn("keepassxc")),
  # Key([mod, "control"], "c", lazy.spawn("/home/dionisos/scripts/com_software")),
  Key([], "Print", lazy.spawn("/home/dionisos/scripts/screenshot")),
  Key([mod], "m", lazy.spawn("/home/dionisos/scripts/dmenu-qtile-windowslist.py")),
  Key([mod, "control"], "s", lazy.spawn("systemctl suspend")),
  Key([mod, "shift"], "s", lazy.spawn("/home/dionisos/scripts/screensaver")),
  # Key([mod], "F9", lazy.function(lambda qtile, args=None: widgetGmail.tick())),
    Key([mod], "F8", lazy.spawn("/home/dionisos/scripts/pgm_keyboard/load")),
  Key([mod], "F7", lazy.spawn("setxkbmap fr")),
  Key([], "XF86Tools", lazy.spawn("playerctl next")), # https://quodlibet.readthedocs.io/en/latest/guide/interacting.html
  Key(["shift"], "XF86Tools", lazy.spawn("playerctl previous")),
  Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause")),

    # Toggle between different layouts as defined below
  Key([mod], "Tab", lazy.next_layout()),
  Key([mod], "space", lazy.next_layout()),
  Key([mod], "q", lazy.window.kill()),
  Key([], "XF86HomePage", lazy.window.kill()),

    Key([mod, "control"], "r", lazy.restart()),
  # Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "x", lazy.spawncmd()),
  Key([mod], "y", lazy.spawncmd()),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
# for vt in range(1, 8):
#     keys.append(
#         Key(
#             ["control", "mod1"],
#             f"f{vt}",
#             lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
#             desc=f"Switch to VT{vt}",
#         )
#     )


groups = [
  Group("a"),
  Group("u"),
  Group("i"),  # , matches=[Match(wm_class=["whats-app-nativefier-7bbd2c", "Skype", "Pidgin", "Hexchat"])]),
  Group("e"),  # , matches=[Match(wm_class=["Element"])]),
  Group("c"),
	Group("l"),
]

keybings = "auiecl"

for index, group in enumerate(groups):
  keys.extend([
    # mod1 + letter of group = switch to group
    Key([mod], keybings[index], lazy.group[group.name].toscreen(None, False)),

    # mod1 + shift + letter of group = switch to & move focused window to group
    Key([mod, "shift"], keybings[index], lazy.window.togroup(group.name)),
  ])

# for i in groups:
#     keys.extend(
#         [
#             # mod + group number = switch to group
#             Key(
#                 [mod],
#                 i.name,
#                 lazy.group[i.name].toscreen(),
#                 desc=f"Switch to group {i.name}",
#             ),
#             # mod + shift + group number = switch to & move focused window to group
#             Key(
#                 [mod, "shift"],
#                 i.name,
#                 lazy.window.togroup(i.name, switch_group=True),
#                 desc=f"Switch to & move focused window to group {i.name}",
#             ),
#             # Or, use below if you prefer not to switch to that group.
#             # # mod + shift + group number = move focused window to group
#             # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
#             #     desc="move focused window to group {}".format(i.name)),
#         ]
#     )

layouts = [
	  layout.Max(),
		layout.Stack(num_stacks=2),
		layout.VerticalTile()
    # layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=4),
    # layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

logo = os.path.join(os.path.dirname(libqtile.resources.__file__), "logo.png")
screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
								# widget.TextBox(),
								# OrgMode(),
								# widgetOrgMode,
								# widget.Battery(format='[{char} {percent:2.0%}]'),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
								widgetVolume,
								widget.Systray(),
                # widget.TextBox("default config", name="default"),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
								widget.Clock(format='%d-%m-%Y %a %R'),
								# widget.Notify(default_timeout=10)
                # widget.QuickExit(),
            ],
            24,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
        background="#000000",
        wallpaper=logo,
        wallpaper_mode="center",
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
focus_previous_on_window_remove = False
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
