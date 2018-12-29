import sys, time, webbrowser
import subprocess, re, os, bs4, requests
import threading
from mygui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
import snowboydecoder
import signal
import speech_recognition as sr
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem

# Объявляем глобальные переменные для передачи сигналов из потока в поток
otvet=''
listen=''
vopros=''
dontlisten=''
ispeak=''
# Объявляем распознаватель речи от гугл
r = sr.Recognizer()
# Переменная-флажок mstop определяет произносить ли следующее предложение
# или выйти из цикла чтения предложений с помощью break
mstop=0
# Подключаем файлы с голосовыми моделями имени ассистента и стоп-фразой
# Их нужно сгенерировать под ваш голос на сайте SnowBoy
model = 'oksana.pmdl'
model2 = 'stop.pmdl'
# Объявляем два детектора горячих слов - для имени и для стоп-слова
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
detector2 = snowboydecoder.HotwordDetector(model2, sensitivity=0.5)

interrupted = False

# Функция принимает строку и список слов которые надо из нее удалить, возвращает строку без этих слов
def cleanphrase(statement, spisok):
    for x in spisok:
        statement=statement.replace(x, '')
    statement=statement.strip()
    return statement

# Функция для запуска внешнего приложения с консоли без ожидания его завершения
def osrun(cmd):
    PIPE = subprocess.PIPE
    subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)

# Функции для сигналов между потоками
def signal_handler(signal, frame):
    global interrupted
    interrupted = True    
def interrupt_callback():
    global interrupted
    return interrupted

# Функция которая дает запрос к серверу Алины получает и говорит ответ
def parsealina(f, s, cl):
    ss=requests.get('http://pythono.ru/alina/index.php?s='+s)
    bb=bs4.BeautifulSoup(ss.text, "html.parser")
    pp=bb.select(cl)
    stroka=''
    for x in pp:
        stroka=stroka+x.getText().strip()+'\n'
    Say(stroka)

# Функция для озвучивания ответа исхода из команды - основной мозг программы
def mozg(f):
    if(f=='привет'):
        Say('Привет хозяин')
    if(f=='пока'):
        Say('До свидания хозяин')
        exit(0)
    if('новости политики' in f):
        parsealina(f,'новости политики','.mystring')
    if('новости науки' in f):
        parsealina(f,'новости науки','.mystring')
    if(('новости' in f) and ('компьютер' in f)):
        parsealina(f,'новости про компьютеры','.mystring')
    if(('найти' in f) or ('найди' in f)):
        parsealina(f,f,'.mystring')
    if('анекдот' in f):
        parsealina(f,'анекдот','.content')
    if(('погод' in f) and ('завтра' in f)):
         parsealina(f,'погода на завтра','.content')
    if(('погод' in f) and not ('завтра' in f)):
        parsealina(f,'погода на сегодня','.content')
    if('валют' in f):
        parsealina(f,'курс валют','.content')
    if(('открой' in f) and ('калькулятор' in f)):
        osrun('gnome-calculator')
    if(('открой' in f) and ('блокнот' in f)):
        osrun('notepadqq %U')
    if(('открой' in f) and ('браузер' in f)):
        webbrowser.open('http://google.com')
    if(('открой' in f) and (('ютуб' in f) or ('youtube' in f))):
        webbrowser.open('http://youtube.com')
    if(('открой' in f) and ('новости' in f)):
        webbrowser.open('https://www.youtube.com/user/rtrussian/videos')
    if(('открой' in f) and ('mail.ru' in f)):
        webbrowser.open('http://mail.ru')
    if(('открой' in f) and ('вконтакте' in f)):
        webbrowser.open('http://vk.com')
    if(("слушать" in f) and ("песн" in f)):
        f=cleanphrase(f, ['песню', 'песни', 'песня', 'хочу', 'песней', 'послушать', 'слушать'])
        webbrowser.open('https://my.mail.ru/music/search/' + f)
    if((("youtube" in f) or ("ютуб" in f) or ("you tube" in f)) and ("смотреть" in f)):
        f=cleanphrase(f, ['хочу', 'на ютубе', 'на ютуб', 'на youtube', 'на you tube', 'на youtub', 'youtube', 'ютуб', 'ютубе', 'посмотреть', 'смотреть'])
        webbrowser.open('http://www.youtube.com/results?search_query=' + f)
    global listen
    listen.emit([2])
    
# Функция активизирует Google Speech Recognition для распознавания основной команды
def listencommand():
    global listen
    listen.emit([1])
    print('Вы сказали Оксана')
    with sr.Microphone() as source:
        print("Скажите что-нибудь")
        audio = r.listen(source)
    try:
        f=r.recognize_google(audio, language="ru-RU").lower()
        print(f)
        global vopros
        vopros.emit([f])
        # Отправляем распознанную команду в функцию mozg()
        mozg(f)
    except sr.UnknownValueError:
        print("Робот не расслышал фразу")
        global dontlisten
        dontlisten.emit(['00'])
    except sr.RequestError as e:
        print("Ошибка сервиса; {0}".format(e))
