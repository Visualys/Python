#!/usr/bin/env python

import os
ip = os.popen('curl ifconfig.me -s').readline()
print(ip)
#f = open('/home/pi/MyDocs/box_cyb/externalip.txt','w')
#f.write(ip+'\n')
#f.close()
#os.system('sudo rclone copy /home/pi/MyDocs/box_cyb/externalip.txt box:/cyb')