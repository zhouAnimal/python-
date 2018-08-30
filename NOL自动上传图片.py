#NOL自动化测试-
import yaml,time,os
import math
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

def get_files(rootdir,fileType):#fileType不区分大小写
    list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    paths =[]
    for i in range(0,len(list)):
        path = os.path.join(rootdir,list[i])
        if os.path.isfile(path) and path.upper().endswith(fileType.upper()):
            paths.append(path)
    return paths
            
class FooError(ValueError):
    pass

#对于图片量大的数据，分成多组 
#paths 数组
#size 每次上传图片的个数
def get_part_data(paths,size):
    results = {}
    length = 0
    print('图片数量：',len(paths))
    if len(paths)> size:
        length = math.ceil(len(paths)/size)
    for i in range(length):
        if i == length-1:
            yield{
                'begin':i*size,
                'end':len(paths)
            }
        else:
            yield{
                'begin':i*size,
                'end':(i+1)*size
            }


#鉴定阶元
def selected_rank(driver,rankName):
    driver.find_element_by_id('select2-idrank-container').click()
    time.sleep(1)
    driver.find_element_by_class_name('select2-search__field').send_keys(rankName)
    time.sleep(1)
    driver.find_element_by_xpath("//ul[@id='select2-idrank-results']/li[contains(text(),'"+rankName+"')]").click()
    
#鉴定状态
def selected_identify(driver,identifyName):
    driver.find_element_by_id('select2-isid-container').click()
    WebDriverWait(driver, 10).until(lambda x: x.find_element_by_class_name('select2-search__field')).send_keys(identifyName)
    time.sleep(1)
    driver.find_element_by_xpath("//ul[@id='select2-isid-results']/li[contains(text(),'"+identifyName+"')]").click()
    

#类群    
def selected_groups(driver,groupName):
    driver.find_element_by_id('select2-groups-container').click()
    time.sleep(1)
    driver.find_element_by_class_name('select2-search__field').send_keys(groupName)
    time.sleep(1)
    driver.find_element_by_xpath("//ul[@id='select2-groups-results']/li[contains(text(),'"+groupName+"')]").click()

#登录
def login(driver,username,password):
    loginBtn  = driver.find_element_by_id('loginIcon')##弹出登录窗口
    loginBtn.click()##单击事件
    # 等待时长10秒，默认0.5秒询问一次
    WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id("token"))
    print("请输入验证码：")
    # 手动输入验证码
    token_code = input()
    driver.find_element_by_id("token").send_keys(token_code)#输入验证码
    driver.find_element_by_id("username").clear()
    driver.find_element_by_id('username').send_keys(username)##输入用户名
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id('password').send_keys(password)##输入密码
    driver.find_element_by_class_name('btn-primary').click()

#打开添加观测记录页面
def open_new_windows(driver,js):
    driver.execute_script(js)
    now_handle = driver.current_window_handle
    all_handles = driver.window_handles
    for handle in all_handles:
        print(handle)
    driver.switch_to_window(all_handles[-1])#切换句柄
    return driver

#填入的关键词没有找到具体位置，重新再操作5次
def re_Text_Value(driver,i,keyWord,position):
    print(keyWord,position)
    try:
        WebDriverWait(driver, 15).until(lambda x: x.find_element_by_id('tipinput')).clear()
        driver.find_element_by_id('tipinput').send_keys(keyWord) #2.地理位置关键词
        time.sleep(2)
        driver.find_element_by_xpath("//div[contains(text(),'"+position+"')]").click()#3.指定一个地理位置
    except:
        print('第',i,'次重置')
        if i >= 5:
            raise FooError("位置无法定位...请检查")
        else:
            i+=1
            re_Text_Value(driver,i,keyWord,position)

       
    
#添加观测记录
def add_new_view(driver,rdate,keyWord,position,datasets,comments):
    print('添加观测记录...',rdate,keyWord,position,datasets,comments)
    driver.find_element_by_id('rdate').send_keys(rdate)##1.记录日期
    re_Text_Value(driver,0,keyWord,position)
    driver.find_element_by_id('select2-dsid-container').click()
    time.sleep(2)
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//ul/li[contains(text(),'"+datasets+"')]")).click()#4.数据集
    driver.find_element_by_id('comments').send_keys(comments)#观测笔记
    driver.find_element_by_xpath("//button/span[contains(text(),'下一步')]").click()#下一步

