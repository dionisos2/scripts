-- luac -p ~/.config/awesome/rc.lua to verify syntax !
-- xev to know code of one key

-- Standard awesome library
local gears = require("gears")
local awful = require("awful")
awful.rules = require("awful.rules")
require("awful.autofocus")
-- Widget and layout library
local wibox = require("wibox")
-- Theme handling library
local beautiful = require("beautiful")
-- Notification library
local naughty = require("naughty")
local menubar = require("menubar")

local vicious = require("vicious")

--Perso
require("environnement")

function implode(delimiter, list)
  local string = ""
  for i,v in pairs(list) do
    string = string .. delimiter .. i .. "/" .. v
  end
  return string
end


-- {{{ Error handling
-- Check if awesome encountered an error during startup and fell back to
-- another config (This code will only ever execute for the fallback config)
if awesome.startup_errors then
    naughty.notify({ preset = naughty.config.presets.critical,
                     title = "Oops, there were errors during startup!",
                     text = awesome.startup_errors })
end

-- Handle runtime errors after startup
do
    local in_error = false
    awesome.connect_signal("debug::error", function (err)
        -- Make sure we don't go into an endless error loop
        if in_error then return end
        in_error = true

        naughty.notify({ preset = naughty.config.presets.critical,
                         title = "Oops, an error happened!",
                         text = err })
        in_error = false
    end)
end
-- }}}

-- {{{ Variable definitions
-- Themes define colours, icons, and wallpapers
beautiful.init("/home/dionisos/.config/awesome/themes/default/theme.lua")

theme.wallpaper = "/home/dionisos/documents/images/moine.jpeg"
-- Default modkey.
-- Usually, Mod4 is the key with a logo between Control and Alt.
-- If you do not like this or do not have such a key,
-- I suggest you to remap Mod4 to another key using xmodmap or other tools.
-- However, you can use another modifier like Mod1, but it may interact with others.
modkey = "Mod4"

-- Table of layouts to cover with awful.layout.inc, order matters.
local layouts =
{
    awful.layout.suit.floating,
    awful.layout.suit.tile,
    -- awful.layout.suit.tile.left,
    -- awful.layout.suit.tile.bottom,
    -- awful.layout.suit.tile.top,
    -- awful.layout.suit.fair,
    -- awful.layout.suit.fair.horizontal,
    -- awful.layout.suit.spiral,
    -- awful.layout.suit.spiral.dwindle,
    awful.layout.suit.max,
    -- awful.layout.suit.max.fullscreen,
    -- awful.layout.suit.magnifier
}
-- }}}

-- {{{ Wallpaper
if beautiful.wallpaper then
    for s = 1, screen.count() do
        gears.wallpaper.maximized(beautiful.wallpaper, s, true)
    end
end
-- }}}

-- {{{ Tags
-- Define a tag table which hold all screen tags.
tags = {names = {"main","prog","console","com","musique","divers"},
		layout = {layouts[2],layouts[2],layouts[2],layouts[2],layouts[2],layouts[2]}}

for s = 1, screen.count() do
    -- Each screen has its own tag table.
    tags[s] = awful.tag(tags.names, s, tags.layout)
end
-- }}}

