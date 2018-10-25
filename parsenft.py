#!/usr/bin/python3
# Enrich nftables output with OUI manufacturer names.
# Meant to be used like this:
# me@box:$ sudo /usr/sbin/nft list ruleset | parsenft.py | sort
# Amazon Technolo 24:4c:e3:xx:xx:xx 192.168.2.88                             6d22h32m52s 
# Apple, Inc.     8c:85:90:yy:yy:yy 192.168.2.83                             6d22h32m52s 
# Apple, Inc.     8c:85:90:yy:yy:yy 2000:1000:1000:1000:aaaa:bbbb:cccc:dddd  6d22h34m3s  
#
# Addresses need to be captured by nftables.
# Sample configuration to be added into /etc/nftables.conf (debian / ubuntu)
# table netdev raw {
#         set inv41h {
#                 type ether_addr . ipv4_addr; timeout 7d;
#         }
#
#         set inv61h {
#                 type ether_addr . ipv6_addr; timeout 7d;
#         }
#
#         chain ingress {
#                 type filter hook ingress device eth0 priority 0;
#                 set add ether saddr . ip saddr @inv41h counter
#                 set add ether saddr . ip6 saddr @inv61h counter
#         }
# }

import os
import re
import sqlite3
import sys
from getpass import getuser

USER_HOME = "~" + getuser()
OUI_FILE_STORE = os.path.join(os.path.expanduser(USER_HOME), ".oui-cache")

def getoui(hwa):
    match = re.search(r'(\w\w:\w\w:\w\w):\w\w:\w\w:\w\w', hwa)
    if match:
        oui = match.group(1).replace(':', '').upper()
    else:
        oui = ''

    return oui

conn = sqlite3.connect(OUI_FILE_STORE)
c = conn.cursor()

fit = iter(sys.stdin)
while True:
    sname = stype = sto = elems = 'undef'

    try:
        line = next(fit).rstrip()
        match = re.search(r'\s*set (\w+) {', line)
        if match:
            sname = match.group(1)
        else:
            continue

        line = next(fit).rstrip()
        match = re.search(r'\s*type ([\s\w.]+)', line)
        if match:
            stype = match.group(1)
        else:
            continue

        line = next(fit).rstrip()
        match = re.search(r'\s*timeout ([\w]+)', line)
        if match:
            sto = match.group(1)
        else:
            continue

        line = next(fit).rstrip()
        match = re.search(r'\s*elements = {([^}]+)}', line)
        if match:
            elems = match.group(1)
        else:
            continue

        # print('set(%(sname)s) type(%(stype)s) timeout(%(sto)s)' % locals())

        smac = sipv4 = stl = 'undef'
        for elem in elems.split(","):
            match = re.search(r'\s*([\dabcdef:]+) \. ([\dabcdef.:]+) expires (\w+)', elem)
            if match:
                smac = match.group(1)
                sinet = match.group(2)
                stl = match.group(3)
                oui = getoui(smac)
                sqlres = c.execute('SELECT company FROM oui WHERE mac =?', (oui,))

                try:
                    comp = sqlres.fetchone()[0]
                except:
                    comp = 'oui lookup fault'

                comp = comp[:15]
                sinet = sinet[:40]
                #print('%(comp)s mac(%(smac)s) inet(%(sinet)s) timeout(%(stl)s)' % locals())
                print('{0:<15} {1:<10} {2:<40} {3:<12}'.format(comp[:15], smac, sinet[:40], stl))

            else:
                continue

    except StopIteration:
        break

