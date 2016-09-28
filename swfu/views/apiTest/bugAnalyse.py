#coding = "utf-8"

from swfu import app
from flask import Flask, request, render_template, url_for
from db import *

import sys, json, os, codecs, time, csv, os

reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/bugAnalyse', methods=['POST', 'GET'])
def bugAnalyse():
    htmlName = 'bugAnalyse.html'
    resultTitle = []
    optins = bugAnalyseDict
    for optin in optins:
        optins[optin]["selected"] = False

    #接受请求
    if request.method == 'POST':
        apiStatus = True
        apiName = request.form['st']
        #已经选择
        if (apiName in optins.keys()) and (apiName != "select") : #是否在范围内
            optins[apiName]["selected"] = True

            if len(optins[apiName]["par"]) != 0: #有参数
                for pars in optins[apiName]["par"]:
                    if pars not in request.form:
                        apiStatus = False
                        break
                    else:
                        if not request.form[pars]:
                            apiStatus = False
                            break
                        else:
                            resultTitle, result = eval(apiName)()

            else: #无参数
                resultTitle, result = eval(apiName)()#执行对应名称的程序
        else:
            optins["select"]["selected"] = True
            apiStatus = False
    #无请求
    else:
        optins["select"]["selected"] = True
        apiStatus = False
        selected = "select"

    #判断状态，选择对应模板
    if apiStatus:
        if apiName == "dayStatus" or apiName == "delayBugReopen" or apiName == "statusAndPriByPersion" or apiName == "active" or apiName =="fixedToday":
            return render_template(htmlName,
                       apiStatus = apiStatus,
                       resultResolve = result,
                       resultTitle = resultTitle,
                       pageTitle = "景典 Bug 分析",
                       optins = optins)
        else:
            return render_template(htmlName,
                       apiStatus = apiStatus,
                       resultAct = result[0],
                       resultResolve = result[1][0:8],
                       resultClose = result[1][9:],
                       resultTitle = resultTitle,
                       pageTitle = "景典 Bug 分析",
                       optins = optins)
    else:
        return render_template(htmlName,
                               apiStatus = apiStatus,
                               pageTitle = "景典 Bug 分析",
                               optins = optins)



# 激活 bug 分析
def statusAndPriByPersion(platform = '0'):
     
    dbName = "zentao"
    als = analyseBugs(dbName)
    
    platform = request.form['platform']
    
    if platform == "1":
        platform = "iOS"
    elif platform == "2":
        platform = "Android"
    elif platform == "3":
        platform = "Web"
    else:
        platform = "All"
    
    
    rows, title = als.newGetActiveBug(platform)
    
    tmpTotleRowByPerson = ['合计','ALL']
    
    lenForRow = len(rows[0])
    
    print lenForRow
    
    
    for i in xrange(2, lenForRow):
        tmpTotleByPerson = 0
        for row in rows:
            print title[i], row[i]
            tmpTotleByPerson += row[i]
        tmpTotleRowByPerson.append( str(tmpTotleByPerson))
    rows.append(tmpTotleRowByPerson)
    return title, rows

            
# Bug 每日状态
def dayStatus():
    tmpResultArry = []
    dbName = "zentao"
    title = ["日期", "每日新增", "每日解决", "每日关闭"]

    sqlCmdOpened = 'select DATE_FORMAT(zt_bug.openedDate,"%Y-%m-%d"), \
    count(DATE_FORMAT(zt_bug.openedDate,"%Y-%m-%d")) from zt_bug GROUP BY \
    DATE_FORMAT(zt_bug.openedDate,"%Y-%m-%d");'
    rowsOpened = dbConnect(dbName).run(sqlCmdOpened)

    tmpResultArrys = rowsOpened

    sqlCmdResolved = 'select DATE_FORMAT(zt_bug.resolvedDate ,"%Y-%m-%d"), \
    count(DATE_FORMAT(zt_bug.resolvedDate,"%Y-%m-%d")) from zt_bug GROUP BY \
    DATE_FORMAT(zt_bug.resolvedDate,"%Y-%m-%d");'
    rowsResolved = dbConnect(dbName).run(sqlCmdResolved)


    for rowResolved in rowsResolved:
        for tmpResultArry in tmpResultArrys:
            if tmpResultArry[0] == rowResolved[0]:
                tmpResultArry.append(rowResolved[1])
                break
        else:
            tmpResultArrys.append([rowResolved[0],'0',rowResolved[1]])
    for tmpResultArry in tmpResultArrys:
        if len(tmpResultArry) < 3:
            tmpResultArry.append("0")


    sqlCmdClosed = 'select DATE_FORMAT(zt_bug.closedDate ,"%Y-%m-%d"), \
    count(DATE_FORMAT(zt_bug.closedDate,"%Y-%m-%d")) from zt_bug GROUP BY \
    DATE_FORMAT(zt_bug.closedDate,"%Y-%m-%d");'
    rowsClosed = dbConnect(dbName).run(sqlCmdClosed)

    for rowClosed in rowsClosed:
        for tmpResultArry in tmpResultArrys:
            if tmpResultArry[0] == rowClosed[0]:
                tmpResultArry.append(rowClosed[1])
                break
        else:
            tmpResultArrys.append([rowClosed[0], '0', '0',rowClosed[1]])

    for tmpResultArry in tmpResultArrys:
        if len(tmpResultArry) < 4:
            tmpResultArry.append("0")
    tmpResultArrys.sort()

    return title, tmpResultArrys[-20:]

