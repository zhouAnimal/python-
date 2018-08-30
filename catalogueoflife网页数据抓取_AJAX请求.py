#根据ajax请求，抓取页面上的数据
import requests
from requests.exceptions import RequestException
import json,xlwt,xlrd
import datetime as d
import os
from xlutils.copy import copy

fileSavePath = "C:\\Users\\BIGIOZ\\Desktop\\data\\"
txtName = fileSavePath+d.datetime.now().strftime("%Y%m%d%H%M%S")+"_log.txt"
f = open(txtName,'w')

##获取链接数据
def get_one_page(url):
    try: 
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('访问http发生错误... ')
        return None
    
##获取目标数组    
def getItems(html):
    hjson = json.loads(html)
    datalist = hjson['items']
    return datalist

##保存为excel,追加写入
def json2Excel(datas,excelName,rowNum):
    isFileExist = os.path.exists(excelName)
    if not isFileExist:
        rowNum = 1
        book = xlwt.Workbook() # 创建excel文件
        sheet = book.add_sheet('Sheet1',cell_overwrite_ok=True) # 添加一个sheet页
        title = ['Name']
        for i in range(len(title)): # 循环列
            sheet.write(0,i,title[i]) # 将title数组中的字段写入到0行i列中
        book.save(excelName)#保存excel
    rb = xlrd.open_workbook(excelName)
    w = copy(rb)
    dsheet = w.get_sheet(0)
    rowNumAdd = rowNum
    for data in datas:
        dsheet.write(rowNumAdd, 0, data['name'])
        rowNumAdd += 1
    w.save(excelName)#保存excel
    logMsg = d.datetime.now().strftime("%Y.%m.%d %H:%M:%S")+"在"+excelName+" 中共写入数据："+str((rowNumAdd-rowNum))+"条,从第"+str(rowNum)+"开始写。\n"
    print(logMsg)
    f.write(logMsg)
    return rowNumAdd

#获取指定“xx”数据，PpName为空则返回全部数据
def get_Point_data(url,pName):
    html = get_one_page(url)
    items = getItems(html)
    #返回全部数据
    if pName.strip()=="":
        for item in items:
            yield{
                'id':item['id'],
                'name':item['name'],
                'rank':item['rank'],
                'type':item['type'],
                'numChildren':item['numChildren'],
                'parentId':item['parentId'], 
            }
        return
    #返回指定数据
    for item in items:
        if item['name']==pName:
            yield{
                'id':item['id'],
                'name':item['name'],
                'rank':item['rank'],
                'type':item['type'],
                'numChildren':item['numChildren'],
                'parentId':item['parentId'],               
            }
        
        
            

##url拼接            
def get_Urls(items,beginStr,endStr):
     for item in items:
            yield{
                'url':beginStr+str(item['id'])+endStr,
                'name':item['name'],
            }
            
    
beginStr = 'http://www.catalogueoflife.org/annual-checklist/2017/browse/tree/fetch/taxa?id=' 
endStr = '&hash=0c6c280363f5cf79ba3edb18597401ed&start=0'
params = [
    ['http://www.catalogueoflife.org/annual-checklist/2017/browse/tree/fetch/taxa?id=33521288&hash=0c6c280363f5cf79ba3edb18597401ed&start=0','Abisara.xls'],
         ]
count = 1
for param in params:#门
    phylumData = get_Point_data(param[0],'Arthropoda')
    phylumUrls = get_Urls(phylumData,beginStr,endStr)
    for phylumUrl in phylumUrls: #纲
        ClassData = get_Point_data(phylumUrl['url'],'Insecta')
        ClassUrls = get_Urls(ClassData,beginStr,endStr)
        for ClassUrl in ClassUrls:#目
            OrderData = get_Point_data(ClassUrl['url'],'Lepidoptera')
            OrderUrls = get_Urls(OrderData,beginStr,endStr)
            for OrderUrl in OrderUrls:#超科
                superfamilyData = get_Point_data(OrderUrl['url'],'Papilionoidea')
                superfamilyUrls = get_Urls(superfamilyData,beginStr,endStr)
                rowNum = 1
                for superfamilyUrl in superfamilyUrls:#科
                    familyData = get_Point_data(superfamilyUrl['url'],'')
                    familyUrls = get_Urls(familyData,beginStr,endStr)
                    for familyUrl in familyUrls:#属
                        xlsName = fileSavePath+familyUrl['name']+'.xls'#文件保存路径
                        genusData = get_Point_data(familyUrl['url'],'')
                        genusUrls = get_Urls(genusData,beginStr,endStr)
                        for genusUrl in genusUrls:#种
                            genusData = get_Point_data(genusUrl['url'],'')
                            rowNum = json2Excel(genusData,xlsName,rowNum)
print('finish...')
f.close()