# -*- encoding: utf-8 -*-
'''
@File    :   qiangke.py
@Time    :   2022/06/05 15:00:00
@Author  :   Daniel-ChenJH
@Email   :   13760280318@163.com
@Version    :   5.5
@Descriptions :   Course-Bullying-in-SJTU
                    上海交通大学全自动抢课脚本,请保证本机Windows10系统已经安装了Chrome浏览器
'''

# The imported libs: 
import logging
import datetime
import traceback
import sys
import requests
import json
import time
import os
from PIL import Image
import threading
from os import remove, path
from time import sleep,strftime,localtime
from PIL import Image,ImageTk
from urllib3.exceptions import ProtocolError
from selenium.common.exceptions import TimeoutException,NoSuchElementException,InvalidSessionIdException,ElementNotInteractableException,ElementClickInterceptedException,StaleElementReferenceException,NoSuchWindowException,WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tkinter as tk
from urllib3.exceptions import NewConnectionError,MaxRetryError
import smtplib
from email.mime.text import MIMEText

def isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

# 显示二维码的子线程
def showpic(monty,count):
    global img_png

    Img=Image.open('user/qrcode.jpg')
    img_png = ImageTk.PhotoImage(Img)
    label_Img = tk.Label(monty, image=img_png)
    # label_Img.grid(column=1,row=2)
    label_Img.pack(padx=5, pady=3,fill='none', expand='no', side='right')
    # label_Img.grid(column=2,row=3,rowspan=1,ipady=5)
    tk.messagebox.showinfo('提示','请在按下\'确定\'后的15秒内用微信扫描弹出的二维码完成登录！')
    sleep(14)
    label_Img.destroy()
    # Img.show()

def search_index(str,key):
    # 返回特定字符在字符串中索引的下标列表
    lstKey = []
    str = str
    key = key
    countStr = str.count(key)
    if countStr < 1:pass
    elif countStr == 1:
        indexKey = str.find(key)
        lstKey.append(indexKey)
    else:
        indexKey = str.find(key)
        lstKey.append(indexKey)
        while countStr > 1:
            str_new = str[indexKey+1:len(str)+1]
            indexKey_new = str_new.find(key)
            indexKey = indexKey+1 +indexKey_new
            lstKey.append(indexKey)
            countStr -= 1
    return lstKey