#激活 bug
def delayBugReopen():
    dbName = "zentao"
    tableName = "zt_bug"
    title = ['Bug号', '项目', '标题', '状态', '解决方案', '最后修改日期' ,'解决者']
    sqlCmd = "select id, product, title, STATUS, resolution, resolvedBy \
    from %s where status='closed' and resolution = 'postponed';"%tableName

    result = dbConnect(dbName).run(sqlCmd)
    
    if result:
    
        result.append(['<a id="modal-324819" href="#modal-container-324819" role="button" class="btn" data-toggle="modal">\
                        <button type="button" class="btn btn-primary" data-dismiss="modal">\
                            激活所有 bug\
                        </button>\
                    </a>\
                    <div class="modal fade" id="modal-container-324819" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">\
                        <div class="modal-dialog">\
                            <div class="modal-content">\
                                <div class="modal-header">\
                                    <h4 class="modal-title" id="myModalLabel">\
                                        是否激活所有延期处理的 bug？\
                                    </h4>\
                                </div>\
                                <div class="modal-body">\
                                    请问：是要激活所有等待延期处理的 bug 吗？\
                                </div>\
                                <div class="modal-footer">\
                                <button type="button" class="btn btn-default" data-dismiss="modal">\
                                    关闭\
                                </button>\
                                <a href =%s >\
                                <button type="button" class="btn btn-primary">\
                                    激活\
                                </button>\
                                </a>\
                            </div>\
                        </div>\
                    </div>\
                </div>'%url_for("bugResult"),'','','','',''])

        return title, result
    else:
        return ["错误"], [["未找到延期处理的 bug"]]


#激活 active 分析
def active():
    dbName = "zentao"
    als = analyseBugs(dbName)
    rows, title = als.newGetActiveBugDetail()
    
    currentDate = _getCurrentDate()
    fileName = "activeBugList(%s).csv" %currentDate
    
    tmpsRows = []
    index = 1
    for row in rows:
        row = (index,) + row
        index += 1
        tmpsRows.append(row)
    
    tmpsRows.append(['<a id="modal-324819" href="%s" role="button" class="btn" data-toggle="modal" download="activeBugList.csv">\
                        <button type="button" class="btn btn-primary" data-dismiss="modal">\
                            点击下载\
                        </button>\
                    </a>'%(url_for("fileDownload", fileName = fileName)),'','','','','',''])
    
    csvFileCreater(title, tmpsRows, fileName)
    
    return title, tmpsRows

def csvFileCreater(title, rows, fileName):
    downloadDocumentPath = os.path.join(app.static_folder, "anal")
    os.system("rm -f %s" %downloadDocumentPath)
    
    f = file(os.path.join(downloadDocumentPath, fileName), 'wb')
    f.write(codecs.BOM_UTF8) 
    writer = csv.writer(f)  
    writer.writerow(title)
    
    for row in rows[:-1]:
        writer.writerow(row)    
 
@app.route('/bugResult', methods=['POST', 'GET'])
def bugResult():
    dbName = "zentao"
    tableName = "zt_bug"
    
    sqlCmdForBugId = "select id, product from %s where status='closed' and \
    resolution = 'postponed';"%tableName
    bugIDs = dbConnect(dbName).run(sqlCmdForBugId)
    
    sqlCmd = "update %s set status ='active', resolution = '', \
    assignedTo = closedBy, resolvedBy = '', closedby = '' where status='closed'\
     and resolution = 'postponed';" %tableName

    result = dbConnect(dbName).edit(sqlCmd)
    if result == 1:
        for bug in bugIDs:
            sqlCmdForComment = "insert into `zentao`.`zt_action` \
                    ( `action`, `product`, `objectType`, `actor`, `date`, `read`, `project`, `comment`, `objectID`) \
                    values ( 'commented', %s, 'bug', 'sunbo', NOW(), '1', '1', '<p>系统自动激活此 bug。</p>', '%s');"%(bug[1],bug[0])
            bugCommentResult = dbConnect(dbName).run(sqlCmdForComment)
        return render_template("bugReopenResult.html",
                                resultTitle = "激活延期成功",
                                pageTitle = "激活延期 bug")
    else:
        return render_template("bugReopenResult.html",
                                resultTitle = "激活延期失败，请从新激活",
                                pageTitle = "激活延期 bug")

def fixedToday():
    dbName = "zentao"
    als = analyseBugs(dbName)
    rows, title = als.newGetFixedTodayBugDetail()
    
    currentDate = time.strftime('%Y%m%d',time.localtime(time.time()))
    
    
    tmpsRows = []
    index = 1
    for row in rows:
        row = (index,) + row
        index += 1
        tmpsRows.append(row)
  
    tmpsRows.append(['<a id="modal-324819" href="%s" role="button" class="btn" data-toggle="modal" download="resolvedBugListToday.csv">\
                               <button type="button" class="btn btn-primary" data-dismiss="modal">\
                                   点击下载\
                               </button>\
                           </a>'%(url_for("fileDownload", fileName = "resolvedBugListToday.csv")),'','','','','','',''])

    csvFileCreater(title, tmpsRows, "resolvedBugListToday.csv")
        
    return title, tmpsRows    
                                
def _getCurrentDate():
    return time.strftime('%Y%m%d',time.localtime(time.time()))

bugAnalyseDict = {'select' :
                    {'text' : "请选择",
                     'selected' : True,
                     'par': {}},
                    'statusAndPriByPersion' :
                    {'text' : "激活Bug综合分析",
                    'selected' : False,
                    'par' : {"platform":"平台"}},
                    'dayStatus' :
                    {'text' : "分日趋势表",
                    'selected' : False,
                    'par' : {}},
                    'active' :
                    {'text' : "激活 Bug 摘要",
                    'selected' : False,
                    'par' : {}},
                    'fixedToday' :
                    {'text' : "今天解决问题摘要",
                    'selected' : False,
                    'par' : {}},
                    'delayBugReopen':
                    {'text' : "重新打开延期Bug",
                    'selected' : False,
                    'par' : {}}
                }


