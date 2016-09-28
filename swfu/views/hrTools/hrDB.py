from swfu import app
from flask import Flask, request, render_template, url_for, abort, redirect, send_from_directory
import pymysql, sys, json, chardet, datetime, os, csv, codecs, time


class HrDb():
    def __init__(self):
        self.conn = pymysql.connect(host='dev.corp.kindin.com.cn',
                                    port=3306,
                                    user='root',
                                    passwd='123456',
                                    db='zbox',
                                    charset='utf8')
        self.cur = self.conn.cursor()

    def run(self, sqlCmd):
        result = self.cur.execute(sqlCmd)
        self.conn.commit()
        return result

    def addHoliday(self, holidayName, holidayDate):
        sqlCmd = 'INSERT into hr_holiday (name, date) VALUES("%s","%s");'%(holidayName, holidayDate)
        self.run(sqlCmd)

    def deleteHoliday(self, holidayID):
        sqlCmd = "delete from hr_holiday where id = %s"%holidayID
        #print sqlCmd
        self.run(sqlCmd)
            
    
    def checkHoliday(self):
        sqlCmd = "select * from hr_holiday order by ID desc"
        self.cur.execute(sqlCmd)
        sourceDatas = self.cur.fetchall()

        arry = []
        for row in sourceDatas:
            tmpArry = []
            for element in row:
                tmpArry.append(str(element))
            arry.append(tmpArry)
        return arry

    def checkUserInfo(self):
        sqlCmd = "select id, name, department, hireDate, leaveDate, overTime from hr_userInfo where leaveDate is Null order by ID asc"
        self.cur.execute(sqlCmd)
        sourceDatas = self.cur.fetchall()

        arry = []
        for row in sourceDatas:
            tmpArry = []
            for element in row:
                tmpArry.append(str(element))
            arry.append(tmpArry)
        return arry
    
    def __exit__(self):
        self.cur.close()
        self.conn.close()