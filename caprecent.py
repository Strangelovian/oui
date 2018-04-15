#!/usr/bin/python3

import fileinput
import os
import re
import sqlite3
from getpass import getuser

USER_HOME = "~" + getuser()
OUI_FILE_STORE = os.path.join(os.path.expanduser(USER_HOME), ".oui-cache")

def getoui(hwa):
    match = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w:(\w\w:\w\w:\w\w):\w\w:\w\w:\w\w:\w\w:\w\w', hwa)
    if match:
        oui = match.group(1).replace(':', '').upper()
    else:
        oui = ''

    return oui

def getmac(hwa):
    match = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w:(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w):\w\w:\w\w', hwa)
    if match:
        mac = match.group(1).replace(':', '').upper()
    else:
        mac = ''

    return mac

conn = sqlite3.connect(OUI_FILE_STORE)
c = conn.cursor()

for line in fileinput.input():
    match = re.search(r'.*MAC=([^ ]*) .*SRC=([^ ]*) .*', line)
    if match:
         hwa = match.group(1)
         ip = match.group(2)
         oui = getoui(hwa)
         mac = getmac(hwa)

         sqlres = c.execute('SELECT company FROM oui WHERE mac =?', (oui,))

         try:
             comp = sqlres.fetchone()[0]
         except:
             comp = 'vafenculo'

         print('%(comp)s %(mac)s %(ip)s' % locals())
    else:
         pass
