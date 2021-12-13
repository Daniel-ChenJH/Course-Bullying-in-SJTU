import logging
import sys
from tkinter import scrolledtext
from tkinter import WORD

def scrolltest(win,scrolW,scrolH):
    scr = scrolledtext.ScrolledText(win, width=scrolW, height=scrolH, wrap=WORD,relief="sunken",font=('宋体 10'))
    return scr

# 用于重定向输出到滚动窗口           
class IODirector(object):
    def __init__(self, text_area):
        self.text_area = text_area

class StdoutDirector(IODirector):
    def write(self, msg):
        self.text_area.insert('end', msg)
        self.text_area.see('end')
        self.text_area.update()
    def flush(self):
        pass


def loggetter(scr):

    logger = logging.getLogger()  # 不加名称设置root logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s  %(message)s',
        datefmt='[%H:%M:%S]')
        
    # 使用FileHandler输出到文件
    fh = logging.FileHandler('user/qiangke_log_file.log','a+',encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    # 使用StreamHandler输出到屏幕
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # 添加Handler
    logger.addHandler(ch)
    logger.addHandler(fh)

    sys.stdout = StdoutDirector(scr)
    app = logging.StreamHandler(stream=sys.stdout)             # added
    app.setLevel(logging.INFO)
    app.setFormatter(formatter)
    logger.addHandler(app)   

    return logger