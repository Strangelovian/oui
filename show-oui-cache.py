#!/usr/bin/python3

import fileinput
import re
import sqlite3

conn = sqlite3.connect('oui.db')
c = conn.cursor()
sqlres = c.execute('SELECT * FROM oui')

for rec in sqlres:
    print(rec)
