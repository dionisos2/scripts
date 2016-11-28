#!/usr/bin/python

## change YOUR* pseudo-variables according to your needs

import imaplib
# import commands
import subprocess

login_proc = subprocess.Popen(["/home/dionisos/scripts/.psw", "-u", "gmail"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
password_proc = subprocess.Popen(["/home/dionisos/scripts/.psw", "-p", "gmail"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

login = login_proc.stdout.read().decode("utf-8")
password = password_proc.stdout.read().decode("utf-8")

#default imap port is 993, change otherwise
M=imaplib.IMAP4_SSL("imap.gmail.com", 993)
M.login(login, password)

status, counts = M.status("Inbox","(MESSAGES UNSEEN)")

unread = counts[0].split()[4][:-1]

print(int(unread))

M.logout()
