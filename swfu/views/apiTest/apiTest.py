#coding = "utf-8"
from flask import Flask, request, render_template, url_for, abort, redirect, send_from_directory
from swfu import app
import pymysql, sys, json, chardet, datetime, os, csv, codecs, time

from db import *

reload(sys)
sys.setdefaultencoding("utf-8")

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

