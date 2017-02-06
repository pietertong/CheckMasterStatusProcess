__author__ = 'pietertong'

sqlServerConfig = {
    "localhost" : {
        "type" : 'mysql',
        "host" : 'localhost',
        "port" : 3306,
        "password" : '123456',
        "user" : 'root',
        "dbName" : 'checkmaster'
    }
}

nosqlServerConfig = {
    "localhost" : {
        "type" : 'redis',
        "host" : 'localhost',
        "port" : '6379',
        "user" : 'localhost',
        "password" : '123456',
        "selectedDb" : 0
    }
}
