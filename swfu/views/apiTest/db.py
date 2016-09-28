import pymysql, sys

reload(sys)
sys.setdefaultencoding("utf-8")

class dbConnect():
    def __init__(self, dbName):
        if dbName:
            self.conn = pymysql.connect(host='dev.corp.kindin.com.cn',
                                        port=3306,
                                        user='root',
                                        passwd='123456',
                                        db=dbName,
                                        charset='utf8')
            self.cur = self.conn.cursor()

    def run(self, sqlCmd):
        arry = []

        self.cur.execute(sqlCmd)
        rows = self.cur.fetchall()

        for row in rows:
            tmpArry = []
            for element in row:
                print element
                tmpArry.append(str(element))
            arry.append(tmpArry)
        return arry

    def edit(self, sqlCmd):
        result = self.cur.execute(sqlCmd)
        self.conn.commit()
        return result

    def __exit__(self):
        self.cur.close()
        self.conn.close()

class analyseBugs():
    def __init__(self, dbName):
        self.dbConnect = pymysql.connect("dev.corp.kindin.com.cn",
                                         "root",
                                         "123456",
                                         dbName,
                                         charset='utf8')
        self.dbCursor = self.dbConnect.cursor()
        self.solvePersonNames = []
        self.assignedPersonNames = []
        self.bugSolutions = []
        self.bugPrioritys = []
        self.allData = self._newGetAllData()

    def getAllColumn(self, dbName):
        data = []
        sqlCmd = "select column_name from COLUMNS where table_schema = 'zentao' and table_name='%s';"%dbName
        self.dbCursor.execute(sqlCmd)
        tmpDatas = self.dbCursor.fetchall()
        for tmpData in tmpDatas:
            data.append(tmpData[0])
        return data

    def _getAllDataByProduct(self, product, dataType):
        sqlCmd = "select distinct %s from zt_bug where product = %s;" %(dataType, product)
        tmpDatas = []
        self.dbCursor.execute(sqlCmd)
        sourceDatas = self.dbCursor.fetchall()
        for sourceData in sourceDatas:
            if sourceData[0] == 'closed' or sourceData[0] == "":
                continue
            tmpDatas.append(sourceData[0])
        return tmpDatas

    def getAllSolvePersonNamesByProduct(self, product):
        self.solvePersonNames = self._getAllDataByProduct(product, "resolvedBy")
        return self.solvePersonNames

    def getAllAssignedPersonNamesByProduct(self, product):
        self.assignedPersonNames = self._getAllDataByProduct(product, "assignedTo")
        return self.assignedPersonNames

    def getAllBugSolutions(self):
        if not self.bugSolutions:
            self.bugSolutions = self._getAllDataByProduct("1", "resolution")
        return self.bugSolutions

    def getAllBugPrioritys(self):
        if not self.bugPrioritys:
            self.bugPrioritys = self._getAllDataByProduct("1", "pri")
        return self.bugPrioritys

    def getAllBugStatus(self):
        return ['active', 'resolved', 'Closed']

    def getBugCountByPersonAndStatus(self, alsType, name, bugStatus, bugSolution, product):
        if alsType:
            sqlCmd = "select count(*) from zt_bug where product = %s and assignedTo = '%s' and status = '%s' and deleted = '0';" %(product, name, bugStatus)

        else:
            sqlCmd = "select count(*) from zt_bug where product = %s and  resolvedBy = '%s' and status = '%s' and deleted = '0' and resolution = '%s';" %(product, name, bugStatus, bugSolution)
        self.dbCursor.execute(sqlCmd)
        sourceDatas = self.dbCursor.fetchall()
        return sourceDatas


    def getBugCountByPriAndStatus(self, alsType, pri, bugStatus, bugSolution, product):
        if alsType:
            sqlCmd = "select count(*) from zt_bug where product = %s and pri = '%s' and status = '%s' and deleted = '0';" %(product, pri, bugStatus)

        else:
            sqlCmd = "select count(*) from zt_bug where product = %s and  pri = '%s' and status = '%s' and deleted = '0' and resolution = '%s';" %(product, pri, bugStatus, bugSolution)
        self.dbCursor.execute(sqlCmd)
        sourceDatas = self.dbCursor.fetchall()
        return sourceDatas

    def _newGetAllData(self):
        sqlCmd = "select id, product, project, pri, status, openedBy, assignedTo, resolvedBy, resolution from zt_bug where deleted = '0'"
        self.dbCursor.execute(sqlCmd)
        sourceDatas = self.dbCursor.fetchall()
        return sourceDatas

    def _newGetAllPri(self):
        return [0,1,2,3,4]

    def _newGetAllBugStatusAndSolutions(self):
        statusAndSolutionDict =[
            {
                'status':'active',
                'Solutions':[""]
            },{
                'status':'resolved',
                'Solutions':["notrepro",
                             "bydesign",
                             "notabug",
                             "duplicate",
                             "external",
                             "willnotfix",
                             "storychange",
                             "tostory"]
            },{
                'status':'closed',
                'Solutions':["fixed",
                             "notrepro",
                             "bydesign",
                             "notabug",
                             "duplicate",
                             "external",
                             "willnotfix",
                             "storychange",
                             "postponed",
                             "tostory"]
            }]
        return statusAndSolutionDict

    def _newGetAllPerson(self, status, platfrom):
        person = []
        data = self.allData
        if status == "All":            
            for d in data:
                if platfrom == "0":
                    if d[5] not in person:
                        person.append(d[5])
                    if d[6] not in person:
                        person.append(d[6])
                else:
                    if d[5] not in person and d[1] == platfrom:
                        person.append(d[5])
                    if d[6] not in person and d[1] == platfrom:
                        person.append(d[6])                    
        else:
            for d in data:
                if d[4] == "active":
                    if platfrom == "0":
                        if d[6] not in person:
                            person.append(d[6])
                    else:
                        if d[6] not in person and str(d[1]) == platfrom:
                            
                            person.append(d[6])
        return person

    def newGetActiveBug(self, platform):
        
        if platform == "iOS":
            platform = "1"
        elif platform == "Android":
            platform = "2"
        elif platform == "Web":
            platform = "3"
        else:
            platform = "0"
        
        person = self._newGetAllPerson("active", platform)
        statusDict = self._newGetAllBugStatusAndSolutions()
        pris = self._newGetAllPri()
        data = self.allData
        detailDict = []

        statusCol = "active"
        title = ['状态', '优先级'] + person + ["合计"]
        
        for pri in pris:
            detailDictRow = []
            for p in person:
                tmpCount = 0
                for d in data:
                    if platform == "0":
                        if d[6] == p and d[3] == pri and d[4] == statusCol:
                            tmpCount += 1
                    else:
                        if d[6] == p and d[3] == pri and d[4] == statusCol and str(d[1]) == platform:
                            tmpCount += 1                       
                detailDictRow.append(tmpCount)
                count = 0
                for item in detailDictRow:
                    count += int(item)
                detailDictRowForResult = [statusCol, str(pri)] + detailDictRow + [count]
            detailDict.append(detailDictRowForResult)
        return detailDict, title

    def newGetActiveBugDetail(self):
        sqlCmd = 'select id as "Bug编号", \
        product as "平台", \
        status as "状态", \
        title as "标题", \
        assignedTo as "分配给", \
        lastEditedDate ,\
        pri as "优先级" from zt_bug \
        where \
    	status = "active" \
    	and assignedTo != "youjinA"\
    	and deleted = "0" \
    	and (product < "4" or product >="8") \
    	and pri <= "4" \
    	and pri != "" \
        ORDER BY assignedTo;'
        
        self.dbCursor.execute(sqlCmd)
        sourceDatas = self.dbCursor.fetchall()
        
        title = ['No.','Bug ID', '平台', '状态', '标题', '分配给', '最后修改日期', '优先级']
        return sourceDatas, title        
    
    def newGetFixedTodayBugDetail(self):
        sqlCmd = 'select id as "Bug编号", \
	                product as "平台", \
	                status as "状态", \
	                title as "标题", \
	                resolvedBy as "解决者", \
	                pri as "优先级", \
	                resolution as "解决方案" \
	                from \
	                    zt_bug \
	                where \
	                    status = "resolved" \
	                    and assignedTo != "youjinA" \
                        and deleted = "0" \
	                    and product < "4" \
                            and DATE_FORMAT(resolvedDate,"%Y-%m-%d") = DATE_FORMAT(NOW(),"%Y-%m-%d")\
                            ORDER BY resolvedBy ;'
        self.dbCursor.execute(sqlCmd)
        sourceDatas = self.dbCursor.fetchall()
                
        title = ["No.", 'Bug编号', '平台', '状态', '标题', '解决者', '优先级', '解决方案']
        return sourceDatas, title           
    
    
    def __exit__(self):
        self.dbConnect.close()