def enter_add_new_video_page(driver):
    WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//*[@id='fh5co-board']/div[1]/div/div[2]/a/span")).click()
    #driver.find_element_by_xpath("//div[@class='item']/div[@class='animate-box']/a").click()
    #driver.find_element_by_xpath("//*[@id='fh5co-board']/div[1]/div/div[2]/a/span").click()
    
    
#批量新建影像记录
def add_new_video(driver,rootdir,LD,ZWM,FLBZ,PSZ,LQ,JDJY,JDZT):
    size = 2
    ycSize = 10 #图片数量达到ycSize时，移除页面上的图片
    imageCount = 1#图片上传执行次数
    imagefile = driver.find_element_by_id("input-fa")
    paths = get_files(rootdir,".jpg")#读取文件夹下的所有JPG文件
    indexs = get_part_data(paths,size)
    for i in indexs:
        begin = int(i['begin'])
        end = int(i['end'])
        print('图片索引位置：',begin,end,paths[begin:end])
        if imageCount == 1:
            imageCount+=1
            driver.find_element_by_id('species').clear()
            driver.find_element_by_id('species').send_keys(LD)#拉丁名
            driver.find_element_by_id('speciesCn').clear()
            driver.find_element_by_id('speciesCn').send_keys(ZWM)#中文名
            driver.find_element_by_id('idnote').clear()
            driver.find_element_by_id('idnote').send_keys(FLBZ)#分类备注
            driver.find_element_by_id('photographer').clear()
            driver.find_element_by_id('photographer').send_keys(PSZ)#拍摄者
            selected_groups(driver,LQ)#类群
            selected_rank(driver,JDJY)#选择鉴定阶元
            selected_identify(driver,JDZT)#鉴定状态
            for path in paths[begin:end]:
                imagefile.send_keys(path)#上传图片
            try:
                WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath("//span[contains(text(),'上传')]")).click()
                WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath("/html/body/div[1]/div[2]/section[2]/div/div[1]/div/div[2]/div/div[contains(text(),'完成')]"))
            except:
                print('可能发生异常，请手动操作')
                print('继续等待图片上传完成0001...')
                WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath("/html/body/div[1]/div[2]/section[2]/div/div[1]/div/div[2]/div/div[contains(text(),'完成')]"))
            print('图片已经上传0002...')
        else:
            print("imageCount=",imageCount)
            imageCount+=1
            if imageCount%10==0:
                print('开始睡眠，清除图片')
                time.sleep(10)
                try:
                    driver.find_element_by_xpath("//span[contains(text(),'移除')]").click()#点击上传按钮
                except:
                    print('手动清除图片')
            for path in paths[begin:end]:
                imagefile.send_keys(path)#上传图片
            try:
                WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath("//span[contains(text(),'上传')]")).click()
                WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath("/html/body/div[1]/div[2]/section[2]/div/div[1]/div/div[2]/div/div[contains(text(),'完成')]"))
            except:
                print('可能发生异常，请手动操作')
                try:
                    WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath("/html/body/div[1]/div[2]/section[2]/div/div[1]/div/div[2]/div/div[contains(text(),'完成')]"))
                except:
                    print("请输入是否继续：1是/2 否")
                    is_continue = input()
                    print(is_continue)
                    if is_continue=='1':
                        pass
                    elif is_continue=='2':
                        raise FooError('手动异常终止程序...')
                    else:
                        print('输入了非法字符，默认继续')
                        
            print('图片已经上传0004...')
            
        
