
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2022/06/01 15:00:00
@Author  :   Daniel Chen
@Version :   5.4
@Contact :   13760280318@163.com
@Description :   Course-Bullying-in-SJTU 客户端GUI顶层实现
'''

current_version='v5.4'

# Headers to be included:
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk 
import sys,ctypes
import threading
from selenium import webdriver
from time import sleep
import os,subprocess
import time
import datetime
import subprocess
import inspect
import tkinter.messagebox 
import requests
import base64
import traceback
import http.client
import queue
import re
import urllib
import zipfile
import shutil

from qiangke import qiangkemain
from qiangkeicons import *
from ToolTip import createToolTip
from loggetter import loggetter,scrolltest
from chrome_checker import chrome_checker

# 全局变量声明
global q
q = queue.Queue()
global righttime
righttime=False
global img_png         
global img_png2        
global logger


version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')  # 匹配前3位版本号的正则表达式

# 操作系统检测
__pl=sys.platform
pl  = 'linux' if __pl.startswith('linux') else 'mac' if __pl == 'darwin' else 'win'

# 用于执行命令行命令
def shell(cmd):
    output= subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return 0

def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

#判断字符是否中文
def isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False
#===================================================================          

def load_config():
    if not os.path.exists('user/config.ini'):
        starttime.set('2022-06-01 00:00:00')
        maxtime.set('100000')
    else:
        f=open('user/config.ini','r',encoding='utf-8')
        data = f.readlines()
        for i in range(12):
            waitbox[i].set(data[i].strip().split('==')[1].strip())
        f.close()

def save_config():
    f=open('user/config.ini','w',encoding='utf-8')
    for i in range(12):
        f.write(str(retrieve_name(waitbox[i]))+'=='+waitbox[i].get().strip()+'\n')
    f.close()

class MyThread(threading.Thread):
  def __init__(self,action=None,logger=None,win=None,monty=None,headless=None,mode=None,on_time=None,times=None,kechengs=None,class_type=None,old_kechengs=None,old_class_type=None):
    threading.Thread.__init__(self)
    self.Flag=True        #停止标志位
    self.Parm=0         #用来被外部访问的
    self.action=action
    self.logger=logger
    self.win=win
    self.monty=monty
    self.headless=headless
    self.mode=mode
    self.on_time=on_time
    self.times=times
    self.kechengs=kechengs
    self.class_type=class_type
    self.old_kechengs=old_kechengs
    self.old_class_type=old_class_type
    self.caidan=False
    self.driver=None
      
  def run(self):
    option = webdriver.ChromeOptions()
    if self.headless:
        option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    option.add_argument("start-maximized") # https://stackoverflow.com/a/26283818/1689770
    option.add_argument("enable-automation") # https://stackoverflow.com/a/43840128/1689770
    option.add_argument("--no-sandbox") # https://stackoverflow.com/a/50725918/1689770
    option.add_argument("--disable-infobars") # https://stackoverflow.com/a/43840128/1689770
    option.add_argument("--disable-dev-shm-usage") # https://stackoverflow.com/a/50725918/1689770
    option.add_argument("--disable-browser-side-navigation") # https://stackoverflow.com/a/49123152/1689770
    option.add_argument("--disable-gpu") # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
    # 防止打印一些无用的日志
    option.add_experimental_option("excludeSwitches", ['enable-automation','enable-logging'])
    
    if pl=='win':self.driver = webdriver.Chrome(options=option,executable_path=os.path.join(os.getcwd(),'user/chromedriver.exe'))
    elif pl=='mac':self.driver = webdriver.Chrome(options=option,executable_path=os.path.join(os.getcwd(),'user/chromedriver'))
    self.driver.set_page_load_timeout(5)

    qiangkemain(self.driver,self.action,self.logger,self.win,self.monty,self.headless,self.mode,self.on_time,self.times,self.kechengs,self.class_type,self.old_kechengs,self.old_class_type,self.caidan)
   
  def setFlag(self,parm):     #外部停止线程的操作函数
    self.Flag=parm #boolean
  
  def setParm(self,parm):     #外部修改内部信息函数
    self.Parm=parm
  
  def getParm(self):       #外部获得内部信息函数
    return self.Parm



def clickMe():
    save_config()
    action.configure(text='脚本运行中')
    action.configure(state='disabled')    # Disable the Button Widget
    kechengs=[]
    class_type=[] 
    old_kechengs=[]
    old_class_type=[]
    
    mode=mo.get()
    if '定点' in mode:mode=1
    elif '替换' in mode:mode=3
    else:mode=2

    if mode!=3:
        if class1.get()!='' :kechengs.append(class1.get().strip().replace('：',':'))
        if class2.get()!='' :kechengs.append(class2.get().strip().replace('：',':'))
        if class3.get()!='' :kechengs.append(class3.get().strip().replace('：',':'))
        if class4.get()!='' :kechengs.append(class4.get().strip().replace('：',':'))
        if cate1.get()!='' :class_type.append(cate1.get().strip())
        if cate2.get()!='' :class_type.append(cate2.get().strip())
        if cate3.get()!='' :class_type.append(cate3.get().strip())
        if cate4.get()!='' :class_type.append(cate4.get().strip())
    else:
        if class1.get()!='' :kechengs.append(class1.get().strip())
        if class2.get()!='' :old_kechengs.append(class2.get().strip())
        if class3.get()!='' :kechengs.append(class3.get().strip())
        if class4.get()!='' :old_kechengs.append(class4.get().strip())
        if cate1.get()!='' :class_type.append(cate1.get().strip())
        if cate2.get()!='' :old_class_type.append(cate2.get().strip())
        if cate3.get()!='' :class_type.append(cate3.get().strip())
        if cate4.get()!='' :old_class_type.append(cate4.get().strip())

    if mode!=2 and starttime.get().strip()!='':
        on_time=starttime.get()
        on_time=on_time.strip()
        try:on_time=datetime.datetime.strptime(on_time,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            action.configure(text='脚本出错')
            tk.messagebox.showwarning('警告','开抢时间设置出错！\n请按照 %Y-%m-%d %H:%M:%S 的格式输入开始时间后重新运行脚本！')
            action.configure(text="确认配置并开始运行")
            action.configure(state='enabled')    # Disable the Button Widget
            return
    else:
        on_time='2022-06-01 00:00:00'
        on_time=datetime.datetime.strptime(on_time,'%Y-%m-%d %H:%M:%S')

    if maxtime.get().strip()!='':
        try:
            times=int(maxtime.get().strip())
            if times<=0:raise ValueError
        except ValueError:
            action.configure(text='脚本出错')
            tk.messagebox.showwarning('警告','最大抢课次数设置出错！\n请输入一个有效的正整数值后重新运行脚本！')
            action.configure(text="确认配置并开始运行")
            action.configure(state='enabled')    # Disable the Button Widget
            return
    else:times=100000
    head=look.get().strip()
    if '有头' in head:headless=False
    else:headless=True

    if len(kechengs)!=len(class_type) or len(old_kechengs) != len(old_class_type):
        action.configure(text='脚本出错')
        tk.messagebox.showwarning('警告','课程信息设置出错！\n课程总数与类别总数必须相同！')
        action.configure(text="确认配置并开始运行")
        action.configure(state='enabled')    # Disable the Button Widget
        return
    if mode==3 and (len(kechengs)!=len(old_kechengs) or len(class_type) != len(old_class_type)):
        action.configure(text='脚本出错')
        tk.messagebox.showwarning('警告','课程信息设置出错！\n替换课程总数与被替换总数必须相同！')
        action.configure(text="确认配置并开始运行")
        action.configure(state='enabled')    # Disable the Button Widget
        return

    if mode==3:
        Chinese=False
        for i in range(len(kechengs)):
            if isChinese(kechengs[i]):Chinese=True
        for i in range(len(old_kechengs)):
            if isChinese(old_kechengs[i]):Chinese=True            
        if Chinese:
            action.configure(text='脚本出错')
            tk.messagebox.showwarning('警告','课程信息设置出错！\n替换抢课模式下，课程信息只支持课号检索！\n请勿在课号位置填入中文字符！')
            action.configure(text="确认配置并开始运行")
            action.configure(state='enabled')    # Disable the Button Widget
            return

    # 必修实为主修
    for i in range(len(old_class_type)):
        if '必修' in old_class_type[i]:old_class_type[i]='主修'
    for i in range(len(class_type)):
        if '必修' in class_type[i]:class_type[i]='主修'  

    qiangkethread = MyThread()
    qiangkethread.setDaemon(True)

    global q
    q.put(time.time())
    q.put(qiangkethread)

    global righttime

    qiangkethread.action=action
    qiangkethread.logger=logger
    qiangkethread.win=win
    qiangkethread.monty=monty
    qiangkethread.headless=headless
    qiangkethread.mode=mode
    qiangkethread.on_time=on_time
    qiangkethread.times=times
    qiangkethread.kechengs=kechengs
    qiangkethread.class_type=class_type
    qiangkethread.old_kechengs=old_kechengs
    qiangkethread.old_class_type=old_class_type
    qiangkethread.caidan=True if (times==149248 and mode!=3 and '彩蛋' in head) else False

    qiangkethread.start()
    # print(qiangkethread.is_alive())   
    if qiangkethread.caidan: action.configure(text='狂暴模式运行中')
    action3.configure(state='enabled')    # Disable the Button Widget

def stop_qiangke():
    global q

    old_time=q.get()
    if int(3-time.time() + old_time) > 0:
        logger.info('程序终止中，请稍等...')
        sleep(int(3-time.time() + old_time))
    old_thread=q.get()
    old_thread.driver.quit()
    # quitting()
    sleep(1)
    # old_thread.setFlag(False)
    # print(qiangkethread.is_alive())
    action.configure(text="确认配置并开始运行")
    action.configure(state='enabled')    # Disable the Button Widget
    action3.configure(state='disabled')

def get_webservertime():
    global righttime
    host='www.baidu.com'
    conn=http.client.HTTPConnection(host)
    conn.request("GET", "/")
    r=conn.getresponse()
    #r.getheaders() #获取所有的http头
    ts=  r.getheader('date') #获取http头date部分
    #将GMT时间转换成北京时间
    ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
    # print(ltime)
    ttime=time.localtime(time.mktime(ltime)+8*60*60)
    # print(ttime)
    dat="date %u-%02u-%02u"%(ttime.tm_year,ttime.tm_mon,ttime.tm_mday)
    tm="time %02u:%02u:%02u"%(ttime.tm_hour,ttime.tm_min,ttime.tm_sec)
    # print (dat,tm)
    os.system(dat)
    os.system(tm)
    logger.info('系统时间校准成功!当前时间为：'+str(datetime.datetime.now())[:-7])
    righttime=True
    # input()

# Create instance
win = tk.Tk()   
# win.geometry('1150x700')
win.title("Course-Bullying-in-SJTU")

# Disable resizing the GUI
win.resizable(0,0)
# Tab Control introduced here --------------------------------------
tabControl = ttk.Notebook(win)          # Create Tab Control
tabControl.pack(expand=1, fill="both")  # Pack to make visible
# ~ Tab Control introduced here -----------------------------------------       
monty = ttk.LabelFrame(tabControl, text='程序参数设定')
monty.grid(column=0, row=0, padx=8, pady=4)
monty.pack(expand=1,fill="both")
# Modified Button Click Function

def add_pic():
    if os.path.exists('user/icon256.ico'):
        Img2=Image.open('user/paycode.png')
        global img_png2
        img_png2 = ImageTk.PhotoImage(Img2)
        label_Img2 = tk.Label(win, image=img_png2)
        label_Img2.pack(padx=5, pady=0,fill='none', expand='no', side='right',anchor='center')

        Img=Image.open('user/icon256.ico')
        global img_png
        img_png = ImageTk.PhotoImage(Img)
        label_Img = tk.Label(win, image=img_png)
        # label_Img.grid(column=1,row=2)
        label_Img.pack(padx=5, pady=0,fill='none', expand='no', side='right',anchor='center')

# Changing our Label
ttk.Label(monty, text="抢课开始时间（默认为2022-06-01 00:00:00）\n若需修改，请按照相同格式输入！").grid(column=0, row=0, sticky='W')

# Adding a Textbox Entry widget
starttime = tk.StringVar()
width=25
# starttime.set('2022-06-01 00:00:00')
starttimeEntered = ttk.Entry(monty, width=width, textvariable=starttime)
starttimeEntered.grid(column=0, row=1, sticky='W')
# Adding a Textbox Entry widget

ttk.Label(monty, text="在下面输入目标课程信息，\n若有多余位置留空即可\n左侧填写课程名称或课号，\n右侧填写对应课程类别").grid(column=0, row=2, sticky='W')
class1 = tk.StringVar()
class1Entered = ttk.Entry(monty, width=width, textvariable=class1)
class1Entered.grid(column=0, row=3, sticky='W')
class2 = tk.StringVar()
class2Entered = ttk.Entry(monty, width=width, textvariable=class2)
class2Entered.grid(column=0, row=4, sticky='W')
class3 = tk.StringVar()
class3Entered = ttk.Entry(monty, width=width, textvariable=class3)
class3Entered.grid(column=0, row=5, sticky='W')
class4 = tk.StringVar()
class4Entered = ttk.Entry(monty, width=width, textvariable=class4)
class4Entered.grid(column=0, row=6, sticky='W')

cate1 = tk.StringVar()
cate1Entered = ttk.Entry(monty, width=width, textvariable=cate1)
cate1Entered.grid(column=1, row=3, sticky='W')
cate2 = tk.StringVar()
cate2Entered = ttk.Entry(monty, width=width, textvariable=cate2)
cate2Entered.grid(column=1, row=4, sticky='W')
cate3 = tk.StringVar()
cate3Entered = ttk.Entry(monty, width=width, textvariable=cate3)
cate3Entered.grid(column=1, row=5, sticky='W')
cate4 = tk.StringVar()
cate4Entered = ttk.Entry(monty, width=width, textvariable=cate4)
cate4Entered.grid(column=1, row=6, sticky='W')

ttk.Label(monty, text="输入最大刷新次数：（默认为100000）").grid(column=1, row=0, sticky='W')
maxtime = tk.StringVar()
maxtimeEntered = ttk.Entry(monty, width=width, textvariable=maxtime)
maxtimeEntered.grid(column=1, row=1, sticky='W')

# Adding a Combobox
look = tk.StringVar()
lookChosen = ttk.Combobox(monty, width=14, textvariable=look)
lookChosen['values'] = ('无头模式(默认)', '有头模式(开发者)','彩蛋模式(狗头)')
lookChosen.grid(column=2, row=2)
lookChosen.current(0)  #设置初始显示值，值为元组['values']的下标
lookChosen.config(state='readonly')  #设为只读模式

ttk.Label(monty, text="请选择抢课模式:").grid(column=2, row=0,sticky='W')
 
# Adding a Combobox
mo = tk.StringVar()
moChosen = ttk.Combobox(monty, width=12, textvariable=mo)
moChosen['values'] = ('定点开抢模式', '持续捡漏模式','替换抢课模式')
moChosen.grid(column=2, row=1)
moChosen.current(0)  #设置初始显示值，值为元组['values']的下标
moChosen.config(state='readonly')  #设为只读模式

ttk.Label(font=('楷体 13 bold'),text="Welcome to Course-Bullying-in-SJTU! 本程序为上海交通大学本科生全自动抢课脚本！\nAuthor：@Daniel-ChenJH, 邮箱: 13760280318@163.com, 程序版本"+current_version+"。\n使用请严格遵守法律法规与学校规章制度，本人对本程序潜在使用者的行为不负任何责任！\n检查版本更新地址：https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU\n国内同步镜像：https://gitee.com/Daniel-ChenJH/Course-Bullying-in-SJTU")\
    .pack(anchor='center',padx=0, pady=1,fill='none', expand='yes', side='bottom')
# Using a scrolled Text control    
scrolW  = 60; scrolH  =  19
scr=scrolltest(win,scrolW,scrolH)
scr.pack(padx=(15,5), pady=2,fill='none', expand=0, side='left')

# Adding a Button
action = ttk.Button(monty,text="确认配置并开始运行",width=18,command=clickMe)   
action.grid(column=2,row=4,rowspan=1,ipady=5)
# Adding a Button
action2 = ttk.Button(monty,text="校准至北京时间",width=18,command=get_webservertime)   
action2.grid(column=2,row=3,rowspan=1,ipady=5)

action3 = ttk.Button(monty,text="终止本次运行",width=18,command=stop_qiangke)   
action3.grid(column=2,row=5,rowspan=1,ipady=5)
action3.configure(state='disabled')    # Disable the Button Widget


if not os.path.exists('user'):os.mkdir('user')

logger=loggetter(scr)

# Add Tooltip
createToolTip(action,'运行脚本.')
createToolTip(starttimeEntered,'抢课开始时间.')
createToolTip(class1Entered,'目标课程1.')
createToolTip(class2Entered,'目标课程2.')
createToolTip(class3Entered,'目标课程3.')
createToolTip(class4Entered,'目标课程4.')
createToolTip(cate1Entered,'课程1对应类别.')
createToolTip(cate2Entered,'课程2对应类别.')
createToolTip(cate3Entered,'课程3对应类别.')
createToolTip(cate4Entered,'课程4对应类别.')
createToolTip(maxtimeEntered,'最大刷新次数.')
createToolTip(moChosen, '选择抢课模式.')
createToolTip(lookChosen, '(开发者)选择运行模式.')
createToolTip(scr,'程序日志.')

# 一次性控制各控件之间的距离
for child in monty.winfo_children(): 
    child.grid_configure(padx=30,pady=3)

waitbox=[starttime,maxtime,mo,look,class1,class2,class3,class4,cate1,cate2,cate3,cate4]

# 程序图标信息 256


def setIcon():
    tmp = open("user/icon512.ico","wb+")  
    tmp.write(base64.b64decode(Icon512()))
    tmp.close()
    tmp = open("user/icon256.ico","wb+")  
    tmp.write(base64.b64decode(Icon256()))
    tmp.close()    
    tmp = open("user/paycode.png","wb+")  
    tmp.write(base64.b64decode(paycode()))
    tmp.close()
    win.iconbitmap("user/icon512.ico") 
    # os.remove("user/icon512.ico")

def check_chrome():

    f=open("user/conf.ini",'w',encoding='utf-8')
    if pl=='win':f.write('[driver]\nabsPath=user\chromedriver.exe\nurl=https://chromedriver.storage.googleapis.com/')
    elif pl=='mac':f.write('[driver]\nabsPath=user/chromedriver\nurl=https://chromedriver.storage.googleapis.com/')
    f.close()

    logger.info("-*-*-*-*-*-*-*-*-*-*-*-*-*-\n\n程序启动成功！程序版本号："+current_version+"\n\nCourse-Bullying-in-SJTU: On-Time Automatic Class Snatching System\n\nAuthor:\t@ Daniel-ChenJH (13760280318@163.com)\nFirst Published on Februry 25th, 2021 , current version: "+current_version+" .\n\nPlease read file \'readme.md\' carefully before running the program!\n")
    c=chrome_checker('user/conf.ini',logger)

    cstr=['未安装Chrome浏览器或浏览器版本获取失败，请重新安装Chrome浏览器后再试！','chromedriver版本获取失败，请删除\'user/chromedriver\'后再试！','chromedriver驱动下载失败，请自行前往 https://registry.npmmirror.com/binary.html?path=chromedriver 下载对应版本驱动，解压后放在user文件夹下！']
    
    if c.exp:
        logger.warning('Chrome配置环节出错，错误类型：'+cstr[int(c.exp)-1])
        action.configure(text='无法运行')
        action.configure(state='disabled')    # Disable the Button Widget
        tk.messagebox.showwarning('警告',cstr[int(c.exp)-1])

    setIcon()
    add_pic()
    if not c.exp:logger.info('前期准备工作完成！')


def is_old(old_ver):
    # name：xxx/xxx
    # https://api.github.com/repos/Daniel-ChenJH/Course-Bullying-in-SJTU
    # print(api_url % name)
    old_ver=float(old_ver.split('v')[1])*10
    try:
        api_url = "https://api.github.com/repos/Daniel-ChenJH/Course-Bullying-in-SJTU"
        all_info = requests.get(api_url,timeout=5).json()
        new_time = time.mktime(time.strptime(all_info["updated_at"], "%Y-%m-%dT%H:%M:%SZ"))
        new_time=new_time+28800
        for any in all_info["topics"]:
            new_ver=int(any.split('v')[1]) if any.startswith('v') else 0

        return (new_ver > old_ver),new_time,'v'+str(new_ver)[0]+'_'+str(new_ver)[1]
    except:
        # URL is limited or VPN is used
        try:
            url=r'https://ghproxy.com/https://raw.githubusercontent.com/Daniel-ChenJH/Course-Bullying-in-SJTU/main/README.md'
            info=urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
            new_ver=float(info[info.find('Course-Bullying-in-SJTU'):info.find('！')].split('v')[-1])*10
            return (new_ver > old_ver),'','v'+str(new_ver)[0]+'_'+str(new_ver)[1]
        except:
            return False,'0','0'


def download_newfile():
    download_url = "https://ghproxy.com/https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU/archive/WIN64.zip" if pl=='win' else "https://ghproxy.com/https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU/archive/MAC.zip"
    status=request_big_data(download_url)
    return status

def process_bar(current, total, prefix='', auto_rm=True):
    bar = '=' * int(current / total * 20)
    bar = f' {prefix} |{bar.ljust(20)}| ({current}/{total}) {current / total:.1%} | '
    # bar = f' {prefix} |{bar.ljust(20)}| {current / total:.1%} | '
    # print(bar, end='\r', flush=True)
    logger.info(bar)
    # if auto_rm and current == total:
    #     print(end=('\r' + ' ' * len(bar) + '\r'), flush=True)

def request_big_data(url):
    name = url.split('/')[-1]
    # 获取文件名
    try:
        try:size=int(urllib.request.urlopen(url,timeout=5).headers['content-length'])/1024
        except:size=12110 if pl=='win' else 29400
        finally:
            logger.info('更新中，文件大小： '+str(round(size/1024,2))+' MB')
            r = requests.get(url, stream=True,timeout=10)
            # stream=True 设置为流读取
            with open("new-"+str(name), "wb") as pdf:
                i=0
                a=time.time()
                for chunk in r.iter_content(chunk_size=512):
                    # 每2048个字节为一块进行读取
                    if chunk:
                        # 如果chunk不为空
                        if i%2400==0: process_bar(i/2,int(size), '更新进度', auto_rm=True)
                        pdf.write(chunk)
                        i=i+1
            logger.info('更新用时（秒）：'+str(round(time.time()-a,2)))
        return True
    except requests.exceptions.ConnectionError:
        logger.warning(traceback.format_exc())
        logger.info('程序更新失败，无法访问Github，请前往https://gitee.com/Daniel-ChenJH/Course-Bullying-in-SJTU自行下载！')
        return False
    except:
        logger.warning(traceback.format_exc())     
        logger.info('程序更新失败，请前往https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU自行下载！')
        return False

def get_new_ver_info():
    urls=[r'https://ghproxy.com/https://raw.githubusercontent.com/Daniel-ChenJH/Course-Bullying-in-SJTU/main/README.md',\
        r'https://cdn.jsdelivr.net/gh/Daniel-ChenJH/Course-Bullying-in-SJTU@main/README.md']
    rstr=''
    for url in urls:
        try:
            info=urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
            a=info.find('更新说明')
            b=0
            for i in range(50):
                if info[a-i]=='#':
                    b=a-i
                    break
            c=b+info[b+1:].find('#')
            d=b+info[b+1:].find('\n')
            info=info[:d+1]+info[d+2:]
            rstr=info[b:c].strip()
            break
            # print(info[b:c].strip())
        except:continue
    return rstr

def check_newest_version(old_ver):
    

    # timethread=threading.Thread(target=showtime)
    # timethread.setDaemon(True)
    # timethread.start()
    
    ttk.Label(monty, text="请注意，若选择替换抢课模式，则请按照希望把\n第二行替换成第一行、希望把第四行替换\n成第三行的顺序正确填写！\n请务必在初次使用前校准时间\nMac系统需自行调整系统时间！").grid(column=1, row=2, sticky='W')
    if pl=='mac':
        head='MAC' 
        end='.dmg'
    elif pl=='win':
        head='WIN64'
        end='.exe'
    cur_file=head+'-Course-Bullying-in-SJTU-' +current_version.replace('.','_')+end
    old,newtime,new_ver = is_old(old_ver)
    if old:
        new_ver_info=get_new_ver_info()
        if newtime:newtime = '于 '+time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime(newtime))
        a=tkinter.messagebox.askquestion('提示', '发现程序'+newtime+' 更新: '+new_ver+' 版，本程序目前为: v'+old_ver[1]+'_'+old_ver[3]+' 版，请问是否下载更新？'+'\n'+new_ver_info)
        if a=='yes':
            logger.info('下载新版中，耗时大约20秒，请耐心等待......')
            new_file=head+'-Course-Bullying-in-SJTU-' +new_ver+end
            if download_newfile():
                try:
                    file_name='new-'+head+'.zip'
                    file_zip = zipfile.ZipFile(file_name, 'r')
                    for file in file_zip.namelist():
                        file_zip.extract(file)
                    file_zip.close()
                    os.remove(file_name)    
                    for f in os.listdir('Course-Bullying-in-SJTU-'+head):
                        shutil.move('Course-Bullying-in-SJTU-'+head+'/'+f,f)
                    shutil.rmtree('Course-Bullying-in-SJTU-'+head, ignore_errors=True, onerror=None)
                    logger.info('更新完成！请使用更新版程序： Course-Bullying-in-SJTU-'+new_ver+' ！')
                    logger.info('新版保存地址：'+os.getcwd()+'/'+head+'-Course-Bullying-in-SJTU-'+new_ver+end)

                    tk.messagebox.showinfo('提示','更新完成！请使用更新版程序： Course-Bullying-in-SJTU-'+new_ver+' ！')
                    if pl=='win':
                        # 更新bat文件
                        fp=open(os.path.join(os.getcwd(),'refresh.bat'),'w',encoding='utf-8')
                        temp='"\ndel /f /s /q   '+cur_file+'\ndel %0'
                        fp.write('@echo off\ncd /d %~dp0\necho 我将删除自身并退出\ntaskkill /f /im "'+cur_file+temp)
                        fp.close()

                    shell(new_file)
                    # try:
                    #     # os.system('taskkill /IM try.exe /F')
                    #     # input('我将删除自身并保留try2')
                    #     os.system('t.bat')
                    # except:
                    #     logger.info(cur_file+'problem!!!')
                    #     logger.warning(traceback.format_exc())
                    #     sleep(10)
                    #     raise SystemExit
                    sys.exit(0)
                except SystemExit:
                    sys.exit(0)
                except:
                    logger.warning(traceback.format_exc())
                    tk.messagebox.showwarning('警告','程序更新失败，请前往https://gitee.com/Daniel-ChenJH/Course-Bullying-in-SJTU自行下载最新版！')
                    sys.exit(0)
            else:
                tk.messagebox.showwarning('警告','程序更新失败，请前往https://gitee.com/Daniel-ChenJH/Course-Bullying-in-SJTU自行下载最新版！')
                sys.exit(0)
    elif new_ver=='0':
        message='程序检查更新失败，本程序版本为: '+current_version+'。请前往https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU自行检查更新！'
        tk.messagebox.showwarning('警告',message)
        logger.info(message)
    else:logger.info('当前程序已是最新版！')

# def showtime():
#     t="\t本机当前时间为:\n"+str(datetime.datetime.now())
#     a=ttk.Label(monty, text=t)
#     a.grid(column=2, row=2, sticky='W')
#     # clock=ttk.Label(monty, text=).grid(column=2, row=2, sticky='W')
#     a.after(150,showtime)

# 这部分用到了windows系统
def check_admin():
    if is_admin():
        pass
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if pl=='win':check_admin()
check_newest_version(current_version)
check_chrome()

load_config()

# Place cursor into starttime Entry
starttimeEntered.focus()      
#======================
# Start GUI
#======================
win.mainloop()