-- {{{ Menu
-- Create a laucher widget and a main menu
myawesomemenu = {
   { "firefox", "firefox" },
   { "gnome-clocks", "gnome-clocks" },
   { "krusader", "krusader" },
   { "emacs", "emacsclient -c" },
   { "pidgin", "pidgin" },
   { "gedit", "gedit" },
   { "quodlibet", "quodlibet" },
   { "terminator", "terminator" },
   { "bépo", "/home/dionisos/scripts/pgm_keyboard/load" },
   { "azerty", terminal_cmd .. "setxkbmap fr" },
   { "edit config", editor .. " " .. awful.util.getdir("config") .. "/rc.lua" },
   { "suspend", terminal_cmd .. "/home/dionisos/scripts/mysuspend" },
   { "restart", awesome.restart }
}

mymainmenu = awful.menu({ items = { { "awesome", myawesomemenu, beautiful.awesome_icon },
                                    { "open terminal", terminal }
                                  }
                        })

mylauncher = awful.widget.launcher({ image = beautiful.awesome_icon,
                                     menu = mymainmenu })

function format_net(widget, args)
   if(args['{enp5s0 carrier}'] == 1)then
	  network = 'enp5s0'
	  network_down_kb = args['{enp5s0 down_kb}']
	  network_up_kb = args['{enp5s0 up_kb}']
   elseif(args['{wlp3s0 carrier}'] == 1) then
	  network = 'wlp3s0'
	  network_down_kb = args['{wlp3s0 down_kb}']
	  network_up_kb = args['{wlp3s0 up_kb}']
   else
	  network = false
   end

   if (network ~= false) then
	  return network .. ':<span color="#CC9393">' .. network_down_kb .. '</span>/<span color="#7F9F7F">' .. network_up_kb .. '</span>'
   else
	  return 'unconnected'
   end
end

function format_org(widget, args)
   if (args[2] > 0) then
	  color = '"#CC9393"'
   else
	  color = '"#7F9F7F"'
   end

   return string.format("<span color=%s> %d/%d(%d) </span>", color, args[2], args[3], args[1])
end

do
   local already_hibernate = false

   function format_bat(widget, args)
	  if (args[2] < 20) then
		 color = '"#CC9393"'
	  else
		 color = '"#7F9F7F"'
		 already_hibernate = false
	  end

	  if (args[2] < 10) and not(already_hibernate) and (args[1] == "-") then
		 already_hibernate = true
		 awful.util.spawn(terminal_cmd .. "/home/dionisos/scripts/hibernation")
	  end

	  if (already_hibernate) then
		 info = "N"
	  else
		 info = "S"
	  end

	  return string.format("<span color=%s> %s%d%s</span>", color, args[1], args[2], info)
   end
end

-- My mail updater widget
function mailcount(format, warg)
    os.execute("/home/dionisos/scripts/unread.py > /home/dionisos/.mailcount")
    local f = io.open("/home/dionisos/.mailcount")

    local l = nil
    if f ~= nil then
       l = f:read()
       f:close()
    else
       l = "?"
    end

    if l == nil then
       l = "?"
    end
    return {tostring(l)}
end

netwidget = wibox.widget.textbox()
batwidget = wibox.widget.textbox()
debugwidget = wibox.widget.textbox('')
volumewidget = wibox.widget.textbox()
orgwidget = wibox.widget.textbox()
mailwidget = wibox.widget.textbox()

-- vicious.register(netwidget, vicious.widgets.net, format_net, 10)
vicious.register(batwidget, vicious.widgets.bat, format_bat, 29, 'BAT0')
local sound_controller = io.popen("/home/dionisos/scripts/current_sound_controller"):read("*all")
vicious.register(volumewidget, vicious.widgets.volume, '$2$1% ', 31, sound_controller)
vicious.register(orgwidget, vicious.widgets.org, format_org, 59, {'/home/dionisos/organisation/agenda.org'})
vicious.register(mailwidget, mailcount, ' {$1}', 1223)

os.setlocale("fr_FR.UTF-8") -- Français
mytextclock = awful.widget.textclock(" %a/%d/%b/%H:%M ")

-- Menubar configuration
menubar.utils.terminal = terminal -- Set the terminal for applications that require it
-- }}}