def from_begin_to_end(driver,sleepTime,item):
        print('execute from_begin_to_end()...')
        js="window.open('http://159.226.67.87/lifenote/user/record/addNew')"
        #js="window.open('http://159.226.67.87/lifenote/user/media/addBatch/374')"
        driver = open_new_windows(driver,js)
        time.sleep(sleepTime)
        add_new_view(driver,item['记录日期'],item['地理位置关键词'],item['地理位置'],item['数据集'],item['观测笔记'])
        time.sleep(sleepTime)
        enter_add_new_video_page(driver)
        time.sleep(sleepTime)
        add_new_video(driver,item['图片文件夹位置'],item['拉丁'],item['中文'],item['分类备注'],item['拍摄者'],item['类群'],item['鉴定阶元'],item['鉴定状态'])

def only_upload_imgs(driver,sleepTime,item,js):
    print("execute only_upload_imgs() ...")
    driver = open_new_windows(driver,js)
    add_new_video(driver,item['图片文件夹位置'],item['拉丁'],item['中文'],item['分类备注'],item['拍摄者'],item['类群'],item['鉴定阶元'],item['鉴定状态'])
    
    
if __name__ == '__main__':
    username = '用户名'
    password = '密码'
    items = [ 
            #1已经上传完成#{ "记录日期":"2018-06-01 00:00:00" , "地理位置关键词":"花木兰植物园" ,"地理位置":"花木兰植物园","观测笔记":"柳毒蛾幼虫128","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\柳毒蛾\\柳毒蛾-幼虫-2018.6-花木兰植物园","鉴定阶元":"种名","拉丁":"Stilprotia salicis","中文":"柳毒蛾","分类备注":"幼虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #2已经上传完成#{ "记录日期":"2017-11-23 00:00:00" , "地理位置关键词":"临春岭森林公园" ,"地理位置":"临春岭森林公园","观测笔记":"粉蚧48","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\粉蚧\\粉蚧-2017.11.23-临春岭森林公园","鉴定阶元":"科","拉丁":"Pseudococcidae","中文":"粉蚧","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #3已经上传完成#{ "记录日期":"2018-06-01 00:00:00" , "地理位置关键词":"卢沟桥秀园社区" ,"地理位置":"卢沟桥街道社区服务中心","观测笔记":"美国白蛾成虫14","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\美国白蛾\\美国白蛾-成虫-2018.6-卢沟桥秀园社区","鉴定阶元":"种名","拉丁":"Hyphantria cunea","中文":"美国白蛾","分类备注":"成虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #4已经上传完成#{ "记录日期":"2018-04-19 00:00:00" , "地理位置关键词":"云南版纳植物园" ,"地理位置":"版纳植物园","观测笔记":"粉蚧91","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\粉蚧\\粉蚧-2018.4.19-云南-版纳植物园","鉴定阶元":"科","拉丁":"Pseudococcidae","中文":"粉蚧","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #5已经上传完成#{{ "记录日期":"2017-12-21 00:00:00" , "地理位置关键词":"云南嘎洒镇曼景罕村" ,"地理位置":"曼景罕村","观测笔记":"红火蚁201","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\红火蚁\\红火蚁-2017.12.21-云南-嘎洒镇曼景罕村","鉴定阶元":"种名","拉丁":"Solenopsis invicta","中文":"红火蚁","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #6已经上传完成#{ "记录日期":"2018-07-18 00:00:00" , "地理位置关键词":"昆明" ,"地理位置":"昆明市","观测笔记":"2018.7.18-云南-昆明，红棕象甲，数量：119","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\红棕象甲\\红棕象甲-2018.7.18-云南-昆明-戌","鉴定阶元":"种名","拉丁":"Rhynchophorus ferrugineus","中文":"红棕象甲","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王戌博","类群":"虫"},
            #7已经上传完成#{ "记录日期":"2018-04-23 00:00:00" , "地理位置关键词":"云南普洱洗马河" ,"地理位置":"洗马河公园","观测笔记":"2018.4.23-云南-普洱洗马河,红火蚁,数量：180","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\红火蚁\\红火蚁-2018.4.23-云南-普洱洗马河","鉴定阶元":"种名","拉丁":"Solenopsis invicta","中文":"红火蚁","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #8已经上传完成#{ "记录日期":"2018-07-27 00:00:00" , "地理位置关键词":"中国科学院动物研究所" ,"地理位置":"中国科学院动物研究所","观测笔记":"2018-07-27，中国科学院动物研究所，美国白蛾，幼虫数量：117","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\美国白蛾\\美国白蛾-幼虫-2018.7.27-北京-动物所","鉴定阶元":"种名","拉丁":"Hyphantria cunea","中文":"美国白蛾","分类备注":"幼虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #9已经上传完成#{ "记录日期":"2018-06-01 00:00:00" , "地理位置关键词":"河北白洋淀" ,"地理位置":"白洋淀景区","观测笔记":"2018-06，白洋淀景区，柳毒蛾幼虫10，柳毒蛾成虫72，美国白蛾幼虫16，美国白蛾成虫102","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\柳毒蛾\\柳毒蛾-幼虫-2018.6-河北白洋淀","鉴定阶元":"种名","拉丁":"Stilprotia salicis","中文":"柳毒蛾","分类备注":"幼虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #9.1已经上传完成#{ "记录日期":"2018-06-01 00:00:00" , "地理位置关键词":"河北白洋淀" ,"地理位置":"白洋淀景区","观测笔记":"柳毒蛾成虫72","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\柳毒蛾\\柳毒蛾-成虫-2018.6-河北白洋淀","鉴定阶元":"种名","拉丁":"Stilprotia salicis","中文":"柳毒蛾","分类备注":"成虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #9.2已经上传完成#{ "记录日期":"2018-06-01 00:00:00" , "地理位置关键词":"河北白洋淀" ,"地理位置":"白洋淀景区","观测笔记":"美国白蛾幼虫16","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\美国白蛾\\美国白蛾-幼虫-2018.6-河北白洋淀","鉴定阶元":"种名","拉丁":"Hyphantria cunea","中文":"美国白蛾","分类备注":"幼虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #9.3已经上传完成#{ "记录日期":"2018-06-01 00:00:00" , "地理位置关键词":"河北白洋淀" ,"地理位置":"白洋淀景区","观测笔记":"美国白蛾成虫102","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\美国白蛾\\美国白蛾-成虫-2018.6-河北白洋淀","鉴定阶元":"种名","拉丁":"Hyphantria cunea","中文":"美国白蛾","分类备注":"成虫","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #10已经上传完成#{ "记录日期":"2018-04-21 00:00:00" , "地理位置关键词":"云南版纳植物园" ,"地理位置":"版纳植物园","观测笔记":"云南版纳植物园，红棕象甲，数量：27","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\红棕象甲\\红棕象甲-2018.4.21-云南-版纳植物园","鉴定阶元":"种名","拉丁":"Rhynchophorus ferrugineus","中文":"红棕象甲","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
            #11已经上传完成{"记录日期":"2018-04-22 00:00:00" , "地理位置关键词":"云南版纳植物园" ,"地理位置":"版纳植物园","观测笔记":"云南版纳植物园，红棕象甲，数量：232","数据集":"2018上半年照片任务","图片文件夹位置":"E:\\数据整理\\2018上半年照片任务_08月21日收\\红棕象甲\\红棕象甲-2018.4.22-云南-版纳植物园","鉴定阶元":"种名","拉丁":"Rhynchophorus ferrugineus","中文":"红棕象甲","分类备注":"无","鉴定状态":"鉴定完成","拍摄者":"王勇","类群":"虫"},
    ]
    count = 1
    sleepTime = 15
    for item in items:
        if(count == 1):
            driver = webdriver.Chrome()
            driver.get('http://159.226.67.87/lifenote/')#网站首页IP地址
            #driver.maximize_window() #最大化窗口
            login(driver,username,password)
            count+=1
        driver.implicitly_wait(10) # 隐性等待，最长等30秒
        time.sleep(10)
        from_begin_to_end(driver,sleepTime,item)
        #s="window.open('http://159.226.67.87/lifenote/user/media/addBatch/425')"#批量上传IP地址
        #nly_upload_imgs(driver,sleepTime,item,js)
    print("上传完成,程序已执行完毕")

    

#WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id("token"))  #等待时长10秒，默认0.5秒询问一次
