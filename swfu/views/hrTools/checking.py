from swfu import app
from flask import Flask, request, render_template, url_for, abort, redirect, send_from_directory
import pymysql, sys, json, chardet, datetime, os, csv, codecs, time
from hrDB import *

reload(sys)
sys.setdefaultencoding("utf-8")

#HR 工具主入口
@app.route('/HrChecking')
@app.route('/HrChecking?page=<pageId>', methods=['POST', 'GET'])
def HrChecking(pageId = ''):
	if pageId != 'view' and pageId != 'cfg' and pageId != '':
		pageId = ''
	return render_template("checkingIndex.html",
                           pageTitle = "人事考勤统计系统",
                           pageId = pageId
                           )

#节假日管理入口
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
    holidayTitle = [u'ID', u'节假日名称', u'日期', u'类型', u'操作']

    return render_template("holiday.html",
                           pageTitle = "节假日修改",
                           holidays = holidaysRows,
                           titles = holidayTitle
                           )    
                           
#用户管理入口
@app.route('/HrChecking/user')
def userInfo():
    userInfoRows = HrDb().checkUserInfo()
    userInfoTitle = [u'ID', u'姓名', u'部门', u'入职日期', u'离职日期', u'加班时间', u'操作']
    return render_template("userInfo.html",
                        pageTitle = "用户修改",
                        titles = userInfoTitle,
                        users = userInfoRows
                       )
                    
#添加用户
@app.route('/HrChecking/user/add', methods=['POST', 'GET'])
def userAdd():
    return "userAdd"

#删除用户
@app.route('/HrChecking/user/edit', methods=['POST', 'GET'])
def userEdit():
    return "userEdit"
  