def login(driver,win,logger,monty):
    try:
        count=0
        try:
            driver.get('https://i.sjtu.edu.cn/')        
            # 尝试使用cookie登录
            if path.exists('user/cookie.txt'):
                f1 = open('user/cookie.txt','r')
                cookie = f1.read()
                cookie =json.loads(cookie)
                driver.delete_all_cookies()
                expire,temp=9999999999,9999999999
                for c in cookie:
                    if 'expiry' in cookie:
                        if c['expiry']<expire:expire=c['expiry']
                        del cookie['expiry']
                    if 'domain' in cookie:del cookie['domain']
                # 过期时间超过60秒
                if  int(expire)-int(time.time())>60:
                    for c in cookie:
                        if 'expiry' in cookie:del cookie['expiry']
                        driver.add_cookie(c)
                    driver.refresh()
                    sleep(0.5)
                    driver.switch_to.default_content()
                    try:
                        lanmu=driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a')
                        cur_user=driver.find_element_by_xpath('/html/body/div[1]/div/ul/li[2]/a/span/font')
                        cur_uid=driver.find_element_by_xpath('//*[@id="sessionUserKey"]').get_attribute('value')
                        logger.info('使用cookie登录成功！当前用户：'+cur_user.text+' '+cur_uid)
                        origin= driver.current_window_handle
                        driver.implicitly_wait(5)
                        return driver,origin,cur_user.text,cur_uid                    
                    # except TimeoutException:
                    #     logger.warning(traceback.format_exc())
                    #     logger.info('使用cookie登录失败，请删除文件\'cookie.txt\'后尝试重新运行程序……')
                    #     driver.quit()
                    #     quitting(logger,win)
                    except (NoSuchElementException,TimeoutException):
                        logger.info('使用cookie登录失败！')
                        driver.delete_all_cookies()
                        driver.refresh()
                        driver.switch_to.default_content()
                        login = WebDriverWait(driver,3,0.1).until(lambda x:driver.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div/div/form/div[6]/div/a/img') )
            logger.info('正在使用二维码登录……')
        except TimeoutException:
            driver.execute_script('window.stop()')
        
        try:driver.get('https://i.sjtu.edu.cn/jaccountlogin')
        except TimeoutException:driver.execute_script('window.stop()')    
        while(1):
            try:
                count+=1
                if count==4:
                    logger.info('失败次数太多，请重新运行程序！')
                    driver.quit()
                    quitting(logger,win)
                    if os.path.exists('user/cookie.txt'):remove('user/cookie.txt')

                qrcodelink=driver.find_element_by_xpath('//*[@id="qr-img"]').get_attribute('src').strip()
                qrcode = requests.get(qrcodelink, timeout=5)

                # 将获取的内容保存为后缀为jpg的图片
                fp = open("user/qrcode.jpg", "wb")
                fp.write(qrcode.content)
                fp.close()
                # img = img.resize((width, height),Image.ANTIALIAS)
                mythread = threading.Thread(target=showpic,args=(monty,count))
                mythread.setDaemon(True)
                mythread.start()
                logger.info('请在按下\'确定\'按钮后的15秒内完成扫码确认登录，此后程序将继续运行！')
                sleep(15)
                driver.switch_to.default_content()
                lanmu=driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a') # 用来确保登陆成功
                cur_user=driver.find_element_by_xpath('/html/body/div[1]/div/ul/li[2]/a/span/font')
                cur_uid=driver.find_element_by_xpath('//*[@id="sessionUserKey"]').get_attribute('value')
                logger.info('登录成功！当前用户:'+cur_user.text+' '+cur_uid)
                # 记录cookie
                cookies = driver.get_cookies()
                f1 = open('user/cookie.txt', 'w')
                f1.write(json.dumps(cookies))
                f1.close()         
                break        
            except NoSuchElementException as e:
                logger.info('登录失败，请扫码新弹出的二维码重试！若二维码一段时间后仍未弹出，请检查你的网络环境后重新运行程序！')
                driver.refresh()
                sleep(1)

        origin= driver.current_window_handle
        driver.implicitly_wait(5)
    except (WebDriverException,NoSuchWindowException,MaxRetryError):
        logger.info('\n\n程序被使用者主动终止！\n\n')
        if count<=1:logger.info('请检查您的网络环境后再试！')
        sys.exit(0)

    return driver,origin,cur_user.text,cur_uid

def waitbegin(logger,mode,on_time):
    if mode==1 or mode==3:
        while True:
            now_time=datetime.datetime.now()
            if now_time<on_time and int((on_time-now_time).seconds)>2:
                logger.info('未到设定的抢课开放时间，程序等待中')
                if int((on_time-now_time).seconds)>60:
                    sleep(60) 
                elif int((on_time-now_time).seconds)>10:
                    sleep(10)
                else:sleep(2)     
            else:
                if now_time>=on_time:break   
    logger.info('程序开始抢课！\n')

def search_in(logger,win,driver,mode,kechengs,stat,handle,class_type,new):
    if handle in new.keys():bias=0
    else:bias=len(new)
    num_bias=0

    classfind=False
    cur_class=kechengs[stat[handle][1]+bias]
    cur_teacher=''
    if ':' in cur_class:cur_class,cur_teacher=cur_class.strip().split(':')
    cur_class_type=class_type[stat[handle][1]+bias]

    try:
        inp = WebDriverWait(driver,1,0.1).until(lambda x:driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input') )
        inp.clear()
        inp.send_keys(cur_class)
        # print('课程输入'+kechengs[stat[handle][1]+bias])
        go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
        go.click()
        sleep(0.5)
        typebox=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/ul')
        types=typebox.find_elements_by_tag_name('a')

    except NoSuchElementException as e:
        unavailable=driver.find_element_by_xpath('//*[@id="innerContainer"]/div[4]/div[2]/div/span')
        if unavailable.is_displayed():
            logger.info('程序错误，当前不属于选课阶段，请自行确认抢课开放时间。')
            driver.quit()
            quitting(logger,win)
            sys.exit(0)
        else:
            logger.info('程序好像出现了一些问题……')
            logger.info(e)
        
    for type in types:
        if cur_class_type in type.text:
            type.click()
            classfind=True
            break
    if not classfind:
        logger.info('课程： '+cur_class+' 与类别：'+cur_class_type+'  关系对应出错，将暂时跳过此门课程（及其组合）！')
        stat[handle][0]=4
        return driver,classfind,stat,kechengs,num_bias

    loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[15]')
    try:
        WebDriverWait(driver,1,0.1).until(EC.visibility_of_element_located(loc))
    except TimeoutException:pass
    driver.implicitly_wait(0.5)

    # sleep(0.8)         
    sleep(0.4)
    rongliang=10+len(driver.find_elements_by_xpath("/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/thead/tr/th"))
    # 检查服务器情况并尝试等待
    kongcount=0
    while rongliang < 13:
        kongcount+=1
        sleep(1)
        rongliang=10+len(driver.find_elements_by_xpath("/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/thead/tr/th"))
        if rongliang==10 or kongcount==3:
            all_window_handles = driver.window_handles
            logger.info('在类别：'+str(cur_class_type)+' 下查找不到课程：'+str(cur_class)+' 将跳过此门课程（及其组合）！')
            stat[handle][0]=4
            if mode==3 and handle in new.keys():
                stat[all_window_handles[new[handle][1]+len(new)+1]][0]=4
            elif mode==3:
                stat[all_window_handles[all_window_handles.index(handle)-len(new)]][0]=4     
            return driver,classfind,stat,kechengs,num_bias    
    
    # 此处教学信息服务网的列表栏序号对应：
    # 12课号13老师14时间15地点16学院17备注18性质19模式20语言21已满22已选/容量23未知24按钮
    # 2022.06.10

    #带:号的老师检索
    if cur_teacher:
        classfind=False
        total_classes=len(driver.find_elements_by_xpath('/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr'))
        for i in range(1,total_classes+1):
            xpath='/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(i)+']/td[13]'
            teachers=driver.find_element_by_xpath(xpath)
            if cur_teacher in teachers.text:
                classfind=True
                new_class=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(i)+']/td[12]/a')
                kechengs[stat[handle][1]+bias]=new_class.text.strip()
                driver=search_again(logger,driver,kechengs,stat,handle,class_type,{})
                break
        if not classfind:
            logger.info('未找到老师：'+cur_teacher+' 任教的课程： '+cur_class+' ，将暂时跳过此门课程（及其组合）！')
            stat[handle][0]=4

    num_bias=1
    if not isChinese(cur_class):
        # 是课号检索
        cur_class=cur_class.split(')')[1][1:].strip() if ')' in cur_class else cur_class # 去掉课号中的学期部分
        if '-' in cur_class: # 是带尾号的精确课号检索
            total_classes=len(driver.find_elements_by_xpath('/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr'))
            for i in range(1,total_classes+1):
                # xpath='/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(i)+']/td[12]'
                xpath = (By.XPATH, '/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(i)+']/td[12]')
                try:
                    WebDriverWait(driver,1,0.1).until(EC.visibility_of_element_located(xpath))
                    driver.implicitly_wait(3)
                except TimeoutException:pass
                class_label=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(i)+']/td[12]')
                logger.info(class_label.text)
                if str(cur_class) == str(class_label.text).split(')')[1][1:].strip():  # '(2022-2023-1)-MARX1205-3' 需要完全一致
                    num_bias=i
                    break       
        # logger.info(str(num_bias)+str(cur_class))
    
    return driver,classfind,stat,kechengs,num_bias