-- {{{ Wibox
-- Create a textclock widget


-- Create a wibox for each screen and add it
mywibox = {}
mypromptbox = {}
mylayoutbox = {}
mytaglist = {}
mytaglist.buttons = awful.util.table.join(
                    awful.button({ }, 1, awful.tag.viewonly),
                    awful.button({ modkey }, 1, awful.client.movetotag),
                    awful.button({ }, 3, awful.tag.viewtoggle),
                    awful.button({ modkey }, 3, awful.client.toggletag),
                    awful.button({ }, 4, function(t) awful.tag.viewnext(awful.tag.getscreen(t)) end),
                    awful.button({ }, 5, function(t) awful.tag.viewprev(awful.tag.getscreen(t)) end)
                    )
mytasklist = {}
mytasklist.buttons = awful.util.table.join(
                     awful.button({ }, 1, function (c)
                                              if c == client.focus then
                                                  c.minimized = true
                                              else
                                                  -- Without this, the following
                                                  -- :isvisible() makes no sense
                                                  c.minimized = false
                                                  if not c:isvisible() then
                                                      awful.tag.viewonly(c:tags()[1])
                                                  end
                                                  -- This will also un-minimize
                                                  -- the client, if needed
                                                  client.focus = c
                                                  c:raise()
                                              end
                                          end),
					 awful.button({ }, 2, function (c)
									          c:kill()
										  end),
                     awful.button({ }, 3, function ()
                                              if instance then
                                                  instance:hide()
                                                  instance = nil
                                              else
                                                  instance = awful.menu.clients({ width=250 })
                                              end
                                          end),
                     awful.button({ }, 4, function ()
                                              awful.client.focus.byidx(1)
                                              if client.focus then client.focus:raise() end
                                          end),
                     awful.button({ }, 5, function ()
                                              awful.client.focus.byidx(-1)
                                              if client.focus then client.focus:raise() end
                                          end))

for s = 1, screen.count() do
    -- Create a promptbox for each screen
    mypromptbox[s] = awful.widget.prompt()
    -- Create an imagebox widget which will contains an icon indicating which layout we're using.
    -- We need one layoutbox per screen.
    mylayoutbox[s] = awful.widget.layoutbox(s)
    mylayoutbox[s]:buttons(awful.util.table.join(
                           awful.button({ }, 1, function () awful.layout.inc(layouts, 1) end),
                           awful.button({ }, 3, function () awful.layout.inc(layouts, -1) end),
                           awful.button({ }, 4, function () awful.layout.inc(layouts, 1) end),
                           awful.button({ }, 5, function () awful.layout.inc(layouts, -1) end)))
    -- Create a taglist widget
    mytaglist[s] = awful.widget.taglist(s, awful.widget.taglist.filter.all, mytaglist.buttons)

    -- Create a tasklist widget
    mytasklist[s] = awful.widget.tasklist(s, awful.widget.tasklist.filter.currenttags, mytasklist.buttons)

    -- Create the wibox
    mywibox[s] = awful.wibox({ position = "top", screen = s })

    -- Widgets that are aligned to the left
    local left_layout = wibox.layout.fixed.horizontal()
    left_layout:add(mylauncher)
    left_layout:add(mytaglist[s])
    left_layout:add(mypromptbox[s])

    -- Widgets that are aligned to the right
    local right_layout = wibox.layout.fixed.horizontal()
    if s == 1 then right_layout:add(wibox.widget.systray()) end
    right_layout:add(mailwidget)
    right_layout:add(orgwidget)
    right_layout:add(mytextclock)
    right_layout:add(volumewidget)
    right_layout:add(netwidget)
    right_layout:add(batwidget)
    right_layout:add(debugwidget)
    right_layout:add(mylayoutbox[s])


    -- Now bring it all together (with the tasklist in the middle)
    local layout = wibox.layout.align.horizontal()
    layout:set_left(left_layout)
    layout:set_middle(mytasklist[s])
    layout:set_right(right_layout)

    mywibox[s]:set_widget(layout)
end
-- }}}

-- {{{ Mouse bindings
root.buttons(awful.util.table.join(
    awful.button({ }, 3, function () mymainmenu:toggle() end),
    awful.button({ }, 4, awful.tag.viewnext),
    awful.button({ }, 5, awful.tag.viewprev)
))
-- }}}