signal.signal(signal.SIGINT, signal_handler)

# Отдельный поток 
def thread(my_func):
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper

@thread
def hotworddetect():
    print('Для того чтобы дать голосовую команду сперва скажите Оксана, и подождите две секунды, а после произнесите команду')
    # Запускаем детектор ключевого слова "Оксана" на движке SnowBoy
    detector.start(detected_callback=listencommand, interrupt_check=interrupt_callback, sleep_time=0.03)
    detector.terminate()

# Функция для прекращения синтеза речи    
def stopstop():
        osrun('pkill -9 RHVoice-test')
        global mstop
        mstop=0

# Запуск детектирования стоп-фразы
@thread
def stopsay():
    detector2.start(detected_callback=stopstop, interrupt_check=interrupt_callback, sleep_time=0.03)
    detector2.terminate()

# Функция отдельным потоком в которой производится чтение предложений
@thread
def Say(t):
    global otvet
    otvet.emit([t])
    global ispeak
    ispeak.emit(['000'])
    # ставим переменную-флажок = 1
    global mstop
    mstop=1
    # Заменяем в тексте переносы строк и табы на точки и пробелы
    t=t.replace('\n','. ')
    t=t.replace('\t','')
    t=t.replace('\r','. ')
    t=t.replace('..','.')
    # Делим текст на массив предложений
    mas=re.split("\\b[.!?\\n]+(?=\\s)", t)
    detector.terminate()
    stopsay()
    for z in mas:
        # Если переменная флажок обнулилась выходим из цикла чтения предложений
        if (mstop==0): break
        # Формируем командную строку для RHVoice
        s='echo «'+z+'» | RHVoice-test -p anna'
        # Запускаем командную строку
        ppp=subprocess.call(s, shell=True)
    detector2.terminate()
    global listen
    listen.emit([2])
    if(t=='До свидания хозяин'):
        os._exit(0)
    hotworddetect()
    



class MyWin(QtWidgets.QMainWindow):
    my_signal = QtCore.pyqtSignal(list, name='my_signal')
    my_listen = QtCore.pyqtSignal(list, name='my_listen')
    my_vopros = QtCore.pyqtSignal(list, name='my_vopros')
    my_dontlisten = QtCore.pyqtSignal(list, name='my_dontlisten')
    my_ispeak = QtCore.pyqtSignal(list, name='my_ispeak')
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label_3.setText("<img src='file:///"+os.getcwd()+"/1.jpg'>")
        # Определяем функцию Mystop при нажатии на вторую кнопку
        self.ui.pushButton_2.clicked.connect(self.Mystop)
        # При нажатии на первую кнопку слушаем основную команду
        self.ui.pushButton.clicked.connect(listencommand)
        # Список сигналов между потоками
        global otvet
        otvet=self.my_signal
        global listen
        listen=self.my_listen
        global dontlisten
        dontlisten=self.my_dontlisten
        global ispeak
        ispeak=self.my_ispeak
        global vopros
        vopros=self.my_vopros
        # Запускаем детектор имени Оксана
        hotworddetect()
        # Подключаем к сигналам функции
        self.my_signal.connect(self.myotvet, QtCore.Qt.QueuedConnection)
        self.my_listen.connect(self.mylisten, QtCore.Qt.QueuedConnection)
        self.my_vopros.connect(self.myvopros, QtCore.Qt.QueuedConnection)
        self.my_dontlisten.connect(self.mydontlisten, QtCore.Qt.QueuedConnection)
        self.my_ispeak.connect(self.myispeak, QtCore.Qt.QueuedConnection) 

    # Выдает ответ в текстовое поле
    def myotvet(self, data):  
        self.ui.textEdit.setText(str(data[0]))
        
    # Выдает в текстовое поле распознанную речь
    def myvopros(self, data): 
        self.ui.textEdit_2.setText(str(data[0]))

    # Если ассистент вас не слышит ставит соответствующую картинку
    def mydontlisten(self, data): 
        self.ui.label_3.setText("<img src='file:///"+os.getcwd()+"/3.jpg'>")

    # Сигнал для установки той или иной картинки в зависимости от состояния Оксаны (слушаю / отдыхаю)
    def mylisten(self, data):  
        if(data[0]==1):
            self.ui.label_3.setText("<img src='file:///"+os.getcwd()+"/2.jpg'>")
        if(data[0]==2):
            self.ui.label_3.setText("<img src='file:///"+os.getcwd()+"/1.jpg'>")

    # Ставит картинку отображаему. когда Оксана говорит
    def myispeak(self, data):
        self.ui.label_3.setText("<img src='file:///"+os.getcwd()+"/4.jpg'>")
        
    # Функция срабатывающая при нажатии кнопки Стоп
    # Обнуляет переменную-флажок и сбивает процесс RHVoice
    def Mystop(self):
        osrun('pkill -9 RHVoice-test')
        global mstop
        mstop=0

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
