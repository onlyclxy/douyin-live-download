#-*- coding: utf-8 -*-
import random
import requests
import re
import os
# import urllib.request
import urllib.parse
import sys
# from bs4 import BeautifulSoup
import time
import json
import configparser
import subprocess
import threading
import string
import logging
import datetime
from configparser import RawConfigParser
from selenium.common.exceptions  import TimeoutException
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import shutil
import hashlib


version=230530.4  #请注意把下面这个地方和文件名改了就行啦
#pyinstaller -F 抖音直播录制_230530.5.py
#pyinstaller 抖音直播录制_230530.5.py

#log日志---------------------------------------------------------------
# sys.stdout = Logger(sys.stdout)  #  将输出记录到log
# sys.stderr = Logger(sys.stderr)  # 将错误信息记录到log    
# 创建一个logger 
logger = logging.getLogger('抖音直播录制%s版'%str(version))
logger.setLevel(logging.INFO)
# 创建一个handler，用于写入日志文件 
if not os.path.exists("log"):
    os.makedirs("log")    
fh = logging.FileHandler("log/错误日志文件.log",encoding="utf-8-sig",mode="a")
fh.setLevel(logging.WARNING)
# 再创建一个handler，用于输出到控制台 
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# formatter = logging.Formatter()
# ch.setFormatter(formatter)
# 定义handler的输出格式 
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
#ch.setFormatter(formatter)
# 给logger添加handler 
logger.addHandler(fh)
# logger.addHandler(ch)
# socket.setdefaulttimeout(10)

#全局变量--------------------------------------------------------------------------------
recording=set()
unrecording=set()
warning_count=0
maxrequest=0
runingList=[]
texturl=[]
textNoRepeatUrl=[]
createVar = locals()
firstStart=True #第一次 不会出现新增链接的字眼
namelist=[]
firstRunOtherLine=True #第一次运行显示线程等


# videosavetype="TS"
# delaydefault=60
# localdelaydefault=0
# videopath=""
# videoQuality="原画"
# videom3u8=False
# looptime=False
# Splitvideobysize=False
# Splitsizes=0
# tsconvertmp4=False
# tsconvertm4a=False    
# delFilebeforeconversion=False  
# creatTimeFile=False
# displayChrome=False
# coverlongurl=False
# onlybrowser=False   
# cookiesSet=""






def updateFile(file,old_str,new_str):
    file_data = ""
    with open(file, "r", encoding="utf-8-sig") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str,new_str)
            file_data += line
    with open(file,"w",encoding="utf-8-sig") as f:
        f.write(file_data)

def get_xx():
    string.ascii_letters= 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return random.choice(string.ascii_lowercase)

def get_dx():
    string.ascii_letters= 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return random.choice(string.ascii_uppercase)

def subwords(words):  
    words=re.sub('[-? * : " < >  / | .]', '', words)
    words=re.sub(r'/', '', words) 
    return words



def convertsmp4(address):  
    address2=address
    address2=address2.replace('.ts' , '')
    address2=address2.replace('.flv' , '')
    if tsconvertmp4:
        _output = subprocess.check_output([
            "ffmpeg", "-i",address,
            "-c:v","copy",
            "-c:a","copy",
            "-f","mp4",address2+".mp4",
        ], stderr = subprocess.STDOUT)
        #print("转换到mp4")
        if delFilebeforeconversion:
            time.sleep(1)
            if os.path.exists(address):
                os.remove(address)  


def convertsm4a(address):
    if tsconvertm4a:
        address2=address
        address2=address2.replace('.ts' , '')
        address2=address2.replace('.flv' , '')
        _output = subprocess.check_output([
            "ffmpeg", "-i",address,
            "-n","-vn",
            "-c:a","aac","-bsf:a","aac_adtstoasc","-ab","320k",
            address2+".m4a",
        ], stderr = subprocess.STDOUT)
        if delFilebeforeconversion:
            time.sleep(1)
            if os.path.exists(address):
                os.remove(address)        
        #print("转换到m4a")

def creatass(filegruop):
    startname=filegruop[0]
    assname=filegruop[1]
    index_time = -1
    finish=0
    today = datetime.datetime.now()
    re_datatime =today.strftime('%Y-%m-%d %H:%M:%S')

    # createVar[str(filegruop+"_th")] =threading.Thread()
    

    while(True):    
        index_time+=1    
        txt=str(index_time)+ "\n" + tranform_int_to_time(index_time)+',000 --> '+ tranform_int_to_time(index_time + 1)+',000' + "\n" + str(re_datatime) + "\n"
        
        with open(assname+".ass",'a',encoding='utf8') as f:
            f.write(txt)
        # print(txt)

        if startname not in recording:  
            finish+=1  
            offset = datetime.timedelta(seconds=1)
            # 获取修改后的时间并格式化        
            re_datatime = (today + offset).strftime('%Y-%m-%d %H:%M:%S')
            today=today + offset
            # print(re_date)    

        else:
            time.sleep(1) 
            today = datetime.datetime.now()            
            re_datatime =today.strftime('%Y-%m-%d %H:%M:%S')
                    
        if finish>15:
            break 

def videodownload(url,filename,size_all):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    size = 0
    chunk_size = 1024    
    requests.urllib3.disable_warnings()
    response = requests.get(url, headers=headers, stream=True, verify=False,proxies=None)
    with open(filename, 'wb') as file:
        for data in response.iter_content(chunk_size = chunk_size):
            file.write(data)
            size += len(data)
            file.flush()
            if size_all > 0:
                sys.stdout.write('  [下载进度]:%.2fMB/%.2fMB' % (float(size/10/ (size_all*1024*1024) * 100), size_all) + '\r')
                if size > size_all*1024*1024:
                    break
            else:
                sys.stdout.write('  [下载进度]:%.2fMB' % float(size/1024/1024) + '\r')
    print('下载完成')

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-US; Nexus 6P Build/OPM7.181205.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.11.1.1197 Mobile Safari/537.36'
}

print( '-------------- 吾爱破解论坛 程序当前配置----------------' )   
print("循环值守录制抖音直播 版本:%s"%str(version))






