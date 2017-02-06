#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhaotongkp#163.com'
import psutil
import time, datetime
import json
import pymysql
from multiprocessing import cpu_count as multicpu
import platform
import common.config
import functions

machinePlatform = platform.platform ( )

# get machine system infomation
def machineSystemInfomations () :
    bootStart = time.strftime ( "%Y-%m-%d %H:%M:%S", time.localtime ( psutil.boot_time ( ) ) )
    alarmValue = 50
    time.sleep ( 0.5 )
    cpuStatus = 1
    memStatus = 1
    diskStatus = 1
    totalStatus = 1
    cpuUsage = psutil.cpu_percent ( interval = 0 )
    time.sleep ( 0.01 )
    ram = int ( psutil.virtual_memory ( ).total / (1024 * 1024) )
    ramUsagePercent = psutil.virtual_memory ( ).percent
    ramUsed = psutil.virtual_memory ( ).used
    diskUsage = psutil.disk_usage ( '/' )
    if cpuUsage >= alarmValue :
        cpuStatus = 0
    if ramUsagePercent >= alarmValue :
        memStatus = 0
    if diskUsage.percent >= alarmValue :
        diskUsage = 0
    if cpuStatus == 0 or ramUsagePercent == 0 :
        totalStatus = 0
    return {
        "platform" : machinePlatform, \
        "cpuCoreNum" : multicpu ( ), \
        "cpuUsage" : cpuUsage, \
        "memorySize" : psutil._TOTAL_PHYMEM / 1024 / 1024, \
        "memoryTotal" : ram / 1024 / 1024, \
        "memoryUsage" : ramUsed / 1024 / 1024, \
        "memoryUsagePercent" : ramUsagePercent, \
        "diskTotal" : diskUsage.total / 1024 / 1024, \
        "diskUsage" : diskUsage.used / 1024 / 1024, \
        "diskUsagePercent" : diskUsage.percent, \
        "cpuStatus" : cpuStatus, \
        "memoryStatus" : memStatus, \
        "diskStatus" : diskStatus, \
        "totalStatus" : totalStatus, \
        "updateTime" : datetime.datetime.now ( ).strftime ( "%Y-%m-%d %H:%M:%S" )
    }

def processInfo():
    return psutil.process_iter()

#
def errorNum (redisObj, ip, type, process) :
    key = ''
    result = redisObj.get ( key )
    if result is None :
        times = 1
    else :
        times = int ( result ) + 1
    ttl = redisObj.ttl ( key )
    redisObj.set ( key, times )
    if int ( times ) == 1 :
        redisObj.expire ( key, 1800 )
    else :
        redisObj.expire ( key, ttl )
    return times


# get all checked master servers form redis
def checkMasterServers (redisObj, key) :
    servers = redisObj.smembers ( key )
    if len ( servers ) :
        return servers
    else :
        return [ ]


# set job of master servers in redis
def setMasterServersJob (redisObj, ip) :
    key = 'checkmaster:set:job:servers'
    redisObj.sadd ( key, ip )


# left push data to redis
def dataLeftPushtoRedis (redisObj, key, dataItems) :
    print key
    print datetime
    return redisObj.lpush ( key, dataItems )


# hash data to redis
def dataHashtoRedis (redisObj, key, dataItems) :
    if len ( dataItems ) :
        for k, v in dataItems.iteritems ( ) :
            redisObj.hset ( key, k, v )
