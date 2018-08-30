#! /usr/bin/env python
#coding=utf-8
#将抓取下来的catalogueoflife数据整理成可导入excel的格式
 
# pyexcel_xls 以 OrderedDict 结构处理数据
from collections import OrderedDict
from pyexcel_xls import get_data
from pyexcel_xls import save_data
import os
import json,xlwt,xlrd
from xlutils.copy import copy

def get_files(rootdir,fileType):
    list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    paths =[]
    for i in range(0,len(list)):
        path = os.path.join(rootdir,list[i])
        if os.path.isfile(path) and path.endswith(fileType):
            paths.append(path)
    return paths
            
class FooError(ValueError):
    pass
    

def read_xls_file(path):
    xls_data = get_data(path)
    xlsDatas = {}
    for sheet_n in xls_data.keys():#逐个读取工作表中的内容
        datas = xls_data[sheet_n]
        xlsDatas[sheet_n] = datas
    return xlsDatas

#rankIDPart：
def get_sql(i,path,records,rankIDPart):
    if i>1000: #判断科是否越界
        raise FooError('设置的科ID范围不够了')
    
    xlsFile = path.split("\\")[-1]
    ke = xlsFile.split(".")[0]
    familyDatas = {}#定义科 idct
    #生成科_主键
    if ke in familyDatas:
        pass
    else:
        familyDatas[ke] = i
    genusDatas = {} #定义属dict
    for (key,value) in records.items():
        j = 0#属累加
        k = 0#种累加
        for v in value:
            if(v[0].find(" ") != -1):#是否可拆分为属、种
                k=k+1
                rank = v[0].split(" ")
                if rank[0] in genusDatas:#生成属ID
                    pass
                else:
                    j=j+1
                    k=1
                    genusId = familyDatas[ke]*1000+j
                    if genusId > (familyDatas[ke]+1)*1000:#判断属是否越界
                        raise FooError('设置的属ID范围不够了')
                    genusDatas[rank[0]] = genusId
                speciesId = genusId * 10000 + k
                if speciesId > (genusId+1)*10000:#判断属是否越界
                    raise FooError('设置的种ID范围不够了')
                yield{
                    '科ID':familyDatas[ke],
                    '科':ke,
                    '科parentID':'',
                    '属ID':genusDatas[rank[0]],
                    '属':rank[0],
                    '属parentID':i,
                    '种Id':speciesId,
                    '种':v[0],
                    '种Parent':genusDatas[rank[0]],  
                    
                }
    ##print(rankDatas)
                    
##保存为excel
def save_to_excel(datas,excelName,rowNum):
    print('数据写入excel...')
    isFileExist = os.path.exists(excelName)
    if not isFileExist:
        rowNum = 1
        book = xlwt.Workbook() # 创建excel文件
        sheet = book.add_sheet('Sheet1',cell_overwrite_ok=True) # 添加一个sheet页
        title = ['ID','name','parentID','rank']
        for i in range(len(title)): # 循环列
            sheet.write(0,i,title[i]) # 将title数组中的字段写入到0行i列中
        book.save(excelName)#保存excel
    rb = xlrd.open_workbook(excelName)
    w = copy(rb)
    dsheet = w.get_sheet(0)
    rowNumAdd = rowNum
    for data in datas:
        dsheet.write(rowNumAdd, 0, data['科ID'])
        dsheet.write(rowNumAdd, 1, data['科'])
        dsheet.write(rowNumAdd, 2, data['科parentID'])
        dsheet.write(rowNumAdd, 3, 'family')
        rowNumAdd += 1
        dsheet.write(rowNumAdd, 0, data['属ID'])
        dsheet.write(rowNumAdd, 1, data['属'])
        dsheet.write(rowNumAdd, 2, data['属parentID'])
        dsheet.write(rowNumAdd, 3, 'genus')
        rowNumAdd += 1
        dsheet.write(rowNumAdd, 0, data['种Id'])
        dsheet.write(rowNumAdd, 1, data['种'])
        dsheet.write(rowNumAdd, 2, data['种Parent'])
        dsheet.write(rowNumAdd, 3, 'species')
        rowNumAdd += 1
    w.save(excelName)#保存excel    
    return rowNumAdd

rankID = 10000
if __name__ == '__main__':
    rootdir = 'E:\数据整理\catalogueoflife_data'
    excelPath = rootdir + '\\result\\'+'result.xls'
    paths = get_files(rootdir,".xls")#读取文件夹下的所有xls文件
    i = 0
    rowNum = 1
    for path in paths:
        i = i+1
        print("正在解析第",i,"个文件...",path)
        rankID = rankID*i
        datas = read_xls_file(path)
        li = get_sql(i,path,datas,rankID)
        rowNum = save_to_excel(li,excelPath,rowNum)
    print("执行完成...")

    
    
