#coding = "utf-8"
from flask import Flask, request, render_template, url_for, abort, redirect, send_from_directory
from testAPI import app
import pymysql, sys, json, chardet, datetime, os, csv, codecs, time
from db import *
import checking

reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/i/<fileName>')
def imageDownload(fileName = ""):
    if fileName != "":
        downloadDocumentPath = os.path.join(app.static_folder, "image")
        return send_from_directory(downloadDocumentPath, fileName)
    else:
        return abort(404)

@app.route('/v/<fileName>')
def videoDownload(fileName = ""):
    if fileName != "":
        downloadDocumentPath = os.path.join(app.static_folder, "video")
        return send_from_directory(downloadDocumentPath, fileName)
    else:
        return abort(404)
    
@app.route('/f/<fileName>')
def fileDownload(fileName = ""):
    if fileName != "":
        downloadDocumentPath = os.path.join(app.static_folder, "anal")
        return send_from_directory(downloadDocumentPath, fileName, as_attachment=True)
    else:
        return abort(404)

#首页
@app.route('/')
def index():
    return render_template('index.html',pageTitle = "API Testing")

@app.route('/apiTest', methods=['POST', 'GET'])
def apiTest():
    htmlName = 'apiTest.html'
    resultTitle = []
    optins = funcDict
    for optin in optins:
        optins[optin]["selected"] = False

    if request.method == 'POST':
        apiStatus = True
        apiName = request.form['st']

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
                resultTitle, result = eval(apiName)()
        else:
            optins["select"]["selected"] = True
            apiStatus = False

    else:
        optins["select"]["selected"] = True
        apiStatus = False
        selected = "select"

    if apiStatus:
        return render_template(htmlName,
                               apiStatus = apiStatus,
                               result = result,
                               resultTitle = resultTitle,
                               pageTitle = "API 测试系统",
                               optins = optins)
    else:
        return render_template(htmlName,
                               apiStatus = apiStatus,
                              pageTitle = "API 测试系统",
                               optins = optins)

#景点排序
def scenic_sort():

    dbName = "loveu"
    cmd = "call test_SORT_FUNCTION();"

    result = dbConnect(dbName).run(cmd)
    title = ['mycnt',
             'code',
             '景点名称',
             'sorts',
             '销量',
             '收藏',
             '评论',
             '分享',
             '访问量',
             '星级',
             '时间']
    return title, result

#城市周边
def scenic_around_city():

    dbName = "loveu"
    city = request.form['city']

    cmd = "call test_AROUND_CITY('%s')" %city

    tmpTitle = ['scenic_spot_code',
                #'product_pic',
                #'product_l_pic',
                'address',
                'scenic_spot_name',
                'sales_price',
                'market_price',
                'give_integral',
                'level',
                'city_name']
    result = dbConnect(dbName).run(cmd)

    return tmpTitle, result

#GPS周边
def scenic_around_gps():
    dbName = "loveu"
    longitude = request.form['longitude']
    latitude = request.form['latitude']

    if ((float(longitude) <= -180.0) or (float(longitude) >= 180.0) or (float(latitude) <= -90.0) or (float(latitude) >= 90.0) ):
        return [u"错误"], [[u"此地点在火星，恕不受理。"]]

    cmd = "call test_AROUND_GPS('%s','%s')" %(latitude, longitude)

    tmpTitle = ['scenic_spot_code',
                'level',
                'city_id',
                'city_name',
                #'product_pic',
                'address',
                'position_x',
                'position_y',
                'scenic_name',
                'sales_price',
                'market_price',
                'distance',
                'comment_amount']
    result = dbConnect(dbName).run(cmd)

    return tmpTitle, result

#门票修改
def changeTicket(sid=None):
    dbName = "loveu"
    tableName = 'product_dtl_tbl'
    scenicName = request.form['scenicName']

    rowCmd = 'SELECT product_id, \
                    sub_product_id, \
                    sub_product_name, \
                    sell_qty, \
                    marketable_qty \
                FROM \
                    product_dtl_tbl \
                WHERE \
                    sub_product_name \
                LIKE "%%%s%%"' %scenicName

    title = ['ID', 'SID', '景点名称', '销售数量', '总计数量', '操作']

    result = dbConnect(dbName).run(rowCmd)
    if result:
        for r in result:
            r.append('<a href="%s"><button type="button" class="btn btn-sm btn-success">修改</button></a>'%(url_for("changeTicketDetile", content = "%s|%s"%(r[0],r[1]))))
    else:
        result = [[u"未搜索到自采酒店"]]
        title = [u"错误"]
    return title, result

#修改门票详细信息
@app.route('/apiTest/<content>',methods=['POST', 'GET'])
def changeTicketDetile(content=None):
    dbName = "loveu"
    pid, sid = content.split("|")
    rowCmd = 'SELECT product_id, sub_product_id, sub_product_name, sell_qty, marketable_qty  FROM product_dtl_tbl WHERE sub_product_id = "%s" and product_id = "%s"' %(sid, pid)

    result = dbConnect(dbName).run(rowCmd)

    return render_template("editDetail.html",
                           result = result,
                           pageTitle = "景点余票修改")

@app.route('/apiTest/ticketResult',methods=['POST', 'GET'])
def changeTicketResult():
    dbName = "loveu"
    if request.method == 'POST':
        pid = request.form['pid']
        sid = request.form['sid']
        count = request.form['count']
        sqlCmdUpdate = "update product_dtl_tbl set sell_qty = '%s' where \
         sub_product_id = '%s' and product_id = '%s';" %(count,sid,pid)
        result = dbConnect(dbName).edit(sqlCmdUpdate)
        return render_template("result.html",
                                pname = request.form['pname'],
                                pageTitle = "余票修改成功")
    else:
        return abort(404)
#测试
def tmp():
    dbName = "loveu"
    tableName = 'comment_info_tbl'

    titleCmd = "select column_name from COLUMNS where table_schema = '%s' \
    and table_name='%s';"%(dbName, tableName)
    rowCmd = "select * from %s limit 10;" %tableName

    title = dbConnect("information_schema").run(titleCmd)
    tmpTitle = []
    for t in title:
        for e in t:
            tmpTitle.append(e)

    title = tmpTitle
    result = dbConnect(dbName).run(rowCmd)

    return title, result

@app.route('/bugAnalyse', methods=['POST', 'GET'])
#======================================================================
#bug 分析主入口
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

#Bug分析
funcDict = {'select' :
            {'text' : "请选择",
             'selected' : True,
             'par': {}},
            'scenic_sort' :
            {'text' : "景点排序列表",
            'selected' : False,
            'par' : {}},
            'tmp' :
            {'text' : "测试接口",
            'selected' : False,
            'par' : {}},
            'changeTicket' :
            {'text' : "门票修改",
            'selected' : False,
            'par' : {"scenicName":"景点名称"}},
            'changeBookingDate' :
            {'text' : "订单出行时间修改",
            'selected' : False,
            'par' : {"orderID":"订单号"}},
            'scenic_around_gps' :
            {'text' : "GPS周边景点",
            'selected' : False,
            'par' : {"longitude":"经度",
                    "latitude":"纬度"}},
            'scenic_around_city':
            {'text' : '城市周边景点',
            'selected' : False,
            'par' : {"city":"所在城市"}}}