def search_again(logger,driver,kechengs,stat,handle,class_type,new):
    if handle in new.keys():bias=0
    else:bias=len(new)
    driver.refresh()
    sleep(1)
    driver.implicitly_wait(0.5)
    inp=driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input')
    inp.clear()
    inp.send_keys(kechengs[stat[handle][1]+bias])
    
    # 查询按钮
    go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
    go.click()
    sleep(0.5)
    typebox=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/ul')
    types=typebox.find_elements_by_tag_name('a')
    for type in types:
        if class_type[stat[handle][1]+bias] in type.text:
            type.click()
            loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[15]')
            try:
                WebDriverWait(driver,1,0.1).until(EC.visibility_of_element_located(loc))
            except TimeoutException:pass
            driver.implicitly_wait(3)
            break
    sleep(0.3)
    return driver

def quitting(logger,win):
    logger.info("Please 'Star' the program of Daniel-ChenJH on Github if you think it's a quite good one. ")   
    logger.info('Link to \'Course-Bullying-in-SJTU\' in Github : https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU')
    # my_file = 'user/button.png' # 文件路径
    # if path.exists(my_file): # 如果文件存在
    #     remove(my_file) # 则删除
    my_file = 'user/qrcode.jpg' # 文件路径
    if path.exists(my_file): # 如果文件存在
        remove(my_file) # 则删除    
    logger.info('程序已完成！请立即自行移步至教学信息服务网 https://i.sjtu.edu.cn 查询确认抢课结果！\n\n')
    tk.messagebox.showinfo('提示','程序正常结束！请务必仔细阅读程序日志！\n创作不易，请勿白嫖！\n如果您觉得本程序还不错，欢迎前往以下网站并点亮一个小星星！\nhttps://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU\n也欢迎您扫码程序面板右侧二维码打赏作者，感谢您的支持！')
    # win.quit()


