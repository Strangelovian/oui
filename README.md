A MAC address is 6 bytes long.
The first 3 bytes are made from the so called [Organizationally Unique Identifier](https://en.wikipedia.org/wiki/Organizationally_unique_identifier).
OUI can be resolved from a database maintained by the IEEE [here](http://standards-oui.ieee.org/oui/oui.txt)

`caprecent.py` takes iptables log lines redirected from standard input.

`parsenft.py` enrich nftable output with OUI manufacturer names

`update-oui-cache.py` needs to be run once, to save the IEEE OUI mapping in a sqllite database stored in ~/.oui-cache. It's using about 2 mega bytes of disk space.

Example iptables syslog entry:
```bash session
me@home:~$ sudo grep RECENT_F /var/log/syslog.1
Apr 20 21:51:40 home_router kernel: [1082100.910875] RECENT_FW: IN=lan_if OUT=wan_if MAC=00:01:23:45:67:89:00:24:e4:ba:da:dd:08:00 SRC=172.19.18.20 DST=1.1.1.1 LEN=76 TOS=0x00 PREC=0x00 TTL=63 ID=31113 DF PROTO=UDP SPT=37368 DPT=53 LEN=56
```

The output piped into caprecent.py:
```bash session
me@home:~$ sudo grep RECENT_F /var/log/syslog.1 | caprecent.py | sort | uniq
Ubiquity Networks Inc. 0024E4BADADD 172.19.18.20
```

Bonus: iptables rules to generate daily syslog entries for local hosts interacting with the local router (ip4tables-save format)
```
*filter
:log_recent_in - [0:0]
:log_recent_fw - [0:0]

-A INPUT -i lan_if -m recent --name day_in ! --rcheck --seconds 86400 -j log_recent_in
-A FORWARD -i lan_if -m recent --name day_fw ! --rcheck --seconds 86400 -j log_recent_fw

-A log_recent_in -j LOG --log-prefix "RECENT_IN: " --log-level 6
-A log_recent_in -m recent --name day_in --set
-A log_recent_fw -j LOG --log-prefix "RECENT_FW: " --log-level 6
-A log_recent_fw -m recent --name day_fw --set
```
