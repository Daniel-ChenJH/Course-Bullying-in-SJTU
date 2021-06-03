# -*- encoding: utf-8 -*-
'''
@File    :   qiangke.py
@Time    :   2021/06/03 19:31:18
@Author  :   Daniel-ChenJH
@Email   :   13760280318@163.com
@Version    :   3.0
@Descriptions :   Course-Bullying-in-SJTU
                    上海交通大学全自动抢课脚本,请保证已经安装了最新版本的Chrome浏览器（90.0.4430系列版本）
                    本程序支持准点开抢与抢课已经开始后持续捡漏两种模式。
'''

# The imported libs: 
import logging
from selenium import webdriver
from time import sleep,strftime,localtime
from PIL import Image
from pytesseract import image_to_string
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from pytesseract.pytesseract import TesseractNotFoundError
from os import remove, path
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import sys
import signal

# 检测程序异常终止
def signal_handling(signum,frame):
    logger.info('******************************')
    logger.info ("程序被使用者终止。")    
    logger.info('******************************')
    sys.exit()

def login(account_name,account_password,headless,bili):
    option = webdriver.ChromeOptions()
    # 无头模式；采用有头模式时将bili调成当前电脑屏幕的缩放比例（1、1.25、1.5或2），并注释掉50~52行
    if headless:
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
    driver = webdriver.Chrome(options=option,executable_path=r'chromedriver.exe')
    driver.set_page_load_timeout(5)
    try:
        driver.get('https://i.sjtu.edu.cn/')
        driver.maximize_window()    
        login = WebDriverWait(driver,5,0.1).until(lambda x:driver.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div/div/form/div[6]/div/a/img') )
        login.click()
    except TimeoutException:
        driver.execute_script('window.stop()')

    driver.switch_to.default_content()
    flag,flag2=True,True
    count=1
    while(flag):
        try:
            name=driver.find_element_by_xpath('//*[@id="user"]')
            name.clear()
            name.send_keys(account_name)
            password=driver.find_element_by_xpath('//*[@id="pass"]')
            password.clear()
            password.send_keys(account_password)
            
            if flag2:       #如果pytesseract没有问题
                captcha=driver.find_element_by_xpath('//*[@id="captcha-img"]')
                photoname='button.png'
                driver.save_screenshot(photoname)

                left = captcha.location['x']*bili
                top = captcha.location['y']*bili
                right = left + captcha.size['width']*bili
                bottom = top + captcha.size['height']*bili

                im = Image.open(photoname)
                im = im.crop((left, top, right, bottom))
                gray = im.convert('L')
                threshold = 180
                table = []
                for i in range(256):
                    if i < threshold:
                        table.append(0)
                    else:
                        table.append(1)
                out = gray.point(table, '1')
                out.save(photoname)
                cap=image_to_string(out)
                captcha=driver.find_element_by_xpath('//*[@id="captcha"]')
                captcha.clear()
                captcha.send_keys(str(cap.strip()))
            else:
                captcha=driver.find_element_by_xpath('//*[@id="captcha"]')
                captcha.clear()
                captcha.send_keys(hand_cap.strip())
            driver.find_element_by_xpath('//*[@id="submit-button"]').click()
            driver.switch_to.default_content()
            lanmu=driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a') # 用来确保登陆成功
            flag=False
            logger.info('登录成功！\n')
        except TimeoutException:
            driver.refresh()
            driver.switch_to.default_content()
            try:
                lanmu=driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a') # 用来确保登陆成功
                flag=False
                logger.info('登录成功！\n')      
            except NoSuchElementException:
                flag=True
        
        except TesseractNotFoundError:
            logger.info('There is something wrong with your tesseract')
            logger.info('The captcha can be seen from file: \'button.png\', please type in the captcha: ')
            hand_cap=input('hand_cap=')
            flag2=False
        except NoSuchElementException:
            logger.info('验证码自动识别错误或jaccount信息输入错误，正在尝试第'+str(count+1)+'次...')
            count+=1
            if count%3==0:
                driver.refresh()
                try:
                    captcha = WebDriverWait(driver,3,0.1).until(lambda x:driver.find_element_by_xpath('//*[@id="captcha"]'))
                except TimeoutException:
                    driver.execute_script('window.stop()')

                driver.switch_to.default_content()
            if count>=12:
                driver.quit()
                logger.info('大概率是您的jaccount信息输入错误，请检查并修改后重试...')
                quitting()
                sys.exit(0)
        except ElementNotInteractableException:
            try:
                driver.refresh()
                sleep(3)
            except TimeoutException:
                driver.execute_script('window.stop()')
            driver.switch_to.default_content()

    origin= driver.current_window_handle
    driver.implicitly_wait(5)

    return driver,origin

def waitbegin(mode,on_time):
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

def search_in(driver,kechengs,stat,handle,class_type,bias):
    classfind=False
    try:
        inp = WebDriverWait(driver,1,0.1).until(lambda x:driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input') )
        inp.clear()
        inp.send_keys(kechengs[stat[handle][1]+bias])
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
            quitting()
            sys.exit(0)
        else:
            logger.info('程序好像出现了一些问题……')
            logger.info(e)
        
    for type in types:
        if class_type[stat[handle][1]] in type.text:
            type.click()
            classfind=True
            break
    if not classfind:
        logger.info(kechengs[stat[handle][1]]+' 的用户指定类别：'+class_type[stat[handle][1]]+'  不存在，将跳过此门课程；请检查确认无误后重新运行程序')
        stat[handle][0]=3
    return driver,classfind,stat

def search_again(driver,kechengs,stat,handle,class_type):
    driver.refresh()
    sleep(1)
    driver.implicitly_wait(5)
    inp=driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input')
    inp.clear()
    inp.send_keys(kechengs[stat[handle][1]])
    
    # 查询按钮
    go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
    go.click()
    sleep(0.5)
    typebox=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/ul')
    types=typebox.find_elements_by_tag_name('a')
    for type in types:
        if class_type[stat[handle][1]] in type.text:
            type.click()
            loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[15]')
            try:
                WebDriverWait(driver,1,0.1).until(EC.visibility_of_element_located(loc))
            except TimeoutException:pass
            driver.implicitly_wait(3)
            break
    return driver

def quitting():
    logger.info("Please 'Star' the program of Daniel-ChenJH on Github if you think it's a quite good one. ")   
    logger.info('Link to \'Course-Bullying-in-SJTU\' in Github : https://github.com/Daniel-ChenJH/Course-Bullying-in-SJTU')
    my_file = 'button.png' # 文件路径
    if path.exists(my_file): # 如果文件存在
        remove(my_file) # 则删除
    input('程序已完成！请立即自行移步至教学信息服务网 https://i.sjtu.edu.cn 查询确认抢课结果！\n\n回车键退出程序……')


def simulater(mode,on_time,old_kechengs,old_class_type,kechengs,class_type,account_name,account_password,times,headless=True,bili=1):
    start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())


    driver,origin=login(account_name,account_password,headless=headless,bili=bili)

    # 准点开抢模式，阻塞程序    
    waitbegin(mode,on_time)
    
    failcount=0
    
    while failcount<50:
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
            logger.info('持续查询刷新中......')
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
                        if handle in stat.keys():
                            driver,classfind,all_stat=search_in(driver,all_kechengs,all_stat,handle,all_class_type,bias=0)
                        else:driver,classfind,all_stat=search_in(driver,all_kechengs,all_stat,handle,all_class_type,bias=len(kechengs))
                        for a,b in all_stat.items():
                            if a in stat.keys():
                                stat[a]=b
                            else:old_stat[a]=b
                        if not classfind:continue
                    
                        # 模式三下需完成所有查询后再开始抢课
                        if mode==3:continue
                    if handle!=origin and all_window_handles.index(handle)<len(kechengs)+1 and stat[handle][0]==0:
                        driver.switch_to.window(handle)
                        loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[15]')
                        try:
                            WebDriverWait(driver,1,0.1).until(EC.visibility_of_element_located(loc))
                        except TimeoutException:pass
                        driver.implicitly_wait(0.5)

                        # 刷新次数达到500时重启程序
                        if (q+1)%500==0:
                            driver=search_again(driver,all_kechengs,all_stat,handle,all_class_type)
                        
                        sleep(0.25)         
                        rongliang=10+len(driver.find_elements_by_xpath("/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/thead/tr/th"))
                        # status=(By.XPATH,'//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td['+str(rongliang)+']')
                        # WebDriverWait(driver,4,0.1).until(EC.presence_of_element_located(status))
                        if rongliang < 13:
                            logger.info('可能是课号输入出现问题，请将\'account.txt\'中的课号修改后重新运行')
                            driver.quit()
                            quitting()
                        status=driver.find_element_by_xpath('//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td['+str(rongliang)+']')
                        
                        if status.is_displayed():
                            # 显示已满
                            logger.info(str(kechengs[stat[handle][1]])+'  try_time== '+str(q+1)+' 无空余名额 '+status.text)
                            go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
                            go.click()
                        else:
                            try:
                                sleep(0.2) 
                                temp=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath('//*[@id="contentBox"]//button'))
                                if temp.text!='退选': 
                                    if mode==3:
                                        # 退掉对应的那一门课
                                        logger.info('发现 '+kechengs[stat[handle][1]]+' 有空余名额，执行替换操作 '+temp.text)
                                        driver.switch_to.window(all_window_handles[stat[handle][1]+len(kechengs)+1])
                                        driver.implicitly_wait(0.5)
                                        tuixuan=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath('//*[@id="contentBox"]//button'))
                                        tuixuan.click()
                                        driver.implicitly_wait(3)
                                        try:
                                            confirm=driver.find_element_by_xpath('//*[@id="confirmModal"]/div/div/div[2]/div/div/p')
                                            if confirm.is_displayed():
                                                logger.info('正在退选 '+str(old_kechengs[stat[handle][1]])+'...')
                                                tuixuanqueding=WebDriverWait(driver,1, 0.1).until(lambda driver: driver.find_element_by_xpath('//*[@id="btn_confirm"]'))
                                                tuixuanqueding.click()
                                                sleep(0.2)
                                                driver.implicitly_wait(0.5)
                                                logger.info('退选成功！')
                                                # 换回之前的窗口
                                                driver.switch_to.window(handle)
                                                driver.implicitly_wait(0.5)

                                                # 规避网页防爬策略
                                                driver.refresh()
                                                sleep(0.5)
                                                driver,classfind,all_stat=search_in(driver,all_kechengs,all_stat,handle,all_class_type,bias=0)
                                                sleep(0.3)
                                                # driver.find_element_by_xpath('//*[@id="contentBox"]//button').click()
                                                try:WebDriverWait(driver,1,0.1).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="contentBox"]//button'),"选课"))
                                                except:pass
                                                temp=driver.find_element_by_xpath('//*[@id="contentBox"]//button')
                                        except Exception as e:
                                            logger.info(e)
                                            logger.info('退选'+old_kechengs[stat[handle][1]]+'时出现问题，请立即自行前往尝试退选并选课')
                                            driver.quit()
                                            quitting()
                                            # sleep(0.3)
                                            # print('temp按钮内容： '+temp.text)
                                    temp.click()
                                    sleep(0.3)
                                    driver.implicitly_wait(2)
                                    try:WebDriverWait(driver,1,0.1).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="contentBox"]//button'),"退选"))
                                    except:pass
                                    temp2=driver.find_element_by_xpath('//*[@id="contentBox"]//button')
                                    # print('temp2按钮内容： '+temp2.text)
                                    try:
                                        if temp2.text=='退选': 
                                            logger.info('\n================================ '+str(kechengs[stat[handle][1]])+' , Success! try_time== '+str(q+1)+' ========================\n')
                                            stat[handle][0]=1
                                        else:                                    
                                            logger.info('好像抢课程：'+str(kechengs[stat[handle][1]])+'中出现了些什么问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!')
                                            stat[handle][0]=3
                                    except Exception as e:
                                        logger.info(str(e)+'Error! 好像抢课程：'+str(kechengs[stat[handle][1]])+'中出现了些什么问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!')
                                        stat[handle][0]=3
                                else :
                                    logger.info('你已经选上这门课了！'+str(kechengs[stat[handle][1]]))
                                    stat[handle][0]=2
                            except Exception as e:
                                logger.info(str(kechengs[stat[handle][1]])+' try_time== '+str(q+1)+' failed '+status.text)
                                logger.info('failed because of :'+str(e)+' Retrying!')
            if q==times-1 or 0 not in st:break
        except Exception as e:
            failcount+=1
            if failcount==1 and q>800: sleep(5)
            logger.info('程序第'+str(failcount)+'次异常，异常原因：'+str(e)+' 重试中...')
            all_window_handles = driver.window_handles
            for handle in all_window_handles:
                if handle !=origin:
                    driver.switch_to.window(handle)
                    driver.implicitly_wait(0.5)
                    driver.close()
            driver.switch_to.window(origin)
            driver.implicitly_wait(0.5)
            driver.refresh()
            sleep(5)       

    if failcount==20:logger.info('好像出了些什么问题,也可能是网站服务器问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!\n')
    st=[]
    tmp=list(stat.values())
    for t in range(len(tmp)):
        st.append(tmp[t][0])
    logger.info('ended!\n\n抢课结果:\n')
    logger.info('成功：')
    for k in range(len(kechengs)):
        if stat[all_window_handles[k+1]][0]==1:
            logger.info(kechengs[k]+'成功，程序成功抢课!')
        elif stat[all_window_handles[k+1]][0]==2:
            logger.info(kechengs[k]+'成功，你之前已经选好这门课了!')
    if 1 not in st and 2 not in st:logger.info('无')

    logger.info('失败：')
    for k in range(len(kechengs)):       
        if stat[all_window_handles[k+1]][0]==3:
            logger.info(kechengs[k]+'失败，抢课中遇到了一些问题，请自行尝试抢这门课!')
        elif stat[all_window_handles[k+1]][0]==0:
            logger.info(kechengs[k]+'失败，直到程序终止都没能抢到此门课!')    
    if 0 not in st and 3 not in st:logger.info('无')
    end_time=strftime("%Y-%m-%d %H:%M:%S", localtime())

    logger.info('Start time: '+start_time)
    logger.info('End time: '+end_time)
    driver.quit()
    quitting()
    