def simulater(action,driver,logger,mode,on_time,monty,win,old_kechengs,old_class_type,kechengs,class_type,times,kuangbao,kuangbao_uid_list,headless=True):
    start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    
    driver,origin,cur_user,cur_uid=login(driver,win,logger,monty)
    kuangbao=kuangbao and cur_uid in kuangbao_uid_list

    if kuangbao: 
        action.configure(text='狂暴模式运行中')
        action.configure(state='disabled')
        logger.info('尊敬的'+cur_user+' '+cur_uid+'，'+'恭喜您成功激活狂暴模式！程序将尝试用最高速度抢课，并自适应服务器的稳定性！')
    else:
        action.configure(text='普通模式运行中')
        tk.messagebox.showinfo('抢课模式提示','当前运行于普通模式，开通狂暴模式即可享受3倍抢课速度！\n点击"确定"继续运行本程序！')
        logger.info('当前运行于普通模式，开通狂暴模式即可享受3倍抢课速度！')
    # 准点开抢模式，阻塞程序    
    waitbegin(logger,mode,on_time)
    failcount=0
    waittime=0 if kuangbao else 0.7
    sessionflag = True

    while failcount<13:
        try:
            # 点击下拉栏尝试进入选课页面
            for j in range(len(kechengs)+len(old_kechengs)):
                now=driver.window_handles
                driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a').click()
                driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/ul/li[3]/a').click()
                WebDriverWait(driver, 2, 0.05).until(EC.new_window_is_opened(now))
            all_window_handles = driver.window_handles       
            # print(all_window_handles) 
            # 添加状态记录字典 
            k,n,i=0,0,0
            stat={}
            old_stat={}
            for handle in all_window_handles:
                i+=1
                if handle !=origin:
                    if i<len(kechengs)+2:
                        stat[handle]=[0,k]
                        k+=1
                    else:
                        old_stat[handle]=[0,n]
                        n+=1
            
            # 此时已经进入选课界面
            httperror=0
            
            logger.info('持续查询刷新中......')
            num_bias_list=[]

            # 开始查询刷新
            for q in range(times):
                tmp=list(stat.values())
                st=[]

                for t in range(len(tmp)):
                    st.append(tmp[t][0])
                if 0 not in st:break    #所有课程都抢课完成

                for handle in all_window_handles:
                    all_kechengs=kechengs+old_kechengs
                    all_class_type=class_type+old_class_type
                    all_stat=stat.copy()
                    all_stat.update(old_stat)
                    # 第一次进入刷新，输入课程信息
                    if q==0 and handle!=origin and all_stat[handle][0]==0:
                        driver.switch_to.window(handle)
                        driver,classfind,all_stat,all_kechengs,class_bias=search_in(logger,win,driver,mode,all_kechengs,all_stat,handle,all_class_type,stat)
                        kechengs=all_kechengs[:len(kechengs)]
                        old_kechengs=all_kechengs[len(kechengs):]

                        if mode==3 and handle in stat.keys() and not classfind:all_stat[all_window_handles[stat[handle][1]+len(kechengs)+1]][0]=4
                        if mode==3 and handle not in stat.keys() and not classfind:all_stat[all_window_handles[all_window_handles.index(handle)-len(kechengs)]][0]=4
                        for a,b in all_stat.items():
                            if a in stat.keys():
                                stat[a]=b
                            else:old_stat[a]=b
                        
                        if class_bias:num_bias_list.append(class_bias)
                        if mode==3 or not classfind:continue
                        # 模式三下需完成所有查询后再开始抢课

                    if handle!=origin and all_window_handles.index(handle)<len(kechengs)+1 and stat[handle][0]==0:
                        if handle!=driver.current_window_handle: driver.switch_to.window(handle)
                        # 只是用来确认网络加载好了，这个变量没啥用
                        loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[15]')
                        try: WebDriverWait(driver,1,0.02).until(EC.visibility_of_element_located(loc))
                        except TimeoutException:pass
                        
                        if not kuangbao:driver.implicitly_wait(0.5)
                        if waittime:sleep(waittime)
                        # 这个bias是10，不能改
                        rongliang=10+len(driver.find_elements_by_xpath("/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/thead/tr/th"))
                        # logger.info(rongliang)
                        kongcount=0
                        # 检查服务器情况并尝试等待
                        whileflag=False
                        while rongliang < 13:
                            kongcount+=1
                            sleep(1)
                            rongliang=10+len(driver.find_elements_by_xpath("/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/thead/tr/th"))
                            if (kongcount==3 and not kuangbao):
                                if q<5:
                                    logger.info('可能是服务器不稳定或课程输入出现问题，请检查后重新运行')
                                    driver.quit()
                                    quitting(logger,win)
                                    sys.exit(0)
                                else:
                                    # 正常刷新过，说明是服务器问题
                                    kongcount=0
                                    logging.info('服务器不稳定，尝试重连，程序小歇一会...')
                                    sleep(3)
                                    driver=search_again(logger,driver,all_kechengs,all_stat,handle,all_class_type,stat)
                                    # sleep(1.5)
                                    continue
                        
                        if whileflag:continue
                        status_check_xpath='//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(num_bias_list[stat[handle][1]])+']/td['+str(rongliang)+']'
                        # logger.info(status_check_xpath)
                        xuan_btn_here='/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(num_bias_list[stat[handle][1]])+']/td['+str(rongliang+3)+']/button'
                        if mode==3:tuixuan_btn_here='/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr['+str(num_bias_list[stat[handle][1]+len(kechengs)])+']/td['+str(rongliang+3)+']/button'
                        
                        status=driver.find_element_by_xpath(status_check_xpath)
                        if status.is_displayed():
                            # 显示已满
                            if (q+1)%10==0 or q==0:
                                logger.info(str(kechengs[stat[handle][1]])+'  try_time== '+str(q+1)+' 无空余名额 '+status.text)
                            go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
                            go.click()
                        else:
                            try:
                                sleep(0.2) 
                                temp=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath(xuan_btn_here))
                                kongcount=0
                                # 检查服务器情况并尝试等待
                                while kongcount<4 and '选' not in temp.text:
                                    temp=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath(xuan_btn_here))
                                    kongcount+=1
                                    sleep(1)
                                
                                if '选' not in temp.text:
                                    logger.info(str(kechengs[stat[handle][1]])+'  try_time== '+str(q+1)+' 服务器不稳定'+str(temp.text))
                                    httperror+=1
                                    if httperror>1:
                                        httperror=0
                                        logger.info('尝试重连服务器，程序小歇一会...')
                                        sleep(1)
                                        driver=search_again(logger,driver,all_kechengs,all_stat,handle,all_class_type,stat)
                                        # sleep(1.5)
                                    continue

                                if temp.text=='选课': 
                                    if mode==3:
                                        # 退掉对应的那一门课
                                        logger.info('发现 '+kechengs[stat[handle][1]]+' 有空余名额，执行替换操作 '+temp.text)
                                        driver.switch_to.window(all_window_handles[stat[handle][1]+len(kechengs)+1])
                                        driver.implicitly_wait(0.5)
                                        tuixuan=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath(tuixuan_btn_here))
                                        tuixuan.click()
                                        driver.implicitly_wait(3)
                                        try:
                                            confirm=driver.find_element_by_xpath('//*[@id="confirmModal"]/div/div/div[2]/div/div/p')
                                            if confirm.is_displayed():
                                                tuixuanqueding=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath('//*[@id="btn_confirm"]'))
                                                if '确' in tuixuanqueding.text:
                                                    tuixuanqueding.click()
                                                    logger.info('正在退选 '+str(old_kechengs[stat[handle][1]])+'...')
                                                    sleep(0.2)
                                                    driver.implicitly_wait(0.5)
                                                    logger.info('退选成功！')
                                                    # 换回之前的窗口
                                                else:
                                                    driver.switch_to.window(handle)
                                                    driver.implicitly_wait(0.5)
                                                    continue
                                                driver.switch_to.window(handle)
                                                driver.implicitly_wait(0.5)

                                                ### 此处必须刷新网页缓存，删不了
                                                # 2022.06.20
                                                driver=search_again(logger,driver,all_kechengs,all_stat,handle,all_class_type,stat)
                                                ### 防止出现“假选课”情况
                                                
                                                try:WebDriverWait(driver,1,0.1).until(EC.text_to_be_present_in_element((By.XPATH, xuan_btn_here),"选课"))
                                                except:pass
                                                temp=driver.find_element_by_xpath(xuan_btn_here)
                                                kongcount=0

                                                # 检查服务器情况并尝试等待
                                                while kongcount<4 and '选' not in temp.text:
                                                    temp=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath(xuan_btn_here))
                                                    kongcount+=1
                                                    sleep(1)
                                                
                                                if '选' not in temp.text:
                                                    logger.info(str(kechengs[stat[handle][1]])+'  try_time== '+str(q+1)+' 服务器不稳定'+str(temp.text))
                                                    logger.info('服务器不稳定！请稍后重试...')
                                                    logger.info('请立即前往教学信息服务网补选刚刚退掉的课程： '+str(old_kechengs[stat[handle][1]])+' !!!')
                                                    driver.quit()
                                                    quitting(logger,win)
                                                    sys.exit(0)

                                        except NoSuchElementException as e:
                                            logger.warning(traceback.format_exc())
                                            logger.info('程序退选失败，将在下次循环继续尝试')
                                            driver.switch_to.window(handle)
                                            driver.implicitly_wait(0.5)
                                            continue
                                    # print('temp按钮内容： '+temp.text)
                                    temp.click()
                                    logger.info('点击选课！')
                                    sleep(0.3)
                                    driver.implicitly_wait(2)
                                    try:WebDriverWait(driver,1,0.1).until(EC.text_to_be_present_in_element((By.XPATH, xuan_btn_here),"退选"))
                                    except TimeoutException:pass
                                    temp2=driver.find_element_by_xpath(xuan_btn_here)
                                    # print('temp2按钮内容： '+temp2.text)
                                    kongcount=0

                                    # 检查服务器情况并尝试等待
                                    while kongcount<4 and '选' not in temp2.text:
                                        temp2=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath(xuan_btn_here))
                                        kongcount+=1
                                        sleep(0.5)
                                    
                                    if '选' not in temp2.text:
                                        logger.info(str(kechengs[stat[handle][1]])+'  try_time== '+str(q+1)+' 服务器不稳定'+str(temp2.text))
                                        logger.info('服务器不稳定！请稍后重试...')
                                        logger.info('请立即前往教学信息服务网补选刚刚退掉的课程： '+str(old_kechengs[stat[handle][1]])+' !!!')
                                        driver.quit()
                                        quitting(logger,win)
                                        sys.exit(0)
                                    try:
                                        if temp2.text=='退选': 
                                            logger.info('\n=============== '+str(kechengs[stat[handle][1]])+' , Success! try_time== '+str(q+1)+' ===============\n')
                                            stat[handle][0]=1
                                        elif temp2.text=='选课':                                    
                                            temp2.click()
                                            logger.info('好像抢课程：'+str(kechengs[stat[handle][1]])+'中出现了些什么问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!'+str(temp2.text))
                                            stat[handle][0]=3
                                            sleep(2)
                                    except (ElementClickInterceptedException,StaleElementReferenceException):
                                        waittime+=0.05
                                        logger.warning(traceback.format_exc())
                                        logger.info('服务器不稳定，将在此后稍许延长等待时间为： '+str(waittime)+' 秒试试')
                                        driver=search_again(logger,driver,all_kechengs,all_stat,handle,all_class_type,stat)
                                        sleep(0.5)
                                    except Exception as e:
                                        logger.warning(traceback.format_exc())
                                        logger.info(e.__class__.__name__)
                                        logger.info(str(e)+'Error! 好像抢课程：'+str(kechengs[stat[handle][1]])+'中出现了些什么问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!'+str(temp2.text))
                                        stat[handle][0]=3
                                        sleep(2)
                                elif temp.text=='退选' :
                                    logger.info('您之前已经选上这门课了！ '+str(kechengs[stat[handle][1]]))
                                    stat[handle][0]=2
                            except Exception as e:
                                logger.warning(traceback.format_exc())
                                logger.info(str(kechengs[stat[handle][1]])+' try_time== '+str(q+1)+' failed '+status.text)
                                logger.info('failed because of :'+str(e.__class__.__name__)+str(e)+' Retrying!')
            if q==times-1 or 0 not in st:break
        except (StaleElementReferenceException,ElementClickInterceptedException):
            logger.warning(traceback.format_exc())
            waittime+=0.05
            logger.info('服务器不稳定，将在此后稍许延长等待时间为： '+str(waittime)+' 秒试试')
            driver=search_again(logger,driver,all_kechengs,all_stat,handle,all_class_type,stat)
            failcount+=1
            sleep(0.5)
            all_window_handles = driver.window_handles
            for handle in all_window_handles:
                if handle !=origin:
                    driver.switch_to.window(handle)
                    driver.implicitly_wait(0.5)
                    driver.close()
            driver.switch_to.window(origin)
            driver.implicitly_wait(0.5)
            sleep(1)

        except (NoSuchWindowException,InvalidSessionIdException,ProtocolError,NewConnectionError,MaxRetryError):
            logger.info('\n\n程序被使用者主动终止！\n\n')
            sessionflag = False
            break            
        except Exception as e:
            failcount+=1
            logger.warning(traceback.format_exc())
            if failcount==1 and q>800: sleep(3)
            logger.info('程序第'+str(failcount)+'次异常，异常原因：'+str(e.__class__.__name__)+'  '+str(e)+' 重试中...')
            all_window_handles = driver.window_handles
            for handle in all_window_handles:
                if handle !=origin:
                    driver.switch_to.window(handle)
                    driver.implicitly_wait(0.5)
                    driver.close()
            driver.switch_to.window(origin)
            driver.implicitly_wait(0.5)
            sleep(5)       

    if failcount==2:logger.info('好像出了些什么问题，……请自行登录网站尝试抢课，并对照文件\'readme.md\'确保无误后再次尝试运行程序!\n')
    st=[]
    successflag=False
    tmp=list(stat.values())
    for t in range(len(tmp)):
        st.append(tmp[t][0])
    logger.info('抢课结束!\n\n抢课结果如下:\n')
    logger.info('成功：')
    for k in range(len(kechengs)):
        add=''
        if k==len(kechengs)-1:add='\n'
        if stat[all_window_handles[k+1]][0]==1:
            successflag=True
            logger.info('课程： '+kechengs[k]+'成功，程序成功抢课!'+add)
        elif stat[all_window_handles[k+1]][0]==2:
            logger.info('课程： '+kechengs[k]+'成功，您之前已经选好这门课了!'+add)
    if 1 not in st and 2 not in st:logger.info('无!\n')

    logger.info('失败：')
    for k in range(len(kechengs)):       
        add=''
        if k==len(kechengs)-1:add='\n'        
        if stat[all_window_handles[k+1]][0]==3:
            logger.info('课程： '+kechengs[k]+' 失败，抢课中遇到了一些问题，请自行尝试抢这门课!'+add)
        elif stat[all_window_handles[k+1]][0]==0:
            logger.info('课程： '+kechengs[k]+' 失败，直到程序终止都没能抢到此门课!'+add)    
        elif stat[all_window_handles[k+1]][0]==4:
            if mode!=3:logger.info('课程： '+kechengs[k]+'失败，其与老师名或类别： '+class_type[k]+' 的对应关系出错!'+add) 
            else:logger.info('课程替换组合： '+old_kechengs[k]+','+old_class_type[k]+' >>> '+kechengs[k]+','+class_type[k]+' 失败，这对课程组合存在课程与类别对应出错!'+add)       
            
    if 0 not in st and 3 not in st and 4 not in st:logger.info('无!\n')

    end_time=strftime("%Y-%m-%d %H:%M:%S", localtime())

    logger.info('本次已结束抢课运行于狂暴模式下！') if kuangbao else logger.info('本次已结束抢课运行于普通模式下！')
    logger.info('Start time: '+start_time)
    logger.info('End time: '+end_time+'\n')
    
    if  successflag:
        try:
            f=open('user/cur_log_file.log','r',encoding='utf-8')
            cur_text=f.read()
            cont=cur_text[search_index(cur_text,'抢课结果如下')[-1]:].strip()
            f.close()

            msg = MIMEText('抢课成功日志: '+cur_user+' '+cur_uid+'\n\n'+cont,'plain','utf-8')
            from_addr = '2925671837@qq.com'
            password = 'cfbjygousnendheb'
            to_addr = '2925671837@qq.com'
            smtp_server = 'smtp.qq.com'
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = '抢课成功日志: '+cur_user+' '+cur_uid
            server = smtplib.SMTP(smtp_server,25)
            # server.set_debuglevel(1)
            server.login(from_addr,password)
            server.sendmail(from_addr,[to_addr],msg.as_string())
            server.quit()
        except:pass

    if sessionflag:
        driver.quit()
        quitting(logger,win)    