def newgeturl(url):
    # print("请求地址"+url)
    global warning_count
    try:  
        for _i in range(10):
            headers2 = {"referer": "https://www.douyin.com/",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                "cookie":cookiesSet}

            try:    
                res=requests.get(url,headers=headers2,proxies=None)
            except Exception as e:
                print("请求网页失败,请检查是否用了代理,错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )    
                logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                warning_count+=1
                return ""
            # print(res.text)
            if len(res.text)<5 or res.text.find("繁忙")>=0:
                # print(1)
                # print(res.text)
                time.sleep(1)
                continue  
            else:
                # print(res.text)
                # print("端口网址为:"+url)
                return res.text       
            # len(res.text)>5             
            print("未获取到正确的网页信息.此时获取的网页信息如下:"+ str(res.text))
            warning_count+=1

    except Exception as e:
        print("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )    
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 

        warning_count+=1
    return ""



def chromeAuto(url):   
    global warning_count
    try:   
        if displayChrome:   
            #是否有浏览器设置  
            chrome = webdriver.Chrome() 
        else:
            chrome = webdriver.Chrome(options=chrome_options)     

        for _b in range(5):

            chrome.set_page_load_timeout(1)
            try:
                chrome.get("https://www.douyin.com/discover")  # 往浏览器的网页地址栏填入url参数
            except:
                pass

                # print("超时了")
                # time.sleep(2)
                # chrome.close()
                # chrome.quit()

            chrome.set_page_load_timeout(3)
            for _t in range(10):
                #是否显示浏览器
                # chrome = Chrome()
                #设置超时5秒
                
                # url="https://live.douyin.com/webcast/web/enter/?aid=6383&web_rid=677464104206"        
                try:
                    try:
                        chrome.get(url)  # 往浏览器的网页地址栏填入url参数                    
                    except:
                        pass  

                    # try:
                    #     chrome.get(url)  # 往浏览器的网页地址栏填入url参数
                    #     time.sleep(10)
                    # except:
                    #     print("超时了")
                    #     time.sleep(2)
                    #     # chrome.close()
                    #     # chrome.quit()
                    #     continue

                    data = chrome.page_source
                    
                    if data.find("status")<0 or data.find("繁忙")>-1:
                        # print("未找到源码网址,2s后重试..")
                        time.sleep(0.5) 
                        chrome.refresh()
                        continue   
                    else:
                        chrome.quit()    
                        return data  

                except:            
                    time.sleep(2)                
                    continue   
            # print(1)
            # chrome.close()
                    
            # print(2)
            time.sleep(2)
    except Exception as e:
        print("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )    
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 

        warning_count+=1

    chrome.quit()    
    return ""          



def getStream_url(douyindata):
    # global warning_count
    portGroup=[]
    restext=""
    if douyindata.find("系统繁忙，请稍后再试")>=0:
        print("未找到源码网址,等待设定好的秒数后会自动重试, 如果一直出现这个问题,请联系作者")
        return portGroup
        
    try:
        #因为获取的网页包含html的信息, 下面对这些框架的代码进行清理. 清理后的代码为{..}可以转json
        #获取不到网页.返回空
        if douyindata=="":
            
            return(portGroup)

        position1=douyindata.find("{")
        position2=douyindata.rfind("}")
        restext=douyindata[position1:position2+1]

        #转换网页源码为json
        try:
            resjs=json.loads(restext)
        except Exception as e:
            if len(str(restext))>0:                
                print("json转换失败, 转换错误信息为: "+str(restext)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno))
                logger.warning("json转换失败,转换错误信息为: "+str(restext)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
            else:
                # print("json获取为空 发生错误的行数: "+str(e.__traceback__.tb_lineno))
                # logger.warning("json获取为空 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                pass 
            return portGroup
        #创建端口参数组
        #转换过json的代码,获取端口具体内容
        #获取主播名字
        startname=resjs["data"]["user"]['nickname']

        #格式化字符串.防止文件名出现特殊字符
        startname = subwords(startname)
        portGroup.append(startname)

        #获取直播间状态.2是直播.4是直播结束
        status=resjs["data"]["data"][0]["status"]  #直播状态  #m3u8流
        # print("直播状态:"+str(+status))

        # #去除前后空格
        # status=status.strip()

        if status==2:
            #参数组添加信息
            portGroup.append(status)
            #获取直播流地址

            
            if videoQuality=="超清":
                res=resjs["data"]["data"][0]["stream_url"]["hls_pull_url_map"]["HD1"]   #m3u8流
                res2=resjs["data"]["data"][0]["stream_url"]["flv_pull_url"]["HD1"]    #flv流
            if videoQuality=="高清":
                res=resjs["data"]["data"][0]["stream_url"]["hls_pull_url_map"]["SD1"]   #m3u8流
                res2=resjs["data"]["data"][0]["stream_url"]["flv_pull_url"]["SD1"]    #flv流                
            if videoQuality=="标清":
                res=resjs["data"]["data"][0]["stream_url"]["hls_pull_url_map"]["SD2"]   #m3u8流
                res2=resjs["data"]["data"][0]["stream_url"]["flv_pull_url"]["SD2"]    #flv流

            #蓝光,原画
            else:
                res=resjs["data"]["data"][0]["stream_url"]["hls_pull_url_map"]["FULL_HD1"]   #m3u8流
                res2=resjs["data"]["data"][0]["stream_url"]["flv_pull_url"]["FULL_HD1"]    #flv流





            # print("下载地址为:"+res)
            #参数组添加信息
            portGroup.append(res)
            portGroup.append(res2)

        else:
            #参数组添加信息
            portGroup.append(status)
            portGroup.append("")
            portGroup.append("")
            # print("没有直播")

        #返回各种端口信息,主播名,状态码,地址
        return(portGroup)
    except Exception as e:
        print("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )    
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
        return portGroup
    return portGroup

#拼接端口的网址,这里只接收输入pc端的网址,输出端口网址
def SplicingUrl(inputUrl):
    try:
        resStr = (inputUrl.split("?")[0]).split("/")[-1]
        #当获取的rid拼接到网址里,获得端口网址
        # resStr="https://live.douyin.com/webcast/web/enter/?aid=6383&web_rid="+resStr 以前的版本
        resStr="https://live.douyin.com/webcast/room/web/enter/?aid=6383&device_platform=web&cookie_enabled=true&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=100.0.4896.127&web_rid="+resStr
        # print(resStr)
        #返回拼接网址
        return resStr
    except Exception as e:
        print("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno))
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 


def changemaxconnect():
    global maxrequest
    global warning_count
    #动态控制连接次数

    Preset=maxrequest
    # 记录当前时间      
    start_time = time.time()

    while True:      

        time.sleep(5)

        if 10 <= warning_count <=20:
            if  Preset > 5:
                maxrequest = 5
            else:
                maxrequest //= 2  # 将maxrequest除以2（向下取整）
                if maxrequest > 0:  # 如果得到的结果大于0，则直接取该结果
                    maxrequest = Preset
                else:  # 否则将其设置为1
                    Preset = 1

            print("同一时间访问网络的线程数动态改为", maxrequest)
            warning_count=0
            time.sleep(5)
                
        elif 20 < warning_count:
            maxrequest = 1
            print("同一时间访问网络的线程数动态改为", maxrequest)            
            warning_count=0
            time.sleep(10)

        elif warning_count < 10 and time.time() - start_time >60:
            maxrequest = Preset
            warning_count=0
            start_time = time.time()
            print("同一时间访问网络的线程数动态改为", maxrequest)

        
def check_md5(file_path):
    """
    计算文件的md5值
    """
    with open(file_path, 'rb') as fp:
        file_md5 = hashlib.md5(fp.read()).hexdigest()
    return file_md5

def backup_file(file_path, backup_dir):
    """
    备份配置文件到备份目录
    """
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        # 拼接备份文件名，年-月-日-时-分-秒
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        backup_file_name = os.path.basename(file_path) + '_' + timestamp
        # 拷贝文件到备份目录
        backup_file_path = os.path.join(backup_dir, backup_file_name)
        shutil.copy2(file_path, backup_file_path)
        print(f'已备份配置文件{file_path}到{backup_file_path}')
    except Exception as e:
        print(f'备份配置文件{file_path}失败：{str(e)}')

def backup_file_start():
    config_file_path = './config.ini'
    url_config_file_path = './URL_config.ini'
    backup_dir = './配置自动备份文件夹'

    config_md5 = ''
    url_config_md5 = ''

    while True:
        try:  
            if os.path.exists(config_file_path):
                new_config_md5 = check_md5(config_file_path)
                if new_config_md5 != config_md5:
                    backup_file(config_file_path, backup_dir)
                    config_md5 = new_config_md5

            if os.path.exists(url_config_file_path):
                new_url_config_md5 = check_md5(url_config_file_path)
                if new_url_config_md5 != url_config_md5:
                    backup_file(url_config_file_path, backup_dir)
                    url_config_md5 = new_url_config_md5
            time.sleep(60)  # 每1分钟检测一次文件是否有修改
        except Exception as e:
            print(f'执行脚本异常：{str(e)}')



allLive=[]   #全部的直播
allRecordingUrl=[]

class C_real_url():
    def douyin(url):
        zhibo_ids=""
        #代码来自于https://github.com/wbt5/real-url/blob/master/douyin.py. 侵删
        x=0
        for y in range(2):
            x+=1
            if x>1:
                url=zhibo_ids
            #         DEBUG = False
            DEBUG = False
            headers = {
                'authority': 'v.douyin.com',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            }

            # url = input('请输入抖音直播链接或19位room_id：')
            # print("传入url",url)
            start_url=url #初始固定一个,防止后面的变量变了
            if re.match(r'\d{19}', url):
                room_id = url
            else:
                try:
                    url = re.search(r'(https.*)', url).group(1)
                    response = requests.head(url, headers=headers)
                    url = response.headers['location']
                    room_id = re.search(r'\d{19}', url).group(0)
                except Exception as e:
                    if DEBUG:
                        print(e)
                    print('地址请求失败,请检查这个网址是否正常: '+start_url)
                    sys.exit(1)
            # print('room_id', room_id)

            try:
                headers.update({
                    'authority': 'webcast.amemv.com',
                    'cookie': '_tea_utm_cache_1128={%22utm_source%22:%22copy%22%2C%22utm_medium%22:%22android%22%2C%22utm_campaign%22:%22client_share%22}',
                })

                params = (
                    ('type_id', '0'),
                    ('live_id', '1'),
                    ('room_id', room_id),
                    ('app_id', '1128'),
                )

                response = requests.get('https://webcast.amemv.com/webcast/room/reflow/info/', headers=headers, params=params).json()
                

                try:
                    rtmp_pull_url = response['data']['room']['stream_url']['flv_pull_url']['FULL_HD1']
                except Exception as e:
                    rtmp_pull_url = response['data']['room']['stream_url']['rtmp_pull_url']
            

                try: 
                    hls_pull_url = response['data']['room']['stream_url']['hls_pull_url_map']['FULL_HD1']
                except Exception as e:
                    hls_pull_url = response['data']['room']['stream_url']['hls_pull_url']

                

                hls_pull_url = response['data']['room']['stream_url']['hls_pull_url']
                zhubo_name = response['data']['room']['owner']['nickname']
                zhibo_id = response['data']['room']["id_str"] #只要判定这个有没有


 

                try:
                    zhibo_ids = response['data']['room']['owner']['own_room']["room_ids_str"][0] #如果这个出错,就判断没有播. 只有播放的时候才会出现这个
                    if zhibo_id==zhibo_ids:
                        # print(zhibo_id)

                        response = requests.head(rtmp_pull_url)
                        if response.status_code == 200:
                            # print(rtmp_pull_url+'直播流链接存在')
                            valueA=True
                        else:
                            # print(rtmp_pull_url+'直播流链接不存在')
                            valueA=False

                        response = requests.head(hls_pull_url)
                        if response.status_code == 200:
                            valueB=True
                            # print(hls_pull_url+'直播流链接存在')
                        else:
                            # print(hls_pull_url+'直播流链接不存在')
                            valueB=False

                        if valueA and valueB:
                            urlA=hls_pull_url
                            urlB=rtmp_pull_url
                        elif  valueA and valueB==False:
                            urlA=hls_pull_url
                            urlB=hls_pull_url
                        elif valueA==False and valueB:
                            urlA=rtmp_pull_url
                            urlB=rtmp_pull_url
                        else: #都不存在
                            urlA=hls_pull_url
                            urlB=rtmp_pull_url      
                                               
                        return([zhubo_name,2,urlA,urlB]) #因为上面出错到不了这里. 所以这里直接设置状态为2
                    else:
                        continue
                
                except:
                    response = requests.head(rtmp_pull_url)
                    if response.status_code == 200:
                        # print(rtmp_pull_url+'直播流链接存在')
                        valueA=True
                    else:
                        # print(rtmp_pull_url+'直播流链接不存在')
                        valueA=False

                    response = requests.head(hls_pull_url)
                    if response.status_code == 200:
                        valueB=True
                        # print(hls_pull_url+'直播流链接存在')
                    else:
                        # print(hls_pull_url+'直播流链接不存在')
                        valueB=False

                    if valueA and valueB:
                        urlA=hls_pull_url
                        urlB=rtmp_pull_url
                    elif  valueA and valueB==False:
                        urlA=hls_pull_url
                        urlB=hls_pull_url
                    elif valueA==False and valueB:
                        urlA=rtmp_pull_url
                        urlB=rtmp_pull_url
                    else: #都不存在
                        urlA=hls_pull_url
                        urlB=rtmp_pull_url          
                                     
                    return([zhubo_name,4,urlA,urlB]) 
                    pass
                # print(zhibo_ids) #如果这个出错,就判断没有播. 只有播放的时候才会出现这个
                # response = requests.head(rtmp_pull_url, timeout=10)
                # if response.status_code == 200:
                #     print('直播流链接存在')
                # else:
                #     print('直播流链接不存在')


                # print(rtmp_pull_url)
                # print(hls_pull_url)
                return [""]
            except Exception as e:
                if DEBUG:
                    print(e)
                return [""]
                # print('获取real url失败')        
        return [""]

print( '......................................................' ) 

def startgo(line,countvariable=-1):
    global warning_count
    # countvariable=line[1]
    # line=line[0]
    while True:
        try:
            # global allLive
            recordfinish=False
            recordfinish_2=False
            counttime=time.time()
            global videopath

            if len(line)<2 or type(line)==str:
                ridcontent=[line,""]
            else:
                ridcontent = line
            rid=ridcontent[0]
            if ridcontent[1]!="":
                print("运行新线程,传入地址"+ridcontent[0],ridcontent[1]+" 序号"+str(countvariable))
            else:
                print("运行新线程,传入地址"+ridcontent[0]+" 序号"+str(countvariable))

            #设置一个数组来获取端口参数    
            portInfo=[]
            startname=""
            # changestaute=""
            Runonce=False
            while True:        
                try:
                    if ridcontent[0].find("https://live.douyin.com/")>-1:
                    #获取源码
                        codePath=SplicingUrl(ridcontent[0])
                        # print("codepath:"+codePath)
                        #浏览器方案
                        if onlybrowser:
                            dycode=chromeAuto(codePath)
                        # cookies方案
                        else:
                            with semaphore:
                                dycode=newgeturl(codePath)
                        # print("获取网页信息完毕")
                        #获取端口信息
                        portInfo=getStream_url(dycode)
                    elif ridcontent[0].find("https://v.douyin.com/")>-1:                        
                        portInfo=C_real_url.douyin(ridcontent[0])
                        # print("portInfo",portInfo)
                    else:
                        portInfo=""
                        
                    # print("端口信息:"+str(portInfo))
                    # 判断返回参数数组长度,防止出错闪退
                    if len(portInfo)==4:
                        #判断状态码
                        startname=portInfo[0]
                        if startname in allLive:
                            print("新增的地址: %s 已经存在,本条线程将会退出"%startname)
                            namelist.append(str(rid)+"|"+str("#"+rid))
                            exit(0)
                        if ridcontent[1]=="" and Runonce==False:                
                            namelist.append(str(ridcontent[0])+"|"+str(ridcontent[0]+",主播: "+startname.strip()))  
                            Runonce=True

                        if portInfo[1]==2:
                            print(portInfo[0]+" 正在直播中 序号"+str(countvariable))
                            

                            #是否显示地址
                            if videom3u8:
                                if videosavetype=="FLV":
                                    print(str(portInfo[0])+ " 直播地址为:"+str(portInfo[3]))
                                else:
                                    print(str(portInfo[0])+ " 直播地址为:"+str(portInfo[2]))
                            
                            #--------------------
                            #“portInfo[2]”对应的是m3u8地址
                            real_url=portInfo[2]
                            # changestaute=portInfo[1]
                            if real_url!="":    
                                now = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))             
                                try:
                                    if len(videopath)>0:
                                        if videopath[-1]!="/":
                                            videopath=videopath+"/"
                                        if not os.path.exists(videopath+startname):              
                                            os.makedirs(videopath+startname)  
                                    else:
                                        if not os.path.exists(startname): 
                                            os.makedirs('./'+startname)  

                                except Exception as e:
                                    print("路径错误信息708: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                    logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                

                                if not os.path.exists(videopath+startname):
                                    print("保存路径不存在,不能生成录制.请避免把本程序放在c盘,桌面,下载文件夹,qq默认传输目录.请重新检查设置")
                                    videopath=""
                                    print("因为配置文件的路径错误,本次录制在程序目录")
                                            
                                
                                if videosavetype=="FLV":
                                    filename=startname + '_' + now + '.flv'     
                                    filenameshort=startname + '_' + now        

                                    if len(videopath)==0:
                                        print("\r"+startname+" 录制视频中: "+os.getcwd()+"/"+startname +'/'+ filename)
                                    else:
                                        print("\r"+startname+" 录制视频中: "+videopath+startname +'/'+ filename)

                                    if not os.path.exists(videopath+startname):
                                        print("目录均不能生成文件,不能生成录制.请避免把本程序放在c盘,桌面,下载文件夹,qq默认传输目录.请重新检查设置,程序将会退出")
                                        input("请按回车退出")
                                        os._exit(0)
                                    #flv录制格式

                                    filenameshort=videopath+startname +'/'+ startname + '_' + now

                                    if creatTimeFile:
                                        filenamegruop=[startname,filenameshort]
                                        createVar[str(filenameshort)] = threading.Thread(target=creatass,args=(filenamegruop,))
                                        createVar[str(filenameshort)].daemon=True
                                        createVar[str(filenameshort)].start()


                                    try:
                                        #“portInfo[3]”对应的是flv地址，使用老方法下载（直接请求下载flv）只能是下载flv流的。
                                        real_url=portInfo[3]
                                        real_url=real_url.replace("/u0026","&")
                                        #real_url='"'+real_url+'"'
                                        recording.add(startname)
                                        #老的下载方法
                                        _filepath, _ = urllib.request.urlretrieve(real_url, videopath+startname +'/'+ filename)
                                        # videodownload(real_url, videopath+startname +'/'+ filename,0)
                                        recordfinish=True
                                        recordfinish_2=True
                                        counttime=time.time()   
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)

                                    except:
                                        print('\r'+time.strftime('%Y-%m-%d %H:%M:%S  ') +startname + ' 未开播')     
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname) 

                                elif videosavetype=="MKV":            
                                    filename=startname + '_' + now + ".mkv"
                                    if len(videopath)==0:
                                        print("\r"+startname+ " 录制视频中: "+os.getcwd()+"/"+startname +'/'+ filename)
                                    else:
                                        print("\r"+startname+ " 录制视频中: "+videopath+startname +'/'+ filename)


                                    ffmpeg_path = "ffmpeg"         
                                    file = videopath+startname +'/'+ filename

                                    filenameshort=videopath+startname +'/'+ startname + '_' + now

                                    
                                    if creatTimeFile:
                                        filenamegruop=[startname,filenameshort]
                                        createVar[str(filenameshort)] = threading.Thread(target=creatass,args=(filenamegruop,))
                                        createVar[str(filenameshort)].daemon=True
                                        createVar[str(filenameshort)].start()




                                    try:
                                        real_url=real_url.replace("/u0026","&")
                                        #real_url='"'+real_url+'"'
                                        recording.add(startname)
                                        _output = subprocess.check_output([
                                            ffmpeg_path, "-y",
                                            "-v","verbose",
                                            "-rw_timeout","10000000", # 10s
                                            "-loglevel","error",
                                            "-hide_banner",
                                            "-user_agent",headers["User-Agent"],
                                            "-protocol_whitelist","rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
                                            "-thread_queue_size","1024",
                                            "-analyzeduration","2147483647",
                                            "-probesize","2147483647",
                                            "-fflags","+discardcorrupt",
                                            "-i",real_url,
                                            "-bufsize","5000k",
                                            "-map","0",
                                            "-sn","-dn",
                                            # "-bsf:v","h264_mp4toannexb",
                                            # "-c","copy",
                                            #"-c:v","libx264",   #后期可以用crf来控制大小
                                            "-reconnect_delay_max","30","-reconnect_streamed","-reconnect_at_eof",
                                            "-c:v","copy",   #直接用copy的话体积特别大.
                                            "-c:a","copy",
                                            "-max_muxing_queue_size","64",
                                            "-correct_ts_overflow","1",
                                            "-f","matroska",
                                            "{path}".format(path=file),
                                        ], stderr = subprocess.STDOUT)

                                        recordfinish=True
                                        recordfinish_2=True
                                        counttime=time.time()  
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)
                                    except subprocess.CalledProcessError as e:
                                        #logging.warning(str(e.output))
                                        print(str(e.output) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)        

                                elif videosavetype=="MP4":            
                                    filename=startname + '_' + now + ".mp4"
                                    if len(videopath)==0:
                                        print("\r"+startname+ " 录制视频中: "+os.getcwd()+"/"+startname +'/'+ filename)
                                    else:
                                        print("\r"+startname+ " 录制视频中: "+videopath+startname +'/'+ filename)


                                    ffmpeg_path = "ffmpeg"         
                                    file = videopath+startname +'/'+ filename

                                    filenameshort=videopath+startname +'/'+ startname + '_' + now

                                    
                                    if creatTimeFile:
                                        filenamegruop=[startname,filenameshort]
                                        createVar[str(filenameshort)] = threading.Thread(target=creatass,args=(filenamegruop,))
                                        createVar[str(filenameshort)].daemon=True
                                        createVar[str(filenameshort)].start()




                                    try:
                                        real_url=real_url.replace("/u0026","&")
                                        #real_url='"'+real_url+'"'
                                        recording.add(startname)
                                        _output = subprocess.check_output([
                                            ffmpeg_path, "-y",
                                            "-v","verbose",
                                            "-rw_timeout","10000000", # 10s
                                            "-loglevel","error",
                                            "-hide_banner",
                                            "-user_agent",headers["User-Agent"],
                                            "-protocol_whitelist","rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
                                            "-thread_queue_size","1024",
                                            "-analyzeduration","2147483647",
                                            "-probesize","2147483647",
                                            "-fflags","+discardcorrupt",
                                            "-i",real_url,
                                            "-bufsize","5000k",
                                            "-map","0",
                                            "-sn","-dn",
                                            # "-bsf:v","h264_mp4toannexb",
                                            # "-c","copy",
                                            #"-c:v","libx264",   #后期可以用crf来控制大小
                                            "-reconnect_delay_max","30","-reconnect_streamed","-reconnect_at_eof",
                                            "-c:v","copy",   #直接用copy的话体积特别大.
                                            "-c:a","copy",
                                            "-max_muxing_queue_size","64",
                                            "-correct_ts_overflow","1",
                                            "-f","mp4",
                                            "{path}".format(path=file),
                                        ], stderr = subprocess.STDOUT)                    

                                        recordfinish=True
                                        recordfinish_2=True
                                        counttime=time.time()  
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)
                                    except subprocess.CalledProcessError as e:
                                        #logging.warning(str(e.output))
                                        print(str(e.output) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)

                                elif videosavetype=="MKV音频":
                                    filename=startname + '_' + now + ".mkv"
                                    if len(videopath)==0:
                                        print("\r"+startname+" 录制MKV音频中: "+os.getcwd()+"/"+startname +'/'+ filename)
                                    else:
                                        print("\r"+startname+" 录制MKV音频中: "+videopath+startname +'/'+ filename)

                                    ffmpeg_path = "ffmpeg"         
                                    file = videopath+startname +'/'+ filename
                                    try:
                                        real_url=real_url.replace("/u0026","&")
                                        #real_url='"'+real_url+'"'
                                        recording.add(startname)
                                        _output = subprocess.check_output([
                                            ffmpeg_path,"-y",
                                            "-v","verbose",
                                            "-rw_timeout","10000000", # 10s
                                            "-loglevel","error",
                                            "-hide_banner",
                                            "-user_agent",headers["User-Agent"],
                                            "-protocol_whitelist","rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
                                            "-thread_queue_size","1024",
                                            "-analyzeduration","2147483647",
                                            "-probesize","2147483647",
                                            "-fflags","+discardcorrupt",
                                            "-i",real_url,
                                            "-bufsize","5000k",
                                            "-map","0:a",
                                            "-sn","-dn",
                                            "-reconnect_delay_max","30","-reconnect_streamed","-reconnect_at_eof",
                                            "-c:a","copy",
                                            "-max_muxing_queue_size","64",
                                            "-correct_ts_overflow","1",
                                            "-f","matroska",
                                            "{path}".format(path=file),
                                        ], stderr = subprocess.STDOUT)


                                        recordfinish=True
                                        recordfinish_2=True
                                        counttime=time.time()
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)
                                        if tsconvertm4a:
                                            threading.Thread(target=convertsm4a,args=(file,)).start()             
                                    except subprocess.CalledProcessError as e:
                                        #logging.warning(str(e.output))
                                        print(str(e.output) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)

                                elif videosavetype=="TS音频":
                                    filename=startname + '_' + now + ".ts"
                                    if len(videopath)==0:
                                        print("\r"+startname+" 录制TS音频中: "+os.getcwd()+"/"+startname +'/'+ filename)
                                    else:
                                        print("\r"+startname+" 录制TS音频中: "+videopath+startname +'/'+ filename)

                                    ffmpeg_path = "ffmpeg"         
                                    file = videopath+startname +'/'+ filename
                                    try:
                                        real_url=real_url.replace("/u0026","&")
                                        #real_url='"'+real_url+'"'
                                        recording.add(startname)
                                        _output = subprocess.check_output([
                                            ffmpeg_path,"-y",
                                            "-v","verbose",
                                            "-rw_timeout","10000000", # 10s
                                            "-loglevel","error",
                                            "-hide_banner",
                                            "-user_agent",headers["User-Agent"],
                                            "-protocol_whitelist","rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
                                            "-thread_queue_size","1024",
                                            "-analyzeduration","2147483647",
                                            "-probesize","2147483647",
                                            "-fflags","+discardcorrupt",
                                            "-i",real_url,
                                            "-bufsize","5000k",
                                            "-map","0:a",
                                            "-sn","-dn",
                                            "-reconnect_delay_max","30","-reconnect_streamed","-reconnect_at_eof",
                                            "-c:a","copy",
                                            "-max_muxing_queue_size","64",
                                            "-correct_ts_overflow","1",
                                            "-f","mpegts",
                                            "{path}".format(path=file),
                                        ], stderr = subprocess.STDOUT)


                                        recordfinish=True
                                        recordfinish_2=True
                                        counttime=time.time()
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)
                                        if tsconvertm4a:
                                            threading.Thread(target=convertsm4a,args=(file,)).start()             
                                    except subprocess.CalledProcessError as e:
                                        #logging.warning(str(e.output))
                                        print(str(e.output) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                        if startname in recording:                        
                                            recording.remove(startname) 
                                        if startname in unrecording:
                                            unrecording.add(startname)


                                        
                                else:               

                                    if(Splitvideobysize):    #这里默认是启用/不启用视频分割功能                                             
                                            while(True):        
                                                now = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time())) 
                                                filename=startname + '_' + now + ".ts"
                                                if len(videopath)==0:
                                                    print("\r"+startname+" 分段录制视频中: "+os.getcwd()+"/"+startname +'/'+ filename + " 每录满: %d M 存一个视频"%Splitsize )
                                                else:
                                                    print("\r"+startname+" 分段录制视频中: "+videopath+startname +'/'+ filename+ " 每录满: %d M 存一个视频"%Splitsize)

                                                ffmpeg_path = "ffmpeg"         
                                                file = videopath+startname +'/'+ filename
                                                filenameshort=videopath+startname +'/'+ startname + '_' + now

                                                if creatTimeFile:
                                                    filenamegruop=[startname,filenameshort]
                                                    createVar[str(filenameshort)] = threading.Thread(target=creatass,args=(filenamegruop,))
                                                    createVar[str(filenameshort)].daemon=True
                                                    createVar[str(filenameshort)].start()


                                                try:
                                                    real_url=real_url.replace("/u0026","&")
                                                    #real_url='"'+real_url+'"'
                                                    recording.add(startname)
                                                    _output = subprocess.check_output([
                                                        ffmpeg_path, "-y",
                                                        "-v","verbose", 
                                                        "-rw_timeout","10000000", # 10s
                                                        "-loglevel","error",
                                                        "-hide_banner",
                                                        "-user_agent",headers["User-Agent"],
                                                        "-protocol_whitelist","rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
                                                        "-thread_queue_size","1024",
                                                        "-analyzeduration","2147483647",
                                                        "-probesize","2147483647",
                                                        "-fflags","+discardcorrupt",
                                                        "-i",real_url,
                                                        "-bufsize","5000k",
                                                        "-map","0",
                                                        "-sn","-dn",
                                                        # "-bsf:v","h264_mp4toannexb",
                                                        # "-c","copy",
                                                        "-reconnect_delay_max","30","-reconnect_streamed","-reconnect_at_eof",
                                                        "-c:v","copy",
                                                        "-c:a","copy",
                                                        "-max_muxing_queue_size","64",
                                                        "-correct_ts_overflow","1",
                                                        "-f","mpegts",
                                                        "-fs",str(Splitsizes),
                                                        "{path}".format(path=file),
                                                    ], stderr = subprocess.STDOUT)


                                                    recordfinish=True   #这里表示正常录制成功一次
                                                    recordfinish_2=True
                                                    counttime=time.time() #这个记录当前时间, 用于后面 1分钟内快速2秒循环 这个值不能放到后面
                                                    if startname in recording:                        
                                                        recording.remove(startname) 
                                                    if startname in unrecording:
                                                        unrecording.add(startname)
                                                    if tsconvertmp4:
                                                        threading.Thread(target=convertsmp4,args=(file,)).start()
                                                    if tsconvertm4a:
                                                        threading.Thread(target=convertsm4a,args=(file,)).start()                                                   
                                                        
                                                except subprocess.CalledProcessError as e:
                                                    #这是里分段 如果录制错误会跳转到这里来
                                                    #logging.warning(str(e.output))
                                                    # print(str(e.output) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                                    # logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                                    if startname in recording:                        
                                                        recording.remove(startname) 
                                                    if startname in unrecording:
                                                        unrecording.add(startname)
                                                    break
                                    else:     
                                        filename=startname + '_' + now + ".ts"
                                        if len(videopath)==0:
                                            print("\r"+startname+" 录制视频中: "+os.getcwd()+"/"+startname +'/'+ filename)
                                        else:
                                            print("\r"+startname+" 录制视频中: "+videopath+startname +'/'+ filename)

                                        ffmpeg_path = "ffmpeg"         
                                        file = videopath+startname +'/'+ filename
                                        filenameshort=videopath+startname +'/'+ startname + '_' + now

                                        if creatTimeFile:
                                            filenamegruop=[startname,filenameshort]
                                            createVar[str(filenameshort)] = threading.Thread(target=creatass,args=(filenamegruop,))
                                            createVar[str(filenameshort)].daemon=True
                                            createVar[str(filenameshort)].start()



                                        try:
                                            real_url=real_url.replace("/u0026","&")
                                            # real_url="\""+real_url+"\""
                                            #real_url='"'+real_url+'"'
                                            # print(real_url)
                                            recording.add(startname)
                                            _output = subprocess.check_output([
                                                ffmpeg_path, "-y",
                                                "-v","verbose", 
                                                "-rw_timeout","10000000", # 10s
                                                "-loglevel","error",
                                                "-hide_banner",
                                                "-user_agent",headers["User-Agent"],
                                                "-protocol_whitelist","rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
                                                "-thread_queue_size","1024",
                                                "-analyzeduration","2147483647",
                                                "-probesize","2147483647",
                                                "-fflags","+discardcorrupt",
                                                "-i",real_url,
                                                "-bufsize","5000k",
                                                "-map","0",
                                                "-sn","-dn",
                                                # "-bsf:v","h264_mp4toannexb",
                                                # "-c","copy",
                                                "-reconnect_delay_max","30","-reconnect_streamed","-reconnect_at_eof",
                                                "-c:v","copy",
                                                "-c:a","copy",
                                                "-max_muxing_queue_size","64",
                                                "-correct_ts_overflow","1",
                                                "-f","mpegts",
                                                "{path}".format(path=file),
                                            ], stderr = subprocess.STDOUT)


                                            recordfinish=True
                                            recordfinish_2=True
                                            counttime=time.time()
                                            if startname in recording:                        
                                                recording.remove(startname) 
                                            if startname in unrecording:
                                                unrecording.add(startname)
                                            if tsconvertmp4:
                                                threading.Thread(target=convertsmp4,args=(file,)).start()
                                            if tsconvertm4a:
                                                threading.Thread(target=convertsm4a,args=(file,)).start()                                    
                                                    
                                                                    
                                        except subprocess.CalledProcessError as e:
                                            #logging.warning(str(e.output))
                                            print(str(e.output) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                                            logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                                            if startname in recording:                        
                                                recording.remove(startname) 
                                            if startname in unrecording:
                                                unrecording.add(startname)

                            else:    
                                print('直播间不存在或未开播')
                                pass

                            if recordfinish_2==True:                              
                                if startname in recording:                        
                                    recording.remove(startname) 
                                if startname in unrecording:
                                    unrecording.add(startname)
                                print('\n'+startname+" "+ time.strftime('%Y-%m-%d %H:%M:%S  ') + '直播录制完成\n')
                                recordfinish_2=False

                        else:
                            print("序号"+str(countvariable) + " " + portInfo[0] + " 等待直播.. ")
                            startname=portInfo[0]
                        

                    else:
                        if len(startname)==0:
                            print('序号'+ str(countvariable) +' 网址内容获取失败,进行重试中...获取失败的地址是:'+ str(line))
                        else:
                            print('序号'+ str(countvariable) +' 网址内容获取失败,进行重试中...获取失败的地址是:'+ str(line)+" 主播为:"+str(startname))
                        warning_count+=1
                        
                except Exception as e:    
                    print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
                    # print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')
                    logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
                    warning_count+=1
                    
                
                num = random.randint(-5, 5) + delaydefault  # 生成-5到5的随机数，加上delaydefault
                if num < 0:  # 如果得到的结果小于0，则将其设置为0
                    num = 0
                x=num

                # 如果出错太多,就加秒数
                if warning_count>100: 
                    x=x+60
                    print("瞬时错误太多,延迟加60秒")
                    

                #这里是.如果录制结束后,循环时间会暂时变成30s后检测一遍. 这样一定程度上防止主播卡顿造成少录
                #当30秒过后检测一遍后. 会回归正常设置的循环秒数
                if recordfinish==True: 
                    counttimeend=time.time()-counttime
                    if counttimeend<60:
                        x=30 #现在改成默认20s
                        recordfinish=False
                    else:
                        recordfinish=False
                else:
                    x=num

                #这里是正常循环
                while x:
                    x = x-1
                    # print('\r循环等待%d秒 '%x)
                    if looptime:
                        print('\r'+startname+' 循环等待%d秒 '%x ,end="")
                    time.sleep(1)
                if looptime:   
                    print('\r检测直播间中...',end="") 
        except Exception as e:    
            print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
            # print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')
            logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
            print("线程崩溃2秒后重试.错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno))
            warning_count+=1
            time.sleep(2)
def searchUserWeb(url):
    # re=requests.get("https://www.douyin.com/user/MS4wLjABAAAAfSxBYimoCmZ8PjEV0yd0ETo9gZHW9DJCHO0arjojTuQ")
    try:
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76'}
        headers3 = {"referer": "https://www.douyin.com/",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        "cookie":cookiesSet}
        # re=requests.get(url=url,proxies=None)
        re=requests.get(url=url,headers=headers3)
        p1=re.text.find("><a href=\"https://live.douyin.com/")
        res=re.text[p1:] 
        p2=res.find("?")
        res=res[:p2]    
        p3=res.rfind("https://live.douyin.com/")
        res=res[p3:]    
        url=res
    except Exception as e:    
        print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
        # print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
    # print(res)
    return url
    

def checkUrlTxt(UrlTxt):
    lastUrlGroup=[]
    try:
        if len(UrlTxt)<=30: #短连接
            # chrome = webdriver.Chrome(service=ChromeDrivePath,options=chrome_options)          
            if displayChrome:   
                #是否有浏览器设置        
                chrome = webdriver.Chrome() 
            else:
                chrome = webdriver.Chrome(options=chrome_options)  
            
            try:
                chrome.get(UrlTxt)  # 往浏览器的网页地址栏填入url参数
                # 设置显式等待，超时时长最大为5s，每隔1s查找元素一次
                # WebDriverWait(chrome,5,1).until(EC.presence_of_element_located(("class name","fpRIB_wC")))
                time.sleep(1)
                dyUrl=chrome.current_url
                chrome.quit()
            except:
                dyUrl=chrome.current_url
                print("超时了")            
                chrome.quit()
                

            # 获取全部标签页

            # time.sleep(2)
            # 将激活标签页设置为最新的一项(按自己业务改)
            # chrome.switch_to.window(window.pop())
            
            position1=dyUrl.find("https://live.douyin.com/")
            if position1>-1: #表示是正常跳转过后的地址
                position2=dyUrl.find("?")
                if position2>-1:
                    lastUrl=dyUrl[0:position2]
                    lastUrlGroup=[lastUrl,'1'] #1标识为有替换长连接                    
                else:                    
                    lastUrlGroup=[] #1标识为有替换长连接             
            else:                 
                lastUrlGroup=[] #1标识为有替换长连接   

        else:            
            lastUrlGroup=[] 

    except Exception as e:    
        chrome.quit()
        print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
        # print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 
        lastUrlGroup=[]

    return(lastUrlGroup)

start5 = datetime.datetime.now()
def displayinfo():
    global start5
    time.sleep(5)
    while True:
        try:
            time.sleep(5)
            os.system("cls")
            # print("循环值守录制抖音直播 版本:%s"%str(version))
            print("\r共监测"+str(Monitoring)+"个直播中", end=" | ")
            #以前的信息
            print("同一时间访问网络的线程数:",maxrequest, end=" | ")            
            if len(videopath)>0:
                if not os.path.exists(videopath):
                    print("配置文件里,直播保存路径并不存在,请重新输入一个正确的路径.或留空表示当前目录,按回车退出")
                    input("程序结束")
                    os._exit(0)
                else:
                    print("视频保存路径: "+videopath, end=" | ")
                    pass
            else:
                print("视频保存路径: 当前目录", end=" | ")             
                
                
            if Splitvideobysize:
                print("TS录制分段开启，录制分段大小为 %d M"%Splitsize, end=" | ")
                
            if onlybrowser:
                print("浏览器检测录制", end=" | ")
            else:
                print("Cookies录制", end=" | ")
                
                
 
                
                
            print("录制视频质量为: "+str(videoQuality), end=" | ")  
            print("录制视频格式为: "+str(videosavetype), end=" | ")               
            # print("同一时间访问网络的线程数为: "+str(maxrequest), end=" | ")
            print("目前瞬时错误数为: "+str(warning_count), end=" | ")
            nowdate=time.strftime("%H:%M:%S", time.localtime())
            print(str(nowdate))
            if len(recording)==0 and len(unrecording)==0:
                time.sleep(5)                
                print("\r没有正在录制的直播 "+nowdate,end="")
                print("")
                
                continue
            else:
                # livetask = len(recording) + len(unrecording)
                # print("正则监控{}个直播".format(str(livetask)))
                if len(recording)>0:                
                    print("x"*60)
                    NoRepeatrecording = list(set(recording))
                    print("正在录制{}个直播: ".format(str(len(NoRepeatrecording))))
                    for x in NoRepeatrecording:
                        print(x+" 正在录制中")
                    #print("%i个直播正在录制中: "%len(NoRepeatrecording)+nowdate)
                    end = datetime.datetime.now()
                    print('总共录制时间: ' +str(end - start5))            
                    print("x"*60)
                else:
                    start5 = datetime.datetime.now()
        except Exception as e:    
            print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
            # print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')
            logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)) 

