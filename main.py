#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhaotongkp#163.com'
import basics.functions
import basics.status
import json
import time, datetime
import psutil
from optparse import OptionParser as optionParse

argvParams = optionParse ( )
argvParams.add_option ( "-i", "--ip", dest = "ip", type = "string", default = True, help = "ip address" )
argvParams.add_option ( "-s", "--seconds", dest = "seconds", default = 10, help = "how often to run this script" )
argvParams.add_option ( "-w", "--warning", dest = "warning", default = 1, help = "is there a warning?" )
(options, args) = argvParams.parse_args ( )
# init redis
redisInitObj = basics.functions.initRedis ( )
# print redisInitObj
errorWarningTimes = 10
needSynchronousKey = "checkmaster:sync:chronous:key"
redisInitObj.set ( needSynchronousKey, errorWarningTimes )


# defined main function
def main () :
    errorMessageHtml = ''
    processList = { }
    newProcessList = { }
    title = "%s has gone ,result is Excetpions" % options.ip

    if options.ip :
        checkMasterServers = basics.status.checkMasterServers ( redisInitObj, 'checkmaster:set:servers' )
        if len ( checkMasterServers ) > 0 :
            if options.ip in checkMasterServers :
                basics.status.setMasterServersJob ( redisInitObj, options.ip )
                masterServerSystemInfomations = basics.status.machineSystemInfomations ( )
                if masterServerSystemInfomations [ 'cpuStatus' ] == 0 :
                    times = basics.status.errorNum ( redisInitObj, options.ip, 'cpu', '' )
                    if int ( times ) == errorWarningTimes :
                        errorMessageHtml = 'cpu'
                processRedisKey = 'checkmaster:set:process:%s' % options.ip
                processData = list ( basics.status.checkMasterServers ( redisInitObj, processRedisKey ) ) ;
                basics.status.dataHashtoRedis ( redisInitObj, 'checkmaster:hash:server:sysinfo',
                                                { options.ip : json.dumps ( masterServerSystemInfomations ) } )
                if len ( processData ) != 0 :
                    for serverProcess in basics.status.processInfo ( ) :
                        for process in processData :
                            alarmValue = 50
                            cpuStatus = 1
                            memStatus = 1
                            diskStatus = 1
                            totalStatus = 1
                            try :
                                if serverProcess.name ( ) == process :
                                    processCpuPercent = serverProcess.cpu_percent ( interval = 0 )
                                    time.sleep ( 0.1 )
                                    processName = serverProcess.name ( )
                                    processMemPercent = serverProcess.memory_percent ( )
                                    processMemUsage = int (serverProcess.memory_info ( ).rss ) / 1024 / 1024
                                    if processCpuPercent >= alarmValue :
                                        cpuStatus = 0
                                        times = basics.status.errorNum ( redisInitObj, options.ip, 'cpu', process )
                                        if int ( times ) == errorWarningTimes :
                                            errorMessageHtml += 'cpu'
                                    if processMemPercent >= alarmValue :
                                        memStatus = 0
                                        times = basics.status.errorNum ( redisInitObj, options.ip, 'memory', process )
                                        if int ( times ) == errorWarningTimes :
                                            errorMessageHtml += 'memory'
                                    if cpuStatus == 0 or memStatus == 0 :
                                        totalStatus = 0
                                    appendData = {
                                        'pid' : serverProcess.pid,
                                        'process' : process,
                                        'cpu_usage' : processCpuPercent,
                                        'memory_usage_percent' : round ( processMemPercent, 2 ),
                                        'cpu_status' : cpuStatus,
                                        'memory_status' : memStatus,
                                        'total_status' : totalStatus,
                                        'memory_usage' : processMemUsage,
                                        'memory_size' : masterServerSystemInfomations [ 'memorySize' ],
                                        'update_time' : datetime.datetime.now ( ).strftime ( "%Y-%m-%d %H:%M:%S" )
                                    }
                                    if processList.has_key ( processName ) :
                                        processList [ process ].append ( appendData )
                                    else :
                                        processList [ process ] = [ appendData ]
                            except psutil.NoSuchProcess :
                                continue
                            except Exception, e :
                                continue
                #
                if len ( processList ) != 0 :
                    for indexList, valueList in processList.iteritems ( ) :
                        alarmValue = 50
                        cpuStatus = 1
                        memStatus = 1
                        diskStatus = 1
                        totalStatus = 1
                        totalCpuUsage = 0
                        totalMemUsage = 0
                        totalMemUsagPercent = 0
                        for indexItem, valueItem in enumerate ( valueList ) :
                            totalCpuUsage += valueItem [ 'cpu_usage' ]
                            totalMemUsage += valueItem [ 'memory_usage' ]
                            totalMemUsagPercent += valueItem [ 'memory_usage_percent' ]
                        if processCpuPercent >= alarmValue :
                            cpuStatus = 0
                        if processMemPercent >= alarmValue :
                            memStatus = 0
                        if cpuStatus == 0 or memStatus == 0 :
                            totalStatus = 0

                        totalProcessInfoes = {
                            'pid' : 0,
                            'process' : indexList,
                            'cpu_usage' : round ( totalCpuUsage, 2 ),
                            'memory_usage_percent' : round ( totalMemUsagPercent, 2 ),
                            'memory_usage' : totalMemUsage,
                            'cpu_status' : cpuStatus,
                            'memory_status' : memStatus,
                            'total_status' : totalStatus,
                            'memory_size' : masterServerSystemInfomations [ 'memorySize' ],
                            'update_time' : datetime.datetime.now ( ).strftime ( "%Y-%m-%d %H:%M:%S" )
                        }
                        newProcessList [ indexList ] = {
                            'total' : totalProcessInfoes,
                            'list' : processList [ indexList ]
                        }
                        for index, value in newProcessList.iteritems ( ) :
                            basics.status.dataHashtoRedis ( redisInitObj, 'checkmaster:hash:server:processes',
                                                            { index : json.dumps ( value ) } )
    if errorMessageHtml is not '' and int ( options.warning ) is 1 :
        basics.status.dataLeftPushtoRedis ( redisInitObj, 'checkmaster:warning:list',
                                            json.dumps ( { 'ip' : options.ip, 'warning_msg' : errorMessageHtml } ) )


# python main.py 192.168.62.129 10 1,then exec there
if __name__ == '__main__' :
    # while True:
    main ( )
    # time.sleep(int(options.seconds))