if __name__ == '__main__':
    logger = logging.getLogger()  # 不加名称设置root logger
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s  %(message)s',
        datefmt='[%H:%M:%S]')
        
    # 使用FileHandler输出到文件
    fh = logging.FileHandler('qiangke_log_file.log','a+',encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    # 使用StreamHandler输出到屏幕
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # 添加两个Handler
    logger.addHandler(ch)
    logger.addHandler(fh)
    # logger.info('this is info message')

    logger.info("\n\nCourse-Bullying-in-SJTU: On-Time Automatic Class Snatching System\n\nAuthor:\t@Daniel-ChenJH (email address: 13760280318@163.com)\nFirst Published on Februry 25th, 2021 , revised for v2.0 on May 24th, 2021, v3.0 on June 3rd,2021 .\n\nPlease read file \'readme.txt\' carefully and then edit file \'account.txt\' before running the program!!!\nThe efficiency of this program depend on your network environment and your PC\'s capability.")
    
    # 检测程序是否异常终止
    signal.signal(signal.SIGINT,signal_handling)

    now_time = datetime.datetime.now()

    # 用户输入读取
    data = []
    for line in open("account.txt","r",encoding='utf-8'):data.append(line.strip())               

    mode=0
    if data[0] in ['1','2','3']:   mode=int(data[0])  
    else:mode=2

    if mode==1 or mode==3:on_time=datetime.datetime.strptime(data[1],'%Y-%m-%d %H:%M:%S')
    else:on_time=datetime.datetime.strptime('2020-01-01 00:00:00','%Y-%m-%d %H:%M:%S')

    times=int(data[2])
    account_name=data[3]
    account_password=data[4]
    dataline=5

    # 提升修改jaccount信息
    if account_name=='your_jaccount_id_here' or account_password=='your_jaccount_password_here':
        logger.info('请先修改jaccount信息，再运行程序！')
        sys.exit(0)

    kechengs=[]
    class_type=[] 
    old_kechengs=[]
    old_class_type=[]
    for line in data[dataline:]:
        if mode==3 and '>>>' in line:
            left=line.split('>>>')[0].strip()
            right=line.split('>>>')[1].strip()
            if ',' in right:
                kechengs.append(right.split(',')[0].strip())
                class_type.append(right.split(',')[1].strip())
            elif '，' in right:
                kechengs.append(right.split('，')[0].strip())
                class_type.append(right.split('，')[1].strip())
            if ',' in left:
                old_kechengs.append(left.split(',')[0].strip())
                old_class_type.append(left.split(',')[1].strip())
            elif '，' in left:
                old_kechengs.append(left.split('，')[0].strip())
                old_class_type.append(left.split('，')[1].strip())
        else:
            if ',' in line:
                kechengs.append(line.split(',')[0].strip())
                class_type.append(line.split(',')[1].strip())
            elif '，' in line:
                kechengs.append(line.split('，')[0].strip())
                class_type.append(line.split('，')[1].strip())

    logger.info('\n====================================\nStarting progress in '+now_time.strftime('%Y-%m-%d %H:%M:%S')+' :\n====================================\n')
    logger.info('Welcome, '+account_name+'!')
    # logger.info('Welcome, ******** !')
    if mode==1:
        logger.info('抢课模式：1.准点开抢\t抢课开始时间设定为：'+on_time.strftime('%Y-%m-%d %H:%M:%S'))
        logger.info('目标课程：')
        logger.info(kechengs)
    elif mode==2:
        logger.info('抢课模式：2.持续捡漏')
        logger.info('目标课程：')
        logger.info(kechengs)
    elif mode==3:
        logger.info('抢课模式：3.替换抢课\t抢课开始时间设定为：'+on_time.strftime('%Y-%m-%d %H:%M:%S'))
        logger.info('替换课程关系：')
        for i in range(len(kechengs)):
            logger.info(old_kechengs[i]+' >>> '+kechengs[i])
    # 无头模式；采用有头模式时将bili调成当前电脑屏幕的缩放比例（1、1.25、1.5或2）
    # 默认参数：headless=True，bili=1
    # simulater(mode,on_time,old_kechengs,old_class_type,kechengs,class_type,account_name,account_password,times,headless=False,bili=1.25)
    simulater(mode,on_time,old_kechengs,old_class_type,kechengs,class_type,account_name,account_password,times)