#--------------------------------------------------------------------------------------------------------------------------------------------
#最开始运行下面的


#备份
t3 = threading.Thread(target=backup_file_start, args=(), daemon=True)
t3.start()  

#检测ffmpeg是否存在
ffmepgFileCheck= subprocess.getoutput(["ffmpeg"])
if ffmepgFileCheck.find("run")>-1:
    # print("ffmpeg存在")
    pass
else:
    print("重要提示:")
    print("检测到ffmpeg不存在,请将ffmpeg.exe放到同目录,或者设置为环境变量,没有ffmpeg将无法录制")

Monitoring=0
while True:    
    #循环读取配置
    try:
        f =open("config.ini",'r', encoding='utf-8-sig')
        f.close()

    except IOError:
        f = open("config.ini",'w', encoding='utf-8-sig')
        f.close()


    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        rid=config.get('1', '直播地址')
    except:
        rid=""


    if os.path.isfile("URL_config.ini"):    
        f =open("URL_config.ini",'r', encoding='utf-8-sig')
        inicontent=f.read()
        f.close()
    else:
        inicontent=""



    if len(inicontent)==0:
        print('请输入要录制的抖音主播pc端直播网址.请注意备份url_config.ini,最近版本增加短连接可能会误删配置里的内容:')
        inurl=input()
        f = open("URL_config.ini",'a+',encoding='utf-8-sig')
        f.write(inurl)
        f.close()
        
        config = configparser.ConfigParser()

        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '直播地址')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组

        #config.set('1', '直播地址', inurl)# 给type分组设置值
        config.set('1', '循环时间(秒)', '60')# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭



    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        maxrequest=config.getint('1', '同一时间访问网络的线程数')
    except:
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '同一时间访问网络的线程数')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组

        config.set('1', '同一时间访问网络的线程数', '3')# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        maxrequest=3

    semaphore = threading.Semaphore(maxrequest)
    # print("同一时间访问网络的线程数:",maxrequest)







    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        delaydefault=config.getint('1', '循环时间(秒)')
    except:
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '循环时间(秒)')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组

        config.set('1', '循环时间(秒)', '60')# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        delaydefault=60



    # config.get(section,option) 得到section中option的值，返回为string类型
    # config.getint(section,option) 得到section中option的值，返回为int类型
    # config.getboolean(section,option) 得到section中option的值，返回为bool类型
    # config.getfloat(section,option) 得到section中option的值，返回为float类型


    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        localdelaydefault=config.getint('1', '排队读取网址时间(秒)')
    except:
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '排队读取网址时间(秒)')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组

        config.set('1', '排队读取网址时间(秒)', '3')# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        localdelaydefault=0
        


    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        videopath=config.get('1', '直播保存路径')
    except:
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')
        else:
            config.remove_option('1', '直播保存路径')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组

        config.set('1', '直播保存路径', '')# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        videopath=""





    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        videosavetype=config.get('1', '视频保存格式TS|MKV|FLV|MP4|TS音频|MKV音频')

    except Exception as _e:
        
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '视频保存格式TS|MKV|FLV|MP4|TS音频|MKV音频')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '视频保存格式TS|MKV|FLV|MP4|TS音频|MKV音频',"TS")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        videosavetype="TS"

    if len(videosavetype)>0:
        if videosavetype.upper().lower()=="FLV".lower():
            videosavetype="FLV"
            # print("直播视频保存为FLV格式")
        elif videosavetype.upper().lower()=="MKV".lower():
            videosavetype="MKV"
            # print("直播视频保存为MKV格式")
        elif videosavetype.upper().lower()=="TS".lower():
            videosavetype="TS"
            # print("直播视频保存为TS格式")
        elif videosavetype.upper().lower()=="MP4".lower():
            videosavetype="MP4"
            # print("直播视频保存为MP4格式")
        elif videosavetype.upper().lower()=="TS音频".lower():
            videosavetype="TS音频"
            # print("直播视频保存为TS音频格式")
        elif videosavetype.upper().lower()=="MKV音频".lower():
            videosavetype="MKV音频"
            # print("直播视频保存为MKV音频格式")        
        else:
            videosavetype="TS"
            print("直播视频保存格式设置有问题,这次录制重置为默认的TS格式")
    else:
        videosavetype="TS"
        print("直播视频保存为TS格式")           
    #------------------------------------------
    #选择画质
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        videoQuality=config.get('1', '原画|超清|高清|标清')

    except Exception as _e:
        
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '原画|超清|高清|标清')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '原画|超清|高清|标清',"原画")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        videoQuality="原画"

    #是否显示直播地址
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        videom3u8=config.get('1', '是否显示直播地址')

    except Exception as _e:
        
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '是否显示直播地址')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '是否显示直播地址',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        videom3u8="否"    


    if videom3u8=="是":
        videom3u8=True
    else:
        videom3u8=False






    #是否显示循环秒数
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        looptime=config.get('1', '是否显示循环秒数')

    except Exception as _e:
        
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '是否显示循环秒数')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '是否显示循环秒数',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        looptime="否"    


    if looptime=="是":
        looptime=True
    else:
        looptime=False


    # #这里是控制是否设置代理
    # try:    
    #     config = configparser.ConfigParser()
    #     config.read('config.ini', encoding='utf-8-sig')
    #     proxies2=config.get('1', '本地代理端口')
    #     proxiesn=proxies2
    #     if len(proxies2)>0:   
            
    #         proxies2={'https': 'http://127.0.0.1:'+str(proxies2)}        
    #         print("检测到有设置代理地址为: "+'http://127.0.0.1:'+str(proxiesn))

    # except Exception as _e:
        
    #     config = configparser.ConfigParser()
    #     # -read读取ini文件
    #     config.read('config.ini', encoding='utf-8-sig')
    #     listx = []
    #     listx = config.sections()# 获取到配置文件中所有分组名称
    #     if '1' not in listx:# 如果分组type不存在则插入type分组
    #         config.add_section('1')

    #     else:
    #         config.remove_option('1', '本地代理端口')# 删除type分组的stuno
    #         # config.remove_section('tpye')# 删除配置文件中type分组


    #     config.set('1', '本地代理端口',"")# 给type分组设置值

    #     o = open('config.ini', 'w',encoding='utf-8-sig')

    #     config.write(o)
        
    #     o.close()#不要忘记关闭

    #     proxies2=""    


    #这里是控制TS是否分段
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        Splitvideobysize=config.get('1', 'TS格式分段录制是否开启')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', 'TS格式分段录制是否开启')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', 'TS格式分段录制是否开启',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        Splitvideobysize="否"    


    if Splitvideobysize=="是":
        Splitvideobysize=True
    else:
        Splitvideobysize=False




    #这里是控制TS分段大小

    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        Splitsize=config.getint('1', '视频分段大小(兆)')
    except:
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')
        else:
            config.remove_option('1', '视频分段大小(兆)')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组
        config.set('1', '视频分段大小(兆)', '1000')# 给type分组设置值
        o = open('config.ini', 'w',encoding='utf-8-sig')
        config.write(o)    
        o.close()#不要忘记关闭
        Splitsize=1000 #1g

    #分段大小不能小于5m
    if Splitsize<5:
        Splitsize=5 #最低不能小于5m

    Splitsizes=Splitsize*1024*1024  #分割视频大小,转换为字节






    #这里是控制TS是否追加mp4格式
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        tsconvertmp4=config.get('1', 'TS录制完成后自动增加生成MP4格式')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', 'TS录制完成后自动增加生成MP4格式')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', 'TS录制完成后自动增加生成MP4格式',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        tsconvertmp4="否"    


    if tsconvertmp4=="是":
        tsconvertmp4=True
    else:
        tsconvertmp4=False

    #这里是控制TS是否追加m4a格式
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        tsconvertm4a=config.get('1', 'TS录制完成后自动增加生成m4a格式')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', 'TS录制完成后自动增加生成m4a格式')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', 'TS录制完成后自动增加生成m4a格式',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        tsconvertm4a="否"    

    if tsconvertm4a=="是":
        tsconvertm4a=True
    else:
        tsconvertm4a=False    

    #追加格式后,是否删除原文件
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        delFilebeforeconversion=config.get('1', '追加格式后删除原文件')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '追加格式后删除原文件')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '追加格式后删除原文件',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        delFilebeforeconversion="否"    

    if delFilebeforeconversion=="是":
        delFilebeforeconversion=True
    else:
        delFilebeforeconversion=False  

    def tranform_int_to_time(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return ("%d:%02d:%02d" % (h, m, s))
        

    #这里控制是否生成时间文件
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        creatTimeFile=config.get('1', '生成时间文件')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '生成时间文件')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '生成时间文件',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        creatTimeFile="否"    


    if creatTimeFile=="是":
        creatTimeFile=True
    else:
        creatTimeFile=False



    # #这里设置浏览器位置
    # try:    
    #     config = configparser.ConfigParser()
    #     config.read('config.ini', encoding='utf-8-sig')
    #     chromePath=config.get('1', '浏览器位置')

    # except Exception as _e:
        
    #     config = configparser.ConfigParser()
    #     # -read读取ini文件
    #     config.read('config.ini', encoding='utf-8-sig')
    #     listx = []
    #     listx = config.sections()# 获取到配置文件中所有分组名称
    #     if '1' not in listx:# 如果分组type不存在则插入type分组
    #         config.add_section('1')

    #     else:
    #         config.remove_option('1', '浏览器位置')# 删除type分组的stuno
    #         # config.remove_section('tpye')# 删除配置文件中type分组


    #     config.set('1', '浏览器位置','data\chrome.exe')# 给type分组设置值

    #     o = open('config.ini', 'w',encoding='utf-8-sig')

    #     config.write(o)
        
    #     o.close()#不要忘记关闭
    #     chromePath='data\chrome.exe'


    #这里控制是否生显示浏览器
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        displayChrome=config.get('1', '是否显示浏览器')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '是否显示浏览器')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '是否显示浏览器',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        displayChrome="否"    


    if displayChrome=="是":
        displayChrome=True
    else:
        displayChrome=False



    #这里是控制是否转换短链接
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        coverlongurl=config.get('1', '短链接自动转换为长连接')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '短链接自动转换为长连接')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '短链接自动转换为长连接',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        coverlongurl="否"    


    if coverlongurl=="是":
        coverlongurl=True
    else:
        coverlongurl=False



    #这里是控制采用浏览器录制
    try:    
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        onlybrowser=config.get('1', '仅用浏览器录制')
            
    except Exception as _e:    
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', '仅用浏览器录制')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组


        config.set('1', '仅用浏览器录制',"否")# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭
        onlybrowser="否"    


    if onlybrowser=="是":
        onlybrowser=True
    else:
        onlybrowser=False    


    # #这里设置浏览器驱动位置
    # try:    
    #     config = configparser.ConfigParser()
    #     config.read('config.ini', encoding='utf-8-sig')
    #     chrome_DrivePath=config.get('1', '浏览器驱动位置')

    # except Exception as _e:
        
    #     config = configparser.ConfigParser()
    #     # -read读取ini文件
    #     config.read('config.ini', encoding='utf-8-sig')
    #     listx = []
    #     listx = config.sections()# 获取到配置文件中所有分组名称
    #     if '1' not in listx:# 如果分组type不存在则插入type分组
    #         config.add_section('1')

    #     else:
    #         config.remove_option('1', '浏览器驱动位置')# 删除type分组的stuno
    #         # config.remove_section('tpye')# 删除配置文件中type分组


    #     config.set('1', '浏览器驱动位置','"chromedriver.exe"')# 给type分组设置值

    #     o = open('config.ini', 'w',encoding='utf-8-sig')

    #     config.write(o)
        
    #     o.close()#不要忘记关闭
    #     chrome_DrivePath='"chromedriver.exe"'





    # print("最开始排队 "+ str(localdelaydefault)+" 秒后读取下一个地址")
    #cookiesSet
    cookiesSet=''   
    try:
        config = RawConfigParser()
        config.read('config.ini', encoding='utf-8-sig')
        cookiesSet=config.get('1', 'cookies')
    except:
        config = configparser.ConfigParser()
        # -read读取ini文件
        config.read('config.ini', encoding='utf-8-sig')
        listx = []
        listx = config.sections()# 获取到配置文件中所有分组名称
        if '1' not in listx:# 如果分组type不存在则插入type分组
            config.add_section('1')

        else:
            config.remove_option('1', 'cookies')# 删除type分组的stuno
            # config.remove_section('tpye')# 删除配置文件中type分组

        config.set('1', 'cookies', '')# 给type分组设置值

        o = open('config.ini', 'w',encoding='utf-8-sig')

        config.write(o)
        
        o.close()#不要忘记关闭

    # if cookiesSet=="":
    #     print("一般需要设置一个cookies才可以运行")

    # 谷歌浏览器驱动地址 
    # chrome_drive = 'data/chromedriver.exe'
    # # 谷歌浏览器位置
    # chromePath= r'D:\Software\JobSoftware\Chromium\Application\Chromium.exe'
    #设置浏览器位置

    # if os.path.exists(chrome_DrivePath)==False:
    #     print("错误-------------浏览器驱动不存在,请至少同目录有没有chromedriver文件")
    #     # time.sleep(3)

    # print(chrome_DrivePath)
    # ChromeDrivePath = Service(chrome_DrivePath)

    chrome_options = Options()

    # 配置不显示浏览器
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #忽略错误
    chrome_options.add_argument('--ignore-certificate-errors')   
    chrome_options.add_argument('--ignore-ssl-errors')    


    #读取url文件
    try:
        file=open("URL_config.ini","r",encoding="utf-8-sig")    
        for line in file:        
            line=line.strip()
            if line.startswith("#"):
                continue
            c=line.split()
            if len(c)==0:
                continue
            else:
                c=line.strip()

                c=c.split('#')
                if len(line)<20:
                    continue
                

                SplitTest = line.split(',')                    
                #判断有没有逗号,有逗号获取逗号前面的地址
                if len(SplitTest)>1:
                    resline= SplitTest[0]
                else:
                    resline=line   

                #短连接转换长连接
                if coverlongurl:
                    #查询是否为主页:有下面这个网址的,返回位置
                    if resline.find("https://www.douyin.com/user/")>-1:
                        res=searchUserWeb(resline)
                        #判断有没有正常返回路径. 如果上面函数出错,会返回输入的值. 那么判断出错,就跳过
                        if res!=resline and res!="":
                            lastdyurl=res
                            namelist.append(str(resline)+"|"+str(res))
                            while len(namelist):    
                                a=namelist.pop()
                                replacewords = a.split('|')
                                if replacewords[0]!=replacewords[1]:                                
                                    updateFile(r"URL_config.ini", replacewords[0], replacewords[1])     
                                    print("转换了路径为:"+str(replacewords[1]))      
                                    resline=replacewords[1]


                    elif resline.find("https://v.douyin.com/")>-1:
                        #查询短链接
                        dyUrlGroup=checkUrlTxt(resline)
                        if len(dyUrlGroup)==2:
                            if dyUrlGroup[1]=="1":
                                namelist.append(str(resline)+"|"+str(dyUrlGroup[0]))
                                while len(namelist):    
                                    a=namelist.pop()
                                    replacewords = a.split('|')
                                    if replacewords[0]!=replacewords[1]: 
                                        updateFile(r"URL_config.ini", replacewords[0], replacewords[1]) 
                                        print("转换了路径为:"+str(replacewords[1]))




                if resline.find("https://live.douyin.com/")>-1 or resline.find("https://v.douyin.com/")>-1:
                    
                    #因为后面需要网址假主播名字,这里再补上
                    if len(SplitTest)>1:
                        lastdyurl= (resline,SplitTest[1])
                    else:
                        lastdyurl=(resline,"")

                    texturl.append(lastdyurl)


                else:                    
                    print(str(resline)+" 未知链接.此条跳过")

                    
                
                
                
                #print(c[0])
        file.close()        

        while len(namelist):    
            a=namelist.pop()
            replacewords = a.split('|')
            if replacewords[0]!=replacewords[1]:
                updateFile(r"URL_config.ini", replacewords[0], replacewords[1]) 
        #格式化后查找不一样

        if len(texturl)>0:
            textNoRepeatUrl = list(set(texturl))

        
        if len(textNoRepeatUrl)>0:
            for i in textNoRepeatUrl:
                #formatcontent[0] #这个为分离出的地址
                if i[0] not in runingList:
                    if firstStart==False: #第一次 不会出现新增链接的字眼
                        print("新增链接: "+ i[0])
                    Monitoring=Monitoring+1
                    args = [i, Monitoring]
                    createVar['thread'+ str(Monitoring)] = threading.Thread(target=startgo,args=args)
                    createVar['thread'+ str(Monitoring)].daemon=True
                    createVar['thread'+ str(Monitoring)].start()
                    runingList.append(i[0])
                    # print("\r"+str(localdelaydefault)+" 秒后读取下一个地址(如果存在) ")
                    time.sleep(localdelaydefault)
        texturl=[]
        firstStart=False #第一次 不会出现新增链接的字眼

    except Exception as e:    
        print("错误信息644:"+str(e)+"\r\n读取的地址为: "+str(rid) +" 发生错误的行数: "+str(e.__traceback__.tb_lineno)  )
        # print(rid+' 的直播地址连接失败,请检测这个地址是否正常,可以重启本程序--requests获取失败')
        logger.warning("错误信息: "+str(e)  +" 发生错误的行数: "+str(e.__traceback__.tb_lineno))   

     
     #这个是第一次运行其他线程.因为有变量前后顺序的问题,这里等全局变量完成后再运行def函数
    if firstRunOtherLine:
        t = threading.Thread(target=displayinfo, args=(), daemon=True)
        t.start()
        t2 = threading.Thread(target=changemaxconnect, args=(), daemon=True)
        t2.start()  

        firstRunOtherLine=False

    #总体循环3s       
    time.sleep(3)
#print('程式结束,请按任意键退出')
input()   


