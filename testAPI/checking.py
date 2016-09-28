from testAPI import app
from flask import Flask, request, render_template, url_for, abort, redirect, send_from_directory
import pymysql, sys, json, chardet, datetime, os, csv, codecs, time
from db import *

reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/HrChecking')
def HrChecking():
    return render_template("checkingIndex.html",
                           pageTitle = "人事考勤统计系统")

@app.route('/HrChecking/holiday', methods=['POST', 'GET'])
@app.route('/HrChecking/holiday?deleteID=<holidayID>', methods=['POST', 'GET'])
def holiday(holidayID = ''):
    
    if request.method == 'POST' and holidayID == '':
        holidayName = request.form['holidayName']
        holidayDate = request.form['holidayDate']

        HrDb().addHoliday(holidayName, holidayDate)
    elif holidayID != '':
        HrDb().deleteHoliday(holidayID)
    
    holidaysRows = HrDb().checkHoliday()
    holidayTitle = [u'ID', u'节假日名称', u'日期', u'操作']

    return render_template("holiday.html",
                           pageTitle = "节假日修改",
                           holidays = holidaysRows,
                           titles = holidayTitle
                           )    
@app.route('/HrChecking/user')
def userInfo():
    userInfoRows = HrDb().checkUserInfo()
    userInfoTitle = [u'ID', u'姓名', u'部门', u'入职日期', u'离职日期', u'加班时间', u'操作']
    return render_template("userInfo.html",
                        pageTitle = "用户修改",
                        titles = userInfoTitle,
                        users = userInfoRows
                       )
@app.route('/HrChecking/user/add', methods=['POST', 'GET'])
def userAdd():
    return "userAdd"
    
@app.route('/HrChecking/user/edit', methods=['POST', 'GET'])
def userEdit():
    return "userEdit"
    
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