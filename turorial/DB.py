#!/usr/bin/env python  
# -*-coding:UTF-8-*-  
import sys,MySQLdb,traceback  
import MySQLdb.cursors
import time  
import scrapy
from scrapy.utils.project import get_project_settings

class DB:  
    settings = get_project_settings()

    def __init__ (self): 
        self.host   = self.settings['MYSQL_HOST']
        self.user   = self.settings['MYSQL_USER']
        self.passwd = self.settings['MYSQL_PASSWD']
        self.db     = self.settings['MYSQL_DBNAME']
        self.charset= "utf-8"
        self.conn   = None  
  
    def _conn (self):  
        try:  
            self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset="utf8",use_unicode=True, cursorclass=MySQLdb.cursors.DictCursor)  
            return True  
        except MySQLdb.Error,e :  
	    self.logger.error( "Mysql Error %d: %s" % (e.args[0], e.args[1]))
            return False  
  
    def _reConn (self,num = 3,stime = 3): #重试连接总次数为1天,这里根据实际情况自己设置,如果服务器宕机1天都没发现就......  
        _number = 0  
        _status = True  
        while _status and _number <= num:  
            try:  
                self.conn.ping()       #cping 校验连接是否异常  
                _status = False  
            except:  
                if self._conn()==True: #重新连接,成功退出  
                    _status = False  
                    break  
                _number +=1  
                time.sleep(stime)      #连接不成功,休眠3秒钟,继续循环，知道成功或重试次数结束  
  
    def select (self, sql = ''):  
        try:  
            print self._reConn()  
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)  
            self.cursor.execute (sql)  
            result = self.cursor.fetchall()  
            self.cursor.close ()  
            return result  
        except MySQLdb.Error,e:  
            #print "Error %d: %s" % (e.args[0], e.args[1])  
            return False  
  
    def select_limit (self, sql ='',offset = 0, length = 20):  
        sql = '%s limit %d , %d ;' % (sql, offset, length)  
        return self.select(sql)  
  
    def query (self, sql = ''):  
        try:  
            self._reConn()  
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)  
            self.cursor.execute ("set names utf8") #utf8 字符集  
            result = self.cursor.execute (sql)  
            self.conn.commit()  
            self.cursor.close ()  
            return (True,result)  
        except MySQLdb.Error, e:  
            return False  
  
    def close (self):  
        self.conn.close()  


