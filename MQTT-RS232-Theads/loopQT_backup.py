# -*- coding: utf-8 -*-
# https://medium.com/@wilfilho/pyqt5-o-fantastico-mundo-das-guis-62914b1b39c1

#from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDial, QLabel
#from PyQt5.QtCore import QBasicTimer

from PyQt5.QtCore import QThread
from PyQt5 import QtCore, QtGui

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


import sys
import time
import serial

import paho.mqtt.client as mqttClient

#=======================================================

def on_connect(client, userdata, flags, rc):
     if rc == 0:
        print("Connected to broker 1...")
        global Connected                 
        Connected = True                 
     else:
         print("Connection failed", rc)

def on_message(client, userdata, message):
    global valor
    valor = message.payload
    print("Recebeu: " + valor)

def on_log(client, userdata, level, buf):
    print("log: " + buf)
        
def on_disconnect(client, userdata, flags, rc=0):
    print("Desconectado - code: " + str(rc))


Connected = False    

#broker = "test.mosquitto.org"
broker = "iot.eclipse.org"

client            = mqttClient.Client("controle_reles_1")               
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker)          
client.loop_start()        
 
while Connected != True:     
    time.sleep(0.1)
 
client.subscribe("MQTT/RASPBERRY", 2)

#=======================================================
#=======================================================

def on_connect(client2, userdata, flags, rc):
     if rc == 0:
        print("Connected to broker 2...")
        global Connected                 
        Connected = True                 
     else:
         print("Connection failed", rc)

def on_message(client2, userdata, message):
    global valor2
    valor2 = message.payload
    print("Recebeu: " + valor2)

def on_log(client2, userdata, level, buf):
    print("log: " + buf)
        
def on_disconnect(client2, userdata, flags, rc=0):
    print("Desconectado - code: " + str(rc))


Connected = False    

client2            = mqttClient.Client("controle_reles_2")               
client2.on_connect = on_connect
client2.on_message = on_message

client2.connect(broker)          
client2.loop_start()        
 
while Connected != True:     
    time.sleep(0.1)
 
client2.subscribe("RASPBERRY", 2)

#=======================================================


comport = serial.Serial('/dev/ttyACM0', 9600)



x = 0
y = 0

status        = 0
valor         = 1
valor2        = 2
valor_serial  = 0 

    
class Window(QWidget):

    def __init__(self, parent=None):
        super(Window, self).__init__()

        self.resize(400, 250)
        self.setWindowTitle("MQTT - Alvaro Junior")
            
        self.label = QLabel(self)
        self.label.resize(200, 60)
        self.label.move(10,80)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QtGui.QFont("Arial", 40, QtGui.QFont.Black))
        self.label.setStyleSheet('QLabel {background-color: black;color:yellow;}')
        self.label.setText('--.-')

        self.label2 = QLabel(self)
        self.label2.resize(200, 60)
        self.label2.move(10,150)
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setFont(QtGui.QFont("Arial", 40, QtGui.QFont.Black))
        self.label2.setStyleSheet('QLabel {background-color: black;color:white;}')
        self.label2.setText('--.-')
        
                
        self.button1 = QPushButton('Thread', self)
        self.button1.move(50, 20)
        self.button1.clicked.connect(self.start_loop_1)

        self.button2 = QPushButton('RS232', self)
        self.button2.move(150, 20)
        self.button2.clicked.connect(self.start_loop_2)

        self.button3 = QPushButton('Pub', self)
        self.button3.move(250, 20)
        self.button3.clicked.connect(self.publish)

        self.button4 = QPushButton('timer', self)
        self.button4.move(250, 60)
        self.button4.clicked.connect(self.timer) 

        self.dial = QDial(self)
        self.dial.resize(100, 100)
        self.dial.move(240,100)
        self.dial.setMaximum(100)
        self.dial.setMinimum(0)
        self.dial.setSingleStep(1)
        self.dial.setValue(0)
        self.dial.setNotchesVisible(True)
        self.dial.valueChanged.connect(self.teste_dial)

        
    def timer(self):
        self.timer = QBasicTimer()
        self.timer.start(100, self)

    def timerEvent(self, e):
        self.label.setText(str(valor)+'°C')
        self.label2.setText(str(valor2)+'%U')
            
    #/////////////////////////////////////////////////////
    # Publicaçao do BOTAO
    def publish(self):
        try:            
             client.publish("RASPBERRY", '3')
             print('Publica: 3')
                
        except IOError:
            print("Erro...")
            
    #/////////////////////////////////////////////////////
    # Publicaçao do DIAL
    def teste_dial(self, valor_dial):
        try:    
             client.publish("RASPBERRY", valor_dial)

        except IOError:
            print("Erro...")



 

        
    def start_loop_1(self):
        
        global x
        global status
        
        if (status == 0) & (x == 0):
            self.thread_loop_1 = Loop_1()
            self.thread_loop_1.start()
        else:
            status = 1
            x = 0

    def start_loop_2(self):
        self.thread_loop_2 = Loop_2()
        self.thread_loop_2.start()



 


#/////////////////////////////////////////////////////////////////
# thread Sub              
class Loop_1(QThread):

    def run(self):            
        while True:
            print('Thread:' + str(valor))
            time.sleep(.2)

            

#/////////////////////////////////////////////////////////////////
# serial rs232     
class Loop_2(QThread):

    def run(self):
        while True:          
            valor_serial = comport.readline().decode('utf-8')[:-2]
            print('Serial: ' + valor_serial)
             



            

root = QApplication([])
app = Window()
app.show()
sys.exit(root.exec_())