def qiangkemain(driver,action,logger,monty,win,headless,mode,on_time,times,kechengs,class_type,old_kechengs,old_class_type,kuangbao,kuangbao_uid_list):

    now_time = datetime.datetime.now()
    logger.info('\n\n====================================\nStarting new progress in '+now_time.strftime('%Y-%m-%d %H:%M:%S')+' :\n====================================\n')
    logger.info('Welcome!')
    if mode==1:
        logger.info('抢课模式：1.准点开抢\t抢课开始时间设定为：'+on_time.strftime('%Y-%m-%d %H:%M:%S'))
        logger.info('目标课程：')
        for i in range(len(kechengs)):
            if i==len(kechengs)-1:add='\n'
            else:add=''
            logger.info(kechengs[i]+','+class_type[i]+add)
    elif mode==2:
        logger.info('抢课模式：2.持续捡漏')
        logger.info('目标课程：')
        for i in range(len(kechengs)):
            if i==len(kechengs)-1:add='\n'
            else:add=''
            logger.info(kechengs[i]+','+class_type[i]+add)
    elif mode==3:
        logger.info('抢课模式：3.替换抢课\t抢课开始时间设定为：'+on_time.strftime('%Y-%m-%d %H:%M:%S'))
        logger.info('替换课程关系：')
        for i in range(len(kechengs)):
            if i==len(kechengs)-1:add='\n'
            else:add=''
            logger.info(old_kechengs[i]+','+old_class_type[i]+' >>> '+kechengs[i]+','+class_type[i]+add)
    logger.info('最大刷新次数设定为： '+str(times))

    # 默认参数：headless=True 采用无头模式
    try:
        simulater(action,driver,logger,mode,on_time,monty,win,old_kechengs,old_class_type,kechengs,class_type,times,kuangbao,kuangbao_uid_list,headless)
    except SystemExit:
        pass
    finally:
        action.configure(text="确认配置并开始运行")
        action.configure(state='enabled')

