import os, time, datetime, logging, webbrowser, subprocess, re, sys, html2text, pygame, urllib.request
from urllib import request
from urllib.parse import quote
from mywindow import *
from PyQt5 import QtCore, QtGui, QtWidgets
import speech_recognition as sr
from gtts import gTTS
from pygame import mixer
mixer.init()


def setMoveWindow(widget):
    """
    Позволяет перемещать окно ухватившись не только за заголовок, а за произвольный виджит (widget).
    """
    win = widget.window()
    cursorShape = widget.cursor().shape()
    moveSource = getattr(widget, "mouseMoveEvent")
    pressSource = getattr(widget, "mousePressEvent")
    releaseSource = getattr(widget, "mouseReleaseEvent")
    
    def move(event):
        if move.b_move:
            x = event.globalX() + move.x_korr - move.lastPoint.x()
            y = event.globalY() + move.y_korr - move.lastPoint.y()
            win.move(x, y)
            widget.setCursor(QtCore.Qt.SizeAllCursor)
        return moveSource(event)
    
    def press(event):
        if event.button() == QtCore.Qt.LeftButton:
            # Корекция геометрии окна: учитываем размеры рамки и заголовока
            x_korr = win.frameGeometry().x() - win.geometry().x()
            y_korr = win.frameGeometry().y() - win.geometry().y()
            # Корекция геометрии виджита: учитываем смещение относительно окна
            parent = widget
            while not parent == win:
                x_korr -= parent.x()
                y_korr -= parent.y()
                parent = parent.parent()
            move.__dict__.update({"lastPoint":event.pos(), "b_move":True, "x_korr":x_korr, "y_korr":y_korr})
        else:
            move.__dict__.update({"b_move":False})
            widget.setCursor(cursorShape)
        return pressSource(event)
    
    def release(event):
        move.__dict__.update({"b_move":False})
        widget.setCursor(cursorShape)
        return releaseSource(event)
    
    setattr(widget, "mouseMoveEvent", move)
    setattr(widget, "mousePressEvent", press)
    setattr(widget, "mouseReleaseEvent", release)
    move.__dict__.update({"b_move":False})
    return widget

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        global sr
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        qss_file = open('style_file.qss').read()
        self.setStyleSheet(qss_file)
        self.ui.pushButton.clicked.connect(self.mycommand)
        self.ui.toolButton_2.clicked.connect(self.myexit)
        self.ui.toolButton.clicked.connect(self.mymin)
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()
        now_time = datetime.datetime.now()
        self._mp3_name = now_time.strftime("%d%m%Y%I%M%S")+".mp3"
        self._mp3_nameold='111'

    # Функция для запуска команд с командной строки Windows
    def osrun(self, cmd):
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)

    # Функция открывает в браузере определенный URL и произносит фразу
    def openurl(self, url, ans):
        webbrowser.open(url)
        self.say(str(ans))
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    # Функция произносит вслух фразу
    def say(self, phrase):
        tts = gTTS(text=phrase, lang="ru")
        tts.save(self._mp3_name)
        mixer.music.load(self._mp3_name)
        mixer.music.play()
        if(os.path.exists(self._mp3_nameold)):
            os.remove(self._mp3_nameold) 
        now_time = datetime.datetime.now()
        self._mp3_nameold=self._mp3_name
        self._mp3_name = now_time.strftime("%d%m%Y%I%M%S")+".mp3"
        
    # Функция чистит фразу от ключевых слов    
    def cleanphrase(self, statement, spisok):
        for x in spisok:
            statement=statement.replace(x, '')
        statement=statement.strip()
        return statement

    # Удаляем лишний mp3 файл
    def _clean_up(self):
        def clean_up():
            os.remove(self._mp3_name)

    # Функция выдает список url из выдачи поисковика по запросу z
    def mysearch(self,z):
        s = 'http://go.mail.ru/search?fm=1&q='+quote(z)
        doc = urllib.request.urlopen(s).read().decode('cp1251',errors='ignore')
        o=re.compile('"url":"(.*?)"')
        l=o.findall(doc)
        sp=[]
        for x in l:
            if((x.rfind('youtube')==-1) and(x.rfind('yandex')==-1) and(x.rfind('mail.ru')==-1) and(x.rfind('.jpg')==-1) and(x.rfind('.png')==-1) and(x.rfind('.gif')==-1)):
                sp.append(x)
        sp = dict(zip(sp, sp)).values()
        sp1=[]
        for x in sp: sp1.append(x)
        return sp1

    # Функция выдает список текстов со страниц из списка переданнных в неё url
    def gettexts(self, urls):
        urls2=[]
        urls2.append(urls[0])
        urls2.append(urls[1])
        texts=[]
        for s in urls2:
            doc = urllib.request.urlopen(s).read().decode('utf-8',errors='ignore')
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.body_width = False
            h.ignore_images = True
            doc = h.handle(doc)
            summa=""       
            ss=doc.split("\n")
            for xx in ss:
                xx=xx.strip()
                if((len(xx)>50) and (xx.startswith('&')==False) and (xx.startswith('>')==False) and (xx.startswith('*')==False) and (xx.startswith('\\')==False) and (xx.startswith('<')==False) and (xx.startswith('(')==False) and (xx.startswith('#')==False) and (xx.endswith('.') or xx.endswith('?') or xx.endswith('!') or xx.endswith(';'))):
                    summa = summa + xx + "\n \n"  
            if(len(summa)>500):
                texts.append(summa)
        return texts

    def myexit(self):
        mixer.stop()
        mixer.quit()
        files = os.listdir()
        print(files)
        files = filter(lambda x: x.endswith('.mp3'), files) 
        for f in files:
            if(os.path.exists(f)): os.remove(f)
        if(os.path.exists('index.html')): os.remove('index.html') 
        sys.exit()

    def mymin(self):
        self.showMinimized()
    
    def mycommand(self):
        print("Скажи что - нибудь!")
        with self._microphone as source:
            audio = self._recognizer.listen(source)
        print("Понял, идет распознавание...")
        try:
            statement = self._recognizer.recognize_google(audio, language="ru_RU")
            statement=statement.lower()

            print("Вы сказали: {}".format(statement))

            # Здесь идут команды для распознавания
            mflag=0
            
            if((statement.find("калькулятор")!=-1) or (statement.find("calculator")!=-1)):
                self.osrun('calc')
                mflag=1
                            
            if((statement.find("блокнот")!=-1) or (statement.find("notepad")!=-1)):
                self.osrun('notepad')
                mflag=1

                             
            if((statement.find("paint")!=-1) or (statement.find("паинт")!=-1)):
                self.osrun('mspaint')
                mflag=1

            if((statement.find("browser")!=-1) or (statement.find("браузер")!=-1)):
                self.openurl('http://google.ru', 'Открываю браузер')
                mflag=1
 
            # Команды для открытия URL в браузере
                    
            if(((statement.find("youtube")!=-1) or (statement.find("youtub")!=-1) or (statement.find("ютуб")!=-1) or (statement.find("you tube")!=-1)) and (statement.find("смотреть")==-1)):                        
                self.openurl('http://youtube.com', 'Открываю ютуб')
                mflag=1
 
            if(((statement.find("новости")!=-1) or (statement.find("новость")!=-1) or (statement.find("новасти")!=-1)) and ((statement.find("youtube")==-1) and (statement.find("youtub")==-1) and (statement.find("ютуб")==-1) and (statement.find("you tube")==-1))):
                self.openurl('https://www.youtube.com/user/rtrussian/videos', 'Открываю новости')
                mflag=1
                         
            if((statement.find("mail")!=-1) or (statement.find("майл")!=-1)):
                self.openurl('https://e.mail.ru/messages/inbox/', 'Открываю почту')
                mflag=1
                        
            if((statement.find("вконтакте")!=-1) or (statement.find("в контакте")!=-1)):
                self.openurl('http://vk.com', 'Открываю Вконтакте')
                mflag=1

            # Команды для поиска в сети интернет

            if((statement.find("читать")!=-1) or (statement.find("четать")!=-1) or (statement.find("читати")!=-1) or (statement.find("читает")!=-1) or (statement.find("чи тать")!=-1) or (statement.find("прочитать")!=-1) or (statement.find("читай")!=-1) or (statement.find("прочитай")!=-1) or (statement.find("считай")!=-1)):
                statement=self.cleanphrase(statement, ['прочитать', 'чи тать', 'читать', 'четать', 'читати', 'читает', 'считай', 'читай', 'про'])
                try:
                    spisok=self.mysearch('статья+'+statement)
                    mytext=self.gettexts(spisok)
                    f = open('index.html', 'w')
                    if(mytext[0]!=''):
                        sss='<pre style="font-size: 120%; font-weight: bold; padding: 50px; background: #efefef; white-space: pre-wrap; white-space: -moz-pre-wrap; white-space: -pre-wrap; white-space: -o-pre-wrap; word-wrap: break-word;">'+str(mytext[0])+'</pre>'
                        f.write(sss)
                    if((len(mytext)>1) and (mytext[1]!='')):
                        sss='<p><pre style="font-size: 120%; font-weight: bold; padding: 50px; background: #efefef; white-space: pre-wrap; white-space: -moz-pre-wrap; white-space: -pre-wrap; white-space: -o-pre-wrap; word-wrap: break-word;">'+str(mytext[1])+'</pre>'
                        f.write(sss)
                    
                    f.close()
                    webbrowser.open('index.html')
                except:
                    self.openurl(self.mysearch('статья+'+statement)[1], "Вот что я нашла")
                mflag=1
                    
                
               

            if((statement.find("покажи")!=-1) or (statement.find("показать")!=-1)):
                statement=self.cleanphrase(statement, ['покажи', 'показать'])                
                self.openurl(self.mysearch('статья+'+statement)[1], "Вот что я нашла")
                mflag=1
                  
            if((statement.find("найти")!=-1) or (statement.find("поиск")!=-1) or (statement.find("найди")!=-1) or (statement.find("дайте")!=-1) or (statement.find("mighty")!=-1)):
                statement=self.cleanphrase(statement, ['найди', 'найти'])
                self.openurl('https://yandex.ru/yandsearch?text=' + statement, "Я нашла следующие результаты")
                mflag=1
                        
            if(((statement.find("смотреть")!=-1) or (statement.find("сматреть")!=-1)) and ((statement.find("фильм")!=-1) or (statement.find("film")!=-1))):
                statement=self.cleanphrase(statement, ['посмотреть', 'смотреть', 'сматреть', 'хочу', 'фильм', 'film'])                
                self.openurl(self.mysearch('смотреть+онлайн+фильм+'+statement)[1], "Если это нужный фильм нажмите Play")
                mflag=1

            if(((statement.find("youtube")!=-1) or (statement.find("ютуб")!=-1) or (statement.find("you tube")!=-1)) and (statement.find("смотреть")!=-1)):
                statement=self.cleanphrase(statement, ['хочу', 'на ютубе', 'на ютуб', 'на youtube', 'на you tube', 'на youtub', 'youtube', 'ютуб', 'ютубе', 'посмотреть', 'смотреть'])
                self.openurl('http://www.youtube.com/results?search_query=' + statement, 'Ищу в ютуб')
                mflag=1

            if((statement.find("слушать")!=-1) and (statement.find("песн")!=-1)):
                statement=self.cleanphrase(statement, ['песню', 'песни', 'песня', 'хочу', 'песней', 'послушать', 'слушать'])
                self.openurl('https://my.mail.ru/music/search/' + statement, "Нажмите плэй")
                mflag=1

                    
            if((statement.find("до свидания")!=-1) or (statement.find("досвидания")!=-1)):
                answer = "Пока!"
                self.say(str(answer))
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                sys.exit()
                mflag=1
                    
            if(mflag==0): self.say(str('Переформулируйте команду'))  

        except sr.UnknownValueError:
            print("Упс! Кажется, я тебя не поняла, повтори еще раз")
            mflag=0
        except sr.RequestError as e:
            print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
        
    
       
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MyWin()
    setMoveWindow(mainWin)
    mainWin.show()
    sys.exit(app.exec_())
           
        
