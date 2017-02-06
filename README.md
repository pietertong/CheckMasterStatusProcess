# CheckMasterStatusProcess
Run this script,please exec cmd:
#########################################################
EG:
	python  main.py -i "192.168.62.129" -s 10 -w 0

#########################################################
Python Check Status of Master ,Status of Process
#########################################################
REDIS:

127.0.0.1:6379> sadd checkmaster:set:process:192.168.62.129 'nginx'

127.0.0.1:6379> sadd set:servers 192.168.62.129 192.168.62.130
