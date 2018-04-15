#!/usr/bin/python3

from urllib.request import urlopen
from getpass import getuser

import sys
import time
import os
import re
import sqlite3

USER_HOME = "~" + getuser()
OUI_FILE_STORE = os.path.join(os.path.expanduser(USER_HOME), ".oui-cache")
IEEE_URL = "http://standards-oui.ieee.org/oui/oui.txt"

class OuiRec(object):

    def __init__(self, cursor):
        self.cursor = cursor
        self.reset()

    def reset(self):
        self.oui = ''
        self.company = ''
        self.addr1 = ''
        self.addr2 = ''
        self.country = ''

    def try_insert(self):
        if self.oui != '' and self.company != '' and self.addr1 != '' and self.addr2 != '' and self.country != '':
            self.cursor.execute('INSERT INTO oui VALUES (''?'', ''?'', ''?'', ''?'', ''?'')', (self.oui, self.company, self.addr1, self.addr2, self.country))
            self.reset()

def update_cache():

    conn = sqlite3.connect(OUI_FILE_STORE)
    c = conn.cursor()

    try:
        c.execute('''DROP TABLE oui''')
    except:
        pass

    c.execute('''CREATE TABLE oui(mac text, company text, addr1 text, addr2 text, country text)''')

    u = urlopen(IEEE_URL)
    file_size = float(u.headers['content-length'])
    print('Downloading: %s Bytes: %s' % (IEEE_URL, file_size))

    file_size_dl = 0
    block_sz = 8192
    rem = bytes("", 'utf-8')

    ouirec = OuiRec(c)
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        buffer = rem + buffer
        file_size_dl += len(buffer)
        bs = str(buffer, 'utf-8')
        lines = bs.split('\n')
        rem = bytes(lines[-1], 'utf-8')

        maclines = iter(lines[:-1])
        while True:
            if ouirec.company == '':
                macline = next(maclines, None)
                if macline == None:
                    break

                if macline == '':
                    ouirec.reset()
                    continue

                macline = macline.rstrip()
                if '(base 16)' not in macline:
                    ouirec.reset()
                    continue

                mac, company = macline.split('(base 16)');
                ouirec.oui = mac.strip()
                ouirec.company = company.strip()

            if ouirec.addr1 == '':
                macline = next(maclines, None)
                if macline == None:
                    break

                if macline == '':
                    ouirec.reset()
                    continue

                macline = macline.strip()
                if not macline:
                    ouirec.reset()
                    continue

                ouirec.addr1 = macline

            if ouirec.addr2 == '':
                macline = next(maclines, None)
                if macline == None:
                    break

                if macline == '':
                    ouirec.reset()
                    continue

                macline = macline.strip()
                if not macline:
                    ouirec.reset()
                    continue

                ouirec.addr2 = macline

            if ouirec.country == '':
                macline = next(maclines, None)
                if macline == None:
                    break

                if macline == '':
                    ouirec.reset()
                    continue

                macline = macline.strip()
                if not macline:
                    ouirec.reset()
                    continue

                ouirec.country = macline

            ouirec.try_insert()

        ouirec.try_insert()

        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        sys.stdout.write('\r' + status,)

    conn.commit()
    conn.close()
    print(">>> Done")

update_cache()
