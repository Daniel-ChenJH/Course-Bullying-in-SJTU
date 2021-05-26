# -*- encoding: utf-8 -*-
'''
@File    :   qiangke.py
@Time    :   2021/02/25 14:17:18
@Author  :   Daniel-ChenJH
@Email   :   13760280318@163.com
@Version    :   2.0
@Descriptions :   上海交通大学全自动抢课脚本,请保证已经安装了最新版本的Chrome浏览器（90.0.4430系列版本）
                    本程序支持准点开抢与抢课已经开始后持续捡漏两种模式。
'''

# The imported libs: 
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

# 将输出同时写入到log文件
class Logger(object):
    def __init__(self, fileN="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN, "a+",encoding='utf-8')
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush() #每次写入后刷新到文件中，防止程序意外结束
    def flush(self):
        self.log.flush()
 

def simulater(mode,on_time,kechengs,class_type,account_name,account_password,times):
    start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

    option = webdriver.ChromeOptions()

    bili=1
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    # 防止打印一些无用的日志
    option.add_experimental_option("excludeSwitches", ['enable-automation','enable-logging'])
    driver = webdriver.Chrome(options=option,executable_path=r'chromedriver.exe')
    driver.get('https://i.sjtu.edu.cn/')
    driver.maximize_window()    # 最大化页面
    # sleep(2)
    driver.set_page_load_timeout(5)
    try:
        login = WebDriverWait(driver,5,0.2).until(lambda x:driver.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div/div/form/div[6]/div/a/img') )
        login.click()
    except TimeoutException:
        driver.execute_script('window.stop()')

    driver.switch_to.default_content()
    flag,flag2=True,True
    count=1

    while(flag):
        try:
            name=driver.find_element_by_xpath('//*[@id="user"]')
            name.send_keys(account_name)
            password=driver.find_element_by_xpath('//*[@id="pass"]')
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
                captcha.send_keys(str(cap.strip()))
            else:
                captcha=driver.find_element_by_xpath('//*[@id="captcha"]')
                captcha.send_keys(hand_cap.strip())
            driver.find_element_by_xpath('//*[@id="submit-button"]').click()
            driver.switch_to.default_content()
            lanmu=driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a') # 用来确保登陆成功
            flag=False
            print('登录成功！\n')
        except TesseractNotFoundError:
            print('There is something wrong with your tesseract, please type in the captcha": ')
            hand_cap=input('')
            flag2=False
        except NoSuchElementException:
            print('\n验证码自动识别错误或jaccount信息输入错误，正在尝试第'+str(count+1)+'次...')
            count+=1
            if count%3==0:
                try:
                    driver.refresh()
                    sleep(3)
                except TimeoutException:
                    driver.execute_script('window.stop()')

                driver.switch_to.default_content()
            if count>=10:
                print('\n大概率是您的jaccount信息输入错误，请检查并修改后重试...')
                my_file = 'button.png' # 文件路径
                if path.exists(my_file): # 如果文件存在
                    remove(my_file) # 则删除
                input('输入回车键退出……')
                return
        except ElementNotInteractableException:
            try:
                driver.refresh()
                sleep(3)
            except TimeoutException:
                driver.execute_script('window.stop()')
            driver.switch_to.default_content()

    origin= driver.current_window_handle
    driver.implicitly_wait(5)
    
    # 准点开抢模式，阻塞程序
    if mode==1:
        print('抢课开始时间设定为：',on_time)
        while True:
            now_time=datetime.datetime.now()
            if now_time<on_time and int((on_time-now_time).seconds)>2:
                print('未到抢课开放时间，当前时间为',now_time.strftime('%Y-%m-%d %H:%M:%S'),'程序等待中')
                if int((on_time-now_time).seconds)>60:
                    sleep(60) 
                elif int((on_time-now_time).seconds)>10:
                    sleep(10)
                else:sleep(2)     
            else:
                if now_time>=on_time:break   
        print('当前时间为',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'程序开始抢课！\n')

    failcount=0
    # 点击下拉栏尝试进入选课页面
    while failcount<50:
        try:
            for j in range(len(kechengs)):
                now=driver.window_handles
                driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/a').click()
                driver.find_element_by_xpath('/html/body/div[3]/div/nav/ul/li[3]/ul/li[3]/a').click()
                WebDriverWait(driver, 5, 0.1).until(EC.new_window_is_opened(now))
            all_window_handles = driver.window_handles
            k=0
            stat={}
            # 此时已经进入选课界面
            for handle in all_window_handles:
                if handle !=origin:
                    stat[handle]=[False,k]
                    driver.switch_to.window(handle)
                    driver.implicitly_wait(2)
                    inp=driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input')
                    inp.send_keys(kechengs[k])
                    
                    go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
                    go.click()

                    typebox=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/ul')
                    types=typebox.find_elements_by_tag_name('a')
                    for type in types:
                        if class_type[k] in type.text:
                            type.click()
                            break
                    k+=1
                    sleep(0.2)

            # 开始查询刷新
            for q in range(times):
                temp=list(stat.values())
                st=[]

                for t in range(len(temp)):
                    st.append(temp[t][0])
                if False not in st:break    #所有课程都抢课完成

                for handle in all_window_handles:
                    if handle!=origin and not stat[handle][0]:
                        driver.switch_to.window(handle)
                        loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[21]')
                        try:
                            WebDriverWait(driver,1,0.1).until(EC.visibility_of_element_located(loc))
                        except TimeoutException:pass
                        driver.implicitly_wait(0.5)
                        
                        # 刷新次数达到500时重启程序
                        if (q+1)%500==0:
                            driver.refresh()
                            sleep(0.5)
                            driver.implicitly_wait(5)
                            inp=driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input')
                            inp.send_keys(kechengs[stat[handle][1]])
                            
                            # 查询按钮
                            go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
                            go.click()
                            sleep(0.3)
                            typebox=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/ul')
                            types=typebox.find_elements_by_tag_name('a')
                            for type in types:
                                if class_type[stat[handle][1]] in type.text:
                                    type.click()
                                    loc = (By.XPATH, '//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[21]')
                                    sleep(1.5)
                                    driver.implicitly_wait(5)
                                    break
                                    
                        rongliang=10+len(driver.find_elements_by_xpath("/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/thead/tr/th"))
                        status=driver.find_element_by_xpath('//html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td['+str(rongliang)+']')
                        if status.is_displayed():
                            # 显示已满
                            print(strftime("%Y-%m-%d %H:%M:%S", localtime()),str(kechengs[stat[handle][1]]),'try_time=='+str(q+1),'failed',status.text)
                            go=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div/span/button[1]')
                            go.click()
                        else:
                            try:
                                temp=WebDriverWait(driver,1, 0.05).until(lambda driver: driver.find_element_by_xpath('//*[@id="contentBox"]//button'))
                                if temp.text!='退选': 
                                    temp.click()
                                    sleep(0.1)
                                    temp2=WebDriverWait(driver,1, 0.05).until(lambda driver: driver.find_element_by_xpath('//*[@id="contentBox"]//button'))
                                    try:
                                        if temp2.text=='退选': 
                                            print('\n================================',str(kechengs[stat[handle][1]]),', Success!',strftime("%Y-%m-%d %H:%M:%S", localtime()),'try_time=='+str(q+1),'========================\n')
                                        else:print('\n好像抢课程：',str(kechengs[stat[handle][1]]),'中出现了些什么问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!\n')
                                    except:print('\n好像抢课程：',str(kechengs[stat[handle][1]]),'中出现了些什么问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!\n')
                                else :print('你已经选上这门课了！'+str(kechengs[stat[handle][1]]))
                                all_window_handles=driver.window_handles
                                stat[handle][0]=True
                            except Exception as e:
                                print(strftime("%Y-%m-%d %H:%M:%S", localtime()),str(kechengs[stat[handle][1]]),'try_time=='+str(q+1),'failed',status.text)
                                print('failed because of :',e,' Retrying!')
            if False not in st:break
        except Exception as e:
            failcount+=1
            print('程序第'+str(failcount)+'次异常，异常原因：',e,'\t重试中...')
            all_window_handles = driver.window_handles
            for handle in all_window_handles:
                if handle !=origin:
                    driver.switch_to.window(handle)
                    driver.implicitly_wait(0.5)
                    driver.close()
            driver.switch_to.window(origin)
            driver.implicitly_wait(0.5)
            sleep(0.5)       

    if failcount==20:print('\n好像出了些什么问题,也可能是网站服务器问题……请自行登录网站尝试抢课，并对照文件\'readme.txt\'确保无误后再次尝试运行程序!\n')
    print('\nended!\n抢课结果:\n')
    for k in range(len(kechengs)):
        if stat[all_window_handles[k+1]][0]:
            print(kechengs[k],'success!')
        else:print(kechengs[k],'failed!')
    end_time=strftime("%Y-%m-%d %H:%M:%S", localtime())
    print('\nStart time: ',start_time)
    print('End time: ',end_time)

    my_file = 'button.png' # 文件路径
    if path.exists(my_file): # 如果文件存在
        remove(my_file) # 则删除
    
    print("\nPlease 'Star' the program of Daniel-ChenJH on Github if you think it's a quite good one. ")
    input('\n程序已完成！请立即自行移步至教学信息服务网 i.sjtu.edu.cn 查询确认抢课结果！\n\n回车键退出程序……')
    driver.quit()


if __name__ == '__main__':
    
    sys.stdout = Logger("qiangke_log_file.txt")
    #会同时在控制台输出和写入“log_file.txt”文件中

    # print("\nOn-Time Automatic Class Snatching System\n\nAuthor:\t@Daniel-ChenJH (email address: 13760280318@163.com)\nFirst Published on Februry 25th, 2021.\n\nThe program can only be run in a Windows x86_64 computer, and is written based on the current structure of the website https://i.sjtu.edu.cn， known as the website for students to deal with their personal stuffs, including choosing classes to attend in the coming semester.\nHowever, you should only use it when the time is permitted for choosing classes, otherwise this program may not work and throw out errors.\nBy using this program, you will be able to choose the designated courses immediately.\nIf the class you wanna choose is currently full, the program can keep refreshing the website page and check if the class is available at a speed of 1 to 2 times per second, until the class is have remaining quota, and once this happens, the program will immediately choose this class.\nYou probably don't need to type in the captcha in order to login! That's so cool!\nNotice that don't use this program too often, for your schoolmates may be angry at you for you can nearly choose all the classes that you want.\n******Reminder: The author(@Daniel-ChenJH) has takes no responsibility for any usage of the program by the potential users.\nAt least now I know that the school won't ban the IP or Jaccount that keep refreshing the page in a short period of time, so you can feel at ease while using it.\nFor any usage problems or discussions, feel free to contact 13760280318@163.com.\n\nUsage: \n1. Unzip the zip file;\n2. Make sure that you own the latest version of Chrome Browser(series of 88.0) on your computer. You can check your version by visiting chrome://settings/help.\n3. Edit the file \"account.txt\" in the unzipped file in the following steps.\n4. Change the second line into the time you want the program to check your class before exiting (if you cannot choose the class finally). You can keep it running by setting this value so big, but remember to give it an integer.\n5. Change the third line into your Jaccount username, and fourth line into your Jaccount password.\n6. Add classes you wanna choose in the following lines, remember !!! one class and its category per line! Classname, teacher's name or course number is all ok to be written here, and you only need to write one message about a class. However, I strongly suggest you write the course number here, which leads to the most accurate information of the course.\n7. If you have multiple classes you wanna choose, just type in them and their categories in the following lines. However, too many courses may lead to a decline in the efficiency of the program. You'd better write no more than four classes here.\n8. Although the program won't quit the class that you have chosen, I still strongly suggest you to make sure there is no time conflict in your expected class schedule.\nHere is a good example of file 'account.txt' :\n\n1000\nyour_jaccount_id_here\nyour_jaccount_password_here\n物理化学，交叉课程\n数据可视化，交叉课程\n离散数学，任选课程\n\n\n")
    print("\n\nOn-Time Automatic Class Snatching System\n\nAuthor:\t@Daniel-ChenJH (email address: 13760280318@163.com)\nFirst Published on Februry 25th, 2021 , revised for v2.0 on May 24th, 2021.\n")
    print('\nPlease read file \'readme.txt\' carefully and then edit file \'account.txt\' before running the program!!!\n')
    now_time = datetime.datetime.now()
    print('Starting progress in ',now_time.strftime('%Y-%m-%d %H:%M:%S'),' :\n====================================\n')

    # 用户输入读取
    data = []
    for line in open("account.txt","r",encoding='utf-8'):
        data.append(line)               

    mode=int(data[0].strip())
    if mode==1:on_time=datetime.datetime.strptime(data[1].strip(),'%Y-%m-%d %H:%M:%S')
    else:on_time=datetime.datetime.strptime('2000-10-11 04:30:00','%Y-%m-%d %H:%M:%S')

    times=int(data[2].strip())
    account_name=data[3].strip()
    account_password=data[4].strip()
    dataline=5

    kechengs=[]
    class_type=[]
    for line in data[dataline:]:
        if ',' in line.strip():
            kechengs.append(line.strip().split(',')[0])
            class_type.append(line.strip().split(',')[1])
        elif ' ' in line.strip():
            kechengs.append(line.strip().split(' ')[0])
            class_type.append(line.strip().split(' ')[1])
        elif '，' in line.strip():
            kechengs.append(line.strip().split('，')[0])
            class_type.append(line.strip().split('，')[1])
    
    print('Welcome, ',account_name,'!')
    print('目标课程：')
    print(kechengs)
    simulater(mode,on_time,kechengs,class_type,account_name,account_password,times)