-- {{{ Key bindings
globalkeys = awful.util.table.join(
    awful.key({ modkey, "Control" }, "Left",   awful.tag.viewprev       ),
    awful.key({ modkey, "Control" }, "Right",  awful.tag.viewnext       ),
    awful.key({ modkey,           }, "Escape", awful.tag.history.restore),

    awful.key({ modkey,           }, "Right",
        function ()
            awful.client.focus.byidx( 1)
            if client.focus then client.focus:raise() end
        end),
    awful.key({ modkey,           }, "Left",
        function ()
            awful.client.focus.byidx(-1)
            if client.focus then client.focus:raise() end
        end),
    awful.key({ modkey,           }, "b", function () mymainmenu:show() end),

    -- Layout manipulation
    awful.key({ modkey, "Shift"   }, "Left", function () awful.client.swap.byidx(  1)    end),
    awful.key({ modkey, "Shift"   }, "Right", function () awful.client.swap.byidx( -1)    end),
    awful.key({ modkey, "Control" }, "j", function () awful.screen.focus_relative( 1) end),
    awful.key({ modkey, "Control" }, "k", function () awful.screen.focus_relative(-1) end),
    awful.key({ modkey,           }, "u", awful.client.urgent.jumpto),
    awful.key({ modkey,           }, "Tab",
        function ()
            awful.client.focus.history.previous()
            if client.focus then
                client.focus:raise()
            end
        end),
	awful.key({ modkey,      }, "m",
						function ()
							 awful.menu.menu_keys.down = { "Down", "s" }
							 awful.menu.menu_keys.up = {"Up", "d"}
							 local cmenu = awful.menu.clients({width=400}, {keygrabber=true, coords={x=0, y=10}})
						end),

    -- Standard program
  awful.key({ modkey },            "y",     function () mypromptbox[mouse.screen]:run() end),
	awful.key({ modkey, "Control", "Shift"}, "#119",function () awful.util.spawn(terminal_cmd .. "/home/dionisos/scripts/dd_poweroff") end),
	awful.key({ modkey, "Control"}, "#119",function () awful.util.spawn(terminal_cmd .. "/home/dionisos/scripts/process_view") end),
	awful.key({modkey, "Control"}, "q",function () awful.util.spawn("xkill") end),
	awful.key({modkey, "Control"}, "e",function () awful.util.spawn("emacsclient -c") end),
  awful.key({modkey, "Control"}, "m",function () awful.util.spawn("quodlibet") end),
	awful.key({modkey, "Control"}, "t",function () awful.util.spawn("empathy") end),
	awful.key({modkey, "Control"}, "i",function () awful.util.spawn("/home/dionisos/installation/obj-instantbird/mozilla/dist/bin/instantbird") end),
	awful.key({modkey, "Control"}, "f",function () awful.util.spawn("firefox") end),
  awful.key({modkey, "Control"}, "g",function () awful.util.spawn("gnome-clocks") end),
	awful.key({modkey, "Control"}, "s",function () awful.util.spawn(terminal_cmd .. "/home/dionisos/scripts/mysuspend") end),
  awful.key({modkey,}, "#75",function () vicious.force({mailwidget}) end),
	awful.key({modkey,}, "#95",function () awful.util.spawn("/home/dionisos/scripts/volume_down 1") os.execute("sleep 0.1") vicious.force({volumewidget}) end),
    awful.key({modkey,}, "#96",function () awful.util.spawn("/home/dionisos/scripts/volume_up 1") os.execute("sleep 0.1") vicious.force({volumewidget})end),
	awful.key({modkey, "Shift"}, "#95",function () awful.util.spawn("/home/dionisos/scripts/volume_down 10") os.execute("sleep 0.1") vicious.force({volumewidget}) end),
    awful.key({modkey, "Shift"}, "#96",function () awful.util.spawn("/home/dionisos/scripts/volume_up 10") os.execute("sleep 0.1") vicious.force({volumewidget})end),
	awful.key({modkey, "Control"}, "#76",function () awful.util.spawn("/home/dionisos/scripts/volume_unmute") os.execute("sleep 0.1") vicious.force({volumewidget}) end),
	awful.key({modkey, }, "#76",function () awful.util.spawn("/home/dionisos/scripts/volume_mute") os.execute("sleep 0.1") vicious.force({volumewidget}) end),
	awful.key({modkey, }, "#74",function () awful.util.spawn("setxkbmap fr") end),
	awful.key({modkey, }, "#73",function () awful.util.spawn("/home/dionisos/scripts/pgm_keyboard/load") end),
    awful.key({ modkey,           }, "#104",function () awful.util.spawn(terminal) end),
	awful.key({}, "#107", function() awful.util.spawn("/home/dionisos/scripts/screenshot") end),
	awful.key({ modkey, }, "#110", function() awful.util.spawn(terminal_cmd .. "genius") end),
    awful.key({ modkey,           }, "Return", function () awful.util.spawn(terminal) end),
    awful.key({ modkey, "Control" }, "r", awesome.restart),
    awful.key({ modkey, "Shift"   }, "q", awesome.quit),

    awful.key({ modkey,           }, "z",     function () awful.tag.incmwfact( 0.05)    end),
    awful.key({ modkey,           }, "j",     function () awful.tag.incmwfact(-0.05)    end),
    awful.key({ modkey, "Shift"   }, "z",     function () awful.tag.incnmaster( 1)      end),
    awful.key({ modkey, "Shift"   }, "j",     function () awful.tag.incnmaster(-1)      end),
    awful.key({ modkey, "Control" }, "z",     function () awful.tag.incncol( 1)         end),
    awful.key({ modkey, "Control" }, "j",     function () awful.tag.incncol(-1)         end),
    awful.key({ modkey,           }, "space", function () awful.layout.inc(layouts,  1) end),
    awful.key({ modkey, "Shift"   }, "space", function () awful.layout.inc(layouts, -1) end),

    awful.key({ modkey,  }, "Down", awful.client.restore),

    -- Prompt
    awful.key({ modkey },            "r",     function () mypromptbox[mouse.screen]:run() end),

    awful.key({ modkey }, "x",
              function ()
                  awful.prompt.run({ prompt = "Run Lua code: " },
                  mypromptbox[mouse.screen].widget,
                  awful.util.eval, nil,
                  awful.util.getdir("cache") .. "/history_eval")
              end),
    -- Menubar
    awful.key({ modkey }, "p", function() menubar.show() end)
)

clientkeys = awful.util.table.join(
    awful.key({ modkey,"Shift"}, "f",      function (c) c.fullscreen = not c.fullscreen  end),
    awful.key({ modkey, }, "q",      function (c) c:kill()                         end),
    awful.key({ modkey, }, "#107",      function(c) awful.util.spawn("/home/dionisos/scripts/screenshot_windows " .. c.window)  end),
    awful.key({ "Control", "Shift"   }, "#61",      function (c) c:kill()                         end),
    awful.key({ modkey, "Control" }, "space",  awful.client.floating.toggle                     ),
    awful.key({ modkey, "Control" }, "Return", function (c) c:swap(awful.client.getmaster()) end),
    -- awful.key({ modkey,           }, "o",      awful.client.movetoscreen                        ),
    -- awful.key({ modkey,           }, "t",      function (c) c.ontop = not c.ontop            end),
    awful.key({ modkey,           }, "Up",
			  function (c)
				 -- The client currently has the input focus, so it cannot be
				 -- minimized, since minimized clients can't have the focus.
				 c.minimized = true
			  end),
    awful.key({ modkey,           }, "e",
			  function (c)
				 c.maximized_horizontal = not c.maximized_horizontal
				 c.maximized_vertical   = not c.maximized_vertical
			  end)
)

-- Compute the maximum number of digit we need, limited to 9
keynumber = 0
for s = 1, screen.count() do
   keynumber = math.min(9, math.max(#tags[s], keynumber))
end

-- Bind all key numbers to tags.
-- Be careful: we use keycodes to make it works on any keyboard layout.
-- This should map on the top row of your keyboard, usually 1 to 9.
for i = 1, keynumber do
    globalkeys = awful.util.table.join(globalkeys,
        awful.key({ modkey }, "#" .. i + 9,
                  function ()
                        local screen = mouse.screen
                        if tags[screen][i] then
                            awful.tag.viewonly(tags[screen][i])
                        end
                  end),
        awful.key({ modkey, "Control" }, "#" .. i + 9,
                  function ()
                      local screen = mouse.screen
                      if tags[screen][i] then
                          awful.tag.viewtoggle(tags[screen][i])
                      end
                  end),
        awful.key({ modkey, "Shift" }, "#" .. i + 9,
                  function ()
                      if client.focus and tags[client.focus.screen][i] then
                          awful.client.movetotag(tags[client.focus.screen][i])
                      end
                  end),
        awful.key({ modkey, "Control", "Shift" }, "#" .. i + 9,
                  function ()
                      if client.focus and tags[client.focus.screen][i] then
                          awful.client.toggletag(tags[client.focus.screen][i])
                      end
                  end))
end

clientbuttons = awful.util.table.join(
    awful.button({ }, 1, function (c) client.focus = c; c:raise() end),
    awful.button({ modkey }, 1, awful.mouse.client.move),
    awful.button({ modkey }, 3, awful.mouse.client.resize))

-- Set keys
root.keys(globalkeys)
-- }}}

-- {{{ Rules
awful.rules.rules = {
    -- All clients will match this rule.
    { rule = { },
      properties = { border_width = beautiful.border_width,
                     border_color = beautiful.border_normal,
                     focus = awful.client.focus.filter,
                     keys = clientkeys,
                     buttons = clientbuttons,
					 size_hints_honor = false} },
    { rule = { class = "MPlayer" },
      properties = { floating = true } },
    { rule = { class = "pinentry" },
      properties = { floating = true } },
    { rule = { class = "gimp" },
      properties = { floating = true } },
    -- Set Firefox to always map on tags number 2 of screen 1.
    -- { rule = { class = "Firefox" },
    --   properties = { tag = tags[1][2] } },
}
-- }}}

-- {{{ Signals
-- Signal function to execute when a new client appears.
client.connect_signal("manage", function (c, startup)
    -- Enable sloppy focus
    c:connect_signal("mouse::enter", function(c)
        if awful.layout.get(c.screen) ~= awful.layout.suit.magnifier
            and awful.client.focus.filter(c) then
            client.focus = c
        end
    end)

    if not startup then
        -- Set the windows at the slave,
        -- i.e. put it at the end of others instead of setting it master.
        -- awful.client.setslave(c)

        -- Put windows in a smart way, only if they does not set an initial position.
        if not c.size_hints.user_position and not c.size_hints.program_position then
            awful.placement.no_overlap(c)
            awful.placement.no_offscreen(c)
        end
    end

    local titlebars_enabled = false
    if titlebars_enabled and (c.type == "normal" or c.type == "dialog") then
        -- Widgets that are aligned to the left
        local left_layout = wibox.layout.fixed.horizontal()
        left_layout:add(awful.titlebar.widget.iconwidget(c))

        -- Widgets that are aligned to the right
        local right_layout = wibox.layout.fixed.horizontal()
        right_layout:add(awful.titlebar.widget.floatingbutton(c))
        right_layout:add(awful.titlebar.widget.maximizedbutton(c))
        right_layout:add(awful.titlebar.widget.stickybutton(c))
        right_layout:add(awful.titlebar.widget.ontopbutton(c))
        right_layout:add(awful.titlebar.widget.closebutton(c))

        -- The title goes in the middle
        local title = awful.titlebar.widget.titlewidget(c)
        title:buttons(awful.util.table.join(
                awful.button({ }, 1, function()
                    client.focus = c
                    c:raise()
                    awful.mouse.client.move(c)
                end),
                awful.button({ }, 3, function()
                    client.focus = c
                    c:raise()
                    awful.mouse.client.resize(c)
                end)
                ))

        -- Now bring it all together
        local layout = wibox.layout.align.horizontal()
        layout:set_left(left_layout)
        layout:set_right(right_layout)
        layout:set_middle(title)

        awful.titlebar(c):set_widget(layout)
    end
end)

client.connect_signal("focus", function(c) c.border_color = beautiful.border_focus end)
client.connect_signal("unfocus", function(c) c.border_color = beautiful.border_normal end)
-- }}}

awful.util.spawn("/home/dionisos/scripts/run_once clipit")
awful.util.spawn("/home/dionisos/scripts/run_once goldendict")
awful.util.spawn("/home/dionisos/scripts/run_once emacs --daemon")
awful.util.spawn("/home/dionisos/scripts/pgm_keyboard/load")
awful.util.spawn("/home/dionisos/scripts/run_on_boot")
