#!/usr/bin/env python
# coding=utf-8
import xlwt
import requests
import re

##获取链接数据
def get_one_page(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/51.0.2704.63 Safari/537.36'}
        response = requests.get(url,headers = headers, timeout = 30)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
        return None
    except RequestException:
        print('访问http发生错误... ')
        return None

book = xlwt.Workbook(encoding='utf-8',style_compression=0)
sheet = book.add_sheet('sheet1',cell_overwrite_ok=True)
url = 'https://www.tesla.com/findus/list/chargers/United+States'
all_html = get_one_page(url)
pattern = re.compile('<address.*?<a.*?href="(.*?)".*?>(.*?)</a>.*?</address>',re.S)
items = re.findall(pattern,all_html)
i = 0
for item in items:
    try:
        
        t_url = "https://www.tesla.com"+item[0]
        t_html = get_one_page(t_url)
        t_pattern = re.compile('href="https://maps.google.com/maps.*?=(.*?)"',re.S)
        t_items = re.findall(t_pattern,t_html)
        print(item[1],t_items[0])
        sheet.write(i,0,item[1])
        sheet.write(i,1,t_items[0])
    except:
        print(i,'_',t_url,'发生异常')
    i+=1
book.save('C:\\Users\\BIGIOZ\\Desktop\\tsl.xls')
print('完成')
#使用正则表达式匹配
