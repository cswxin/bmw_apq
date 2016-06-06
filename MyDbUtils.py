#encoding:utf-8
from django.db import connection
import MySQLdb
from releaseinfo import *

def cursor():
    cursor = None
    con = None
    if DATABASE_ENGINE == 'sqlite3':
        cursor = connection.cursor()
    elif DATABASE_ENGINE == 'django.db.backends.mysql':
        con = MySQLdb.connect(user=DATABASE_USER, db=DATABASE_NAME, passwd=DATABASE_PASSWORD, host=DATABASE_HOST, charset='utf8')
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
    return cursor, con
