sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pyqt5

sudo apt-get install scons gcc flite flite1-dev expat libunistring-dev libsox-dev
sudo apt-get install libasound-dev
sudo apt-get install libpulse-dev libao-dev 

sudo git clone https://github.com/Olga-Yakovleva/RHVoice
cd RHVoice
sudo scons
sudo scons install
sudo ldconfig
После этого можно проверить, работает ли синтез речи с помощью команды в консоли:

echo «Привет я синтезатор речи» | RHVoice-test -p anna

Движок установили, теперь сделаем простенький GUI к нему.

Чтобы создать графический интерфейс под PyQt5, кроме самого PyQt5 понадобится также Qt designer. Как установить его, написано здесь:

https://askubuntu.com/questions/612314/how-to-install-pyqt-for-python-3-in-ubuntu-14-10

После установки, запускаем Designer командой:

qtchooser -run-tool=designer -qt=5

и создаем очень простой интерфейс из одного большого текстового поля и двух кнопок.

Сохраняем .ui файл как reader.ui, и преобразовываем его в файл .py командой:

pyuic5 reader.ui -o mygui.py


Программа тестировалась под Linux Mint с установленным Python 3.5, PyQt5.

Возможно понадобится 

pip install pyaudio
pip install pygame
pip install gTTS
pip install html2text
pip install SpeechRecognition
как установить pip тут https://losst.ru/ustanovka-pip-v-ubuntu