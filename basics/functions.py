#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'pietertong'

import common.config
import redis
import pymysql
import requests
import json
import logging
import datetime, time
import sys, os


# init redis connection
def initRedis (dbName = 'localhost') :
    dbHost = common.config.nosqlServerConfig [ dbName ] [ 'host' ] ;
    dbPort = common.config.nosqlServerConfig [ dbName ] [ 'port' ] ;
    dbUser = common.config.nosqlServerConfig [ dbName ] [ 'user' ] ;
    dbPassword = common.config.nosqlServerConfig [ dbName ] [ 'password' ] ;
    dbSelected = common.config.nosqlServerConfig [ dbName ] [ 'selectedDb' ] ;
    try :
        redisObj = redis.StrictRedis ( host = dbHost, port = dbPort, db = dbSelected, password = dbPassword ) ;
        return redisObj
    except :
        logRuntime ( 'main', initRuntime ( ), "连接数据库失败" )
        exit ( "Exception E ,Error." )


# logging runtime some data
def logRuntime (type, path, logInformations) :
    formatter = logging.Formatter ( '%(asctime)s %(message)s' )
    loggerNormal = logging.getLogger ( type )
    hdlr = logging.FileHandler ( path )
    hdlr.setFormatter ( formatter )
    loggerNormal.addHandler ( hdlr )
    loggerNormal.warning ( logInformations )


# init runtime path
def initRuntime (type = 'errors') :
    path = sys.path [ 0 ]
    if os.path.isdir ( path ) :
        runtimePath = path
    elif os.path.isfile ( path ) :
        runtimePath = os.path.dirname ( path )
    else :
        runtimePath = '..'
    return runtimePath + '/runtime/log/' + type + '_' + datetime.datetime.now ( ).strftime ( '%Y%m%d' ) + '.log'


