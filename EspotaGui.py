#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Original espota.py by Ivan Grokhotkov:
# https://gist.github.com/igrr/d35ab8446922179dc58c
#
# Modified since 2015-09-18 from Pascal Gollor (https://github.com/pgollor)
# Modified since 2015-11-09 from Hristo Gochkov (https://github.com/me-no-dev)
# Modified since 2016-01-03 from Matthew O'Gorman (https://githumb.com/mogorman)
#
# This script will push an OTA update to the ESP
# use it like: python espota.py -i <ESP_IP_address> -I <Host_IP_address> -p <ESP_port> -P <Host_port> [-a password] -f <sketch.bin>
# Or to upload SPIFFS image:
# python espota.py -i <ESP_IP_address> -I <Host_IP_address> -p <ESP_port> -P <HOST_port> [-a password] -s -f <spiffs.bin>
#
# Changes
# 2015-09-18:
# - Add option parser.
# - Add logging.
# - Send command to controller to differ between flashing and transmitting SPIFFS image.
#
# Changes
# 2015-11-09:
# - Added digest authentication
# - Enhanced error tracking and reporting
#
# Changes
# 2016-01-03:
# - Added more options to parser.
# 
#Changes
# V1.0.0 2018-11-23
# Create grapic version with QT5 and Python 3.7
# Christophe Caron www.caron.ws
#Changes 
# V1.0.1 2018-11-18
# validation of values
# Christophe Caron www.caron.ws

from __future__ import print_function
import socket
import sys
import os
import optparse
import hashlib
import random
import time

# Commands
FLASH = 0
SPIFFS = 100
AUTH = 200
PROGRESS = False


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QColorDialog, QDialog,
        QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
        QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton,QAction)

import ipaddress


class Ui_Form(QtWidgets.QWidget):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(512, 480)
        Form.setMaximumSize(QtCore.QSize(640, 480))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo-Domo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.checkBox_SIPFFS = QtWidgets.QCheckBox(Form)
        self.checkBox_SIPFFS.setGeometry(QtCore.QRect(400, 78, 96, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_SIPFFS.setFont(font)
        self.checkBox_SIPFFS.setObjectName("checkBox_SIPFFS")
        self.label_Tx_Chemin = QtWidgets.QLabel(Form)
        self.label_Tx_Chemin.setGeometry(QtCore.QRect(0, 26, 121, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_Tx_Chemin.setFont(font)
        self.label_Tx_Chemin.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Tx_Chemin.setObjectName("label_Tx_Chemin")
        self.label_Chemin = QtWidgets.QLabel(Form)
        self.label_Chemin.setGeometry(QtCore.QRect(120, 26, 391, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_Chemin.setFont(font)
        self.label_Chemin.setInputMethodHints(QtCore.Qt.ImhMultiLine)
        self.label_Chemin.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Chemin.setText("")
        self.label_Chemin.setObjectName("label_Chemin")
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setGeometry(QtCore.QRect(4, 344, 505, 127))
        self.textEdit.setAutoFillBackground(False)
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setObjectName("textEdit")
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(4, 300, 505, 29))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.splitter_2 = QtWidgets.QSplitter(Form)
        self.splitter_2.setGeometry(QtCore.QRect(0, 230, 511, 59))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.pushButton_Fichier = QtWidgets.QPushButton(self.splitter_2)
        self.pushButton_Fichier.setMinimumSize(QtCore.QSize(250, 48))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_Fichier.setFont(font)
        self.pushButton_Fichier.setFlat(False)
        self.pushButton_Fichier.setObjectName("pushButton_Fichier")
        self.pushButton_MaJ = QtWidgets.QPushButton(self.splitter_2)
        self.pushButton_MaJ.setMinimumSize(QtCore.QSize(250, 48))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_MaJ.setFont(font)
        self.pushButton_MaJ.setFlat(False)
        self.pushButton_MaJ.setObjectName("pushButton_MaJ")
        self.splitter_7 = QtWidgets.QSplitter(Form)
        self.splitter_7.setGeometry(QtCore.QRect(12, 74, 365, 133))
        self.splitter_7.setOrientation(QtCore.Qt.Vertical)
        self.splitter_7.setObjectName("splitter_7")
        self.splitter = QtWidgets.QSplitter(self.splitter_7)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label_IP_Module = QtWidgets.QLabel(self.splitter)
        self.label_IP_Module.setMinimumSize(QtCore.QSize(175, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_IP_Module.setFont(font)
        self.label_IP_Module.setFrameShape(QtWidgets.QFrame.Box)
        self.label_IP_Module.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_IP_Module.setObjectName("label_IP_Module")
        self.lineEdit_IP_Module = QtWidgets.QLineEdit(self.splitter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_IP_Module.setFont(font)
        self.lineEdit_IP_Module.setFrame(True)
        self.lineEdit_IP_Module.setObjectName("lineEdit_IP_Module")
        self.splitter_3 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.label_Port_Module = QtWidgets.QLabel(self.splitter_3)
        self.label_Port_Module.setMinimumSize(QtCore.QSize(175, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_Port_Module.setFont(font)
        self.label_Port_Module.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Port_Module.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_Port_Module.setObjectName("label_Port_Module")
        self.lineEdit_Port_Module = QtWidgets.QLineEdit(self.splitter_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_Port_Module.setFont(font)
        self.lineEdit_Port_Module.setText("")
        self.lineEdit_Port_Module.setFrame(True)
        self.lineEdit_Port_Module.setObjectName("lineEdit_Port_Module")
        self.splitter_4 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_4.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_4.setObjectName("splitter_4")
        self.label_IP_Hote = QtWidgets.QLabel(self.splitter_4)
        self.label_IP_Hote.setMinimumSize(QtCore.QSize(175, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_IP_Hote.setFont(font)
        self.label_IP_Hote.setFrameShape(QtWidgets.QFrame.Box)
        self.label_IP_Hote.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_IP_Hote.setObjectName("label_IP_Hote")
        self.lineEdit_IP_Hote = QtWidgets.QLineEdit(self.splitter_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_IP_Hote.setFont(font)
        self.lineEdit_IP_Hote.setText("")
        self.lineEdit_IP_Hote.setFrame(True)
        self.lineEdit_IP_Hote.setObjectName("lineEdit_IP_Hote")
        self.splitter_5 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_5.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_5.setObjectName("splitter_5")
        self.label_Port_Hote = QtWidgets.QLabel(self.splitter_5)
        self.label_Port_Hote.setMinimumSize(QtCore.QSize(175, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_Port_Hote.setFont(font)
        self.label_Port_Hote.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Port_Hote.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_Port_Hote.setObjectName("label_Port_Hote")
        self.lineEdit_Port_Hote = QtWidgets.QLineEdit(self.splitter_5)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_Port_Hote.setFont(font)
        self.lineEdit_Port_Hote.setText("")
        self.lineEdit_Port_Hote.setFrame(True)
        self.lineEdit_Port_Hote.setObjectName("lineEdit_Port_Hote")
        self.splitter_6 = QtWidgets.QSplitter(self.splitter_7)
        self.splitter_6.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_6.setObjectName("splitter_6")
        self.label_MdP = QtWidgets.QLabel(self.splitter_6)
        self.label_MdP.setMinimumSize(QtCore.QSize(175, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_MdP.setFont(font)
        self.label_MdP.setFrameShape(QtWidgets.QFrame.Box)
        self.label_MdP.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_MdP.setObjectName("label_MdP")
        self.lineEdit_MdP = QtWidgets.QLineEdit(self.splitter_6)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_MdP.setFont(font)
        self.lineEdit_MdP.setText("")
        self.lineEdit_MdP.setFrame(True)
        self.lineEdit_MdP.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_MdP.setObjectName("lineEdit_MdP")
        self.pushButton_EN = QtWidgets.QPushButton(Form)
        self.pushButton_EN.setGeometry(QtCore.QRect(404, 2, 107, 23))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_EN.setFont(font)
        self.pushButton_EN.setObjectName("pushButton_EN")

        self.messageBox = QMessageBox()
        self.messageBox.setIcon(QMessageBox.Information)
        self.messageBox.setText("This is a message box")       
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo-Domo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.messageBox.setWindowIcon(icon)
        self.messageBox.setStandardButtons(QMessageBox.Ok)



        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        #Commande des boutons
        self.pushButton_Fichier.clicked.connect(self.setOpenFileName)
        self.pushButton_MaJ.clicked.connect(CdeFlash)
        self.pushButton_EN.clicked.connect(Traduction)  


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Estopa Gui"))
        self.checkBox_SIPFFS.setToolTip(_translate("Form", "<html><head/><body><p>Cochez pour téléverser votre fichier SIPFFS</p></body></html>"))
        self.checkBox_SIPFFS.setText(_translate("Form", " SIPFFS"))
        self.label_Tx_Chemin.setText(_translate("Form", "Chemin du fichier: "))
        self.label_Chemin.setText(_translate("Form", ""))
        self.pushButton_Fichier.setText(_translate("Form", "Sélection du fichier binaire"))
        self.pushButton_MaJ.setText(_translate("Form", "Mise à jour"))
        self.label_IP_Module.setText(_translate("Form", "Adresse IP Module: "))
        self.lineEdit_IP_Module.setToolTip(_translate("Form", "<html><head/><body><p>Entrez votre adresse IP:192.168.1.20</p></body></html>"))
        self.lineEdit_IP_Module.setText(_translate("Form", ""))
        self.label_Port_Module.setText(_translate("Form", "Port Module: "))
        self.lineEdit_Port_Module.setToolTip(_translate("Form", "<html><head/><body><p>Vide=Valeur par défaut ou numéro du port: 8266</p></body></html>"))
        self.label_IP_Hote.setText(_translate("Form", "Adresse IP Hôte: "))
        self.lineEdit_IP_Hote.setToolTip(_translate("Form", "<html><head/><body><p>Vide= Valeur par défaut ou Entrez votre adresse IP:192.168.1.20</p></body></html>"))
        self.label_Port_Hote.setText(_translate("Form", "Port Hôte: "))
        self.lineEdit_Port_Hote.setToolTip(_translate("Form", "<html><head/><body><p>Vide= Valeur par défaut ou Entrez votre port : 1000</p></body></html>"))
        self.lineEdit_Port_Hote.setText(_translate("Form", ""))
        self.label_MdP.setText(_translate("Form", "Mot de passe: "))
        self.lineEdit_MdP.setToolTip(_translate("Form", "<html><head/><body><p>Vide= Valeur par défaut ou Entrez votre mot de passe</p></body></html>"))
        self.pushButton_EN.setText(_translate("Form", "English"))
        self.messageBox.setWindowTitle(_translate("Form","Message d'érreur"))

    def retranslateUi_En(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Estopa Gui"))
        self.checkBox_SIPFFS.setToolTip(_translate("Form", "<html><head/><body><p>Check to upload your file SIPFFS</p></body></html>"))
        self.checkBox_SIPFFS.setText(_translate("Form", " SIPFFS"))
        self.label_Tx_Chemin.setText(_translate("Form", "File path: "))
        self.label_Chemin.setText(_translate("Form", ""))
        self.pushButton_Fichier.setText(_translate("Form", "Selecting the binary file"))
        self.pushButton_MaJ.setText(_translate("Form", "Update"))
        self.label_IP_Module.setText(_translate("Form", "IP address module: "))
        self.lineEdit_IP_Module.setToolTip(_translate("Form", "<html><head/><body><p>Enter your address IP:192.168.1.20</p></body></html>"))
        self.lineEdit_IP_Module.setText(_translate("Form", ""))
        self.label_Port_Module.setText(_translate("Form", "Port Module: "))
        self.lineEdit_Port_Module.setToolTip(_translate("Form", "<html><head/><body><p>Empty = Default value or number of the port: 8266</p></body></html>"))
        self.label_IP_Hote.setText(_translate("Form", "IP adress Host: "))
        self.lineEdit_IP_Hote.setToolTip(_translate("Form", "<html><head/><body><p>Empty = Default value or Enter your IP address:192.168.1.20</p></body></html>"))
        self.label_Port_Hote.setText(_translate("Form", "Port Host: "))
        self.lineEdit_Port_Hote.setToolTip(_translate("Form", "<html><head/><body><p>Empty = Default value or Enter your port : 1000</p></body></html>"))
        self.lineEdit_Port_Hote.setText(_translate("Form", ""))
        self.label_MdP.setText(_translate("Form", "Password: "))
        self.lineEdit_MdP.setToolTip(_translate("Form", "<html><head/><body><p>Empty= Default value or Enter your password</p></body></html>"))
        self.pushButton_EN.setText(_translate("Form", "French"))
        self.messageBox.setWindowTitle(_translate("Form","Error message"))

    def setOpenFileName(self):    
        options = QFileDialog.Options()
        options = QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Fichier Binaire","",
                "Fichier Bin (*.bin)")
        if fileName:
            self.label_Chemin.setText(fileName)


def CdeFlash():
    ui.textEdit.setText("")
    if ui.label_Chemin.text()=="":
        ui.messageBox.setText("No files selected")
        if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Aucun fichier selectionné")
        ui.messageBox.exec_() 
        return
    try:
        ip = ipaddress.ip_address(ui.lineEdit_IP_Module.text())
        ui.messageBox.setText("Invalid IP address for module")
    except ValueError:
        if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Adresse IP invalide pour le module")
        ui.messageBox.exec_()
        return
    except:
        if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Adresse IP invalide pour le module")
        ui.messageBox.exec_()
        return
    sys.argv=["-i",ui.lineEdit_IP_Module.text(),"-f",ui.label_Chemin.text(),"--auth="+ui.lineEdit_MdP.text(),"-r"]
    if ui.checkBox_SIPFFS.isChecked()==True:
        sys.argv.append("-s")
    if ui.lineEdit_Port_Module.text()!="":
        validation=checkIntValue(ui.lineEdit_Port_Module.text(),5000,60000)
        if validation=="ko":
            ui.messageBox.setText("Invalid value for module port")
            if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Valeur invalide pour le port du module")
            ui.messageBox.exec_()
            return
        sys.argv.append("--port="+(ui.lineEdit_Port_Module.text()))
    if ui.lineEdit_Port_Hote.text()!="":
        validation=checkIntValue(ui.lineEdit_Port_Hote.text(),10000,60000)
        if validation=="ko":
            ui.messageBox.setText("Invalid value for host port")
            if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Valeur invalide pour le port de l'hôte")
            ui.messageBox.exec_()
            return
        sys.argv.append("--host_port="+(ui.lineEdit_Port_Hote.text()))
    if ui.lineEdit_IP_Hote.text()!="":
        try:
            ip = ipaddress.ip_address(ui.lineEdit_IP_Hote.text())
            ui.messageBox.setText("Invalid IP address for host")
        except ValueError:
            if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Adresse IP invalide pour l'hôte")
            ui.messageBox.exec_()
            return
        except:
            if ui.pushButton_EN.text() !="French": ui.messageBox.setText("Adresse IP invalide pour l'hôte")
            ui.messageBox.exec_()
            return
        sys.argv.append("--host_ip="+(ui.lineEdit_IP_Hote.text()))
    flashing(sys.argv)

def Traduction():
    if ui.pushButton_EN.text()=="English":
        ui.retranslateUi_En(Form)
    else:
        ui.retranslateUi(Form)

def checkIntValue(valeur,minValue,maxValue):
    try:
        intTarget = int(valeur)
        if intTarget <minValue  or intTarget > maxValue:
            return("ko")
        else:
            return("ok")
    except ValueError:
        return("ko")
    except:
        return ("ko") 

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
  if (PROGRESS):
    barLength = 60 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
      progress = float(progress)
    if not isinstance(progress, float):
      progress = 0
      status = "error: progress var must be float\r\n"
    if progress < 0:
      progress = 0
      status = "Halt...\r\n"
    if progress >= 1:
      progress = 1
      status = "Done...\r\n"
    ui.textEdit.insertPlainText(status)
    ui.progressBar.setProperty("value", int(progress*100))

  else:
    ui.textEdit.insertPlainText(".")

def serve(remoteAddr, localAddr, remotePort, localPort, password, filename, command = FLASH):
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = (localAddr, localPort)
  ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[INFO]: Starting on '+str(server_address[0])+":"+ str(server_address[1]))
  try:
    sock.bind(server_address)
    sock.listen(1)
  except:
    ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+"[ERROR]:Listen Failed")
    return 1

  content_size = os.path.getsize(filename)
  f = open(filename,'rb')
  file_md5 = hashlib.md5(f.read()).hexdigest()
  f.close()
  ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[INFO]: Upload size: '+str(content_size))
  message = '%d %d %d %s\n' % (command, localPort, content_size, file_md5)

  # Wait for a connection
  ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[INFO]: Sending invitation to: '+ remoteAddr)
  sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  remote_address = (remoteAddr, int(remotePort))
  sent = sock2.sendto(message.encode(), remote_address)
  sock2.settimeout(10)
  try:
    data = sock2.recv(128).decode()
  except:
    ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: No Answer')
    sock2.close()
    return 1
  if (data != "OK"):
    if(data.startswith('AUTH')):
      nonce = data.split()[1]
      cnonce_text = '%s%u%s%s' % (filename, content_size, file_md5, remoteAddr)
      cnonce = hashlib.md5(cnonce_text.encode()).hexdigest()
      passmd5 = hashlib.md5(password.encode()).hexdigest()
      result_text = '%s:%s:%s' % (passmd5 ,nonce, cnonce)
      result = hashlib.md5(result_text.encode()).hexdigest()
      ui.textEdit.insertPlainText('Authenticating...')
      sys.stderr.flush()
      message = '%d %s %s\n' % (AUTH, cnonce, result)
      sock2.sendto(message.encode(), remote_address)
      sock2.settimeout(10)
      try:
        data = sock2.recv(32).decode()
      except:
        ui.textEdit.insertPlainText('FAIL\n')
        ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: No Answer to our Authentication')
        sock2.close()
        return 1
      if (data != "OK"):
        ui.textEdit.insertPlainText('FAIL\n')
        ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: ' + data)
        sock2.close()
        return 1
      ui.textEdit.insertPlainText('OK\n')
    else:
      ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: Bad Answer: ' + data)
      sock2.close()
      return 1
  sock2.close()

  ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[INFO]: Waiting for device...')
  try:
    sock.settimeout(10)
    connection, client_address = sock.accept()
    sock.settimeout(None)
    connection.settimeout(None)
  except:
    ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: No response from device')
    sock.close()
    return 1

  try:
    f = open(filename, "rb")
    if (PROGRESS):
      update_progress(0)
    else:
      ui.textEdit.insertPlainText('Uploading')
      sys.stderr.flush()
    offset = 0
    while True:
      chunk = f.read(1460)
      if not chunk: break
      offset += len(chunk)
      update_progress(offset/float(content_size))
      connection.settimeout(10)
      try:
        connection.sendall(chunk)
        res = connection.recv(4)
      except:
        ui.textEdit.insertPlainText('\n')
        ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: Error Uploading')
        connection.close()
        f.close()
        sock.close()
        return 1

    ui.textEdit.insertPlainText('\n')
    ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[INFO]: Waiting for result...')
    # libraries/ArduinoOTA/ArduinoOTA.cpp L311 L320
    # only sends digits or 'OK'. We must not not close
    # the connection before receiving the 'O' of 'OK'
    try:
      connection.settimeout(60)
      while True:
        if connection.recv(32).decode().find('O') >= 0: break
      ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[INFO]: Result: OK')
      connection.close()
      f.close()
      sock.close()
      if (data != "OK"):
        ui.textEdit.insertPlainText('\n')
        ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: ' + data)
        return 1;
      return 0
    except:
      ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+'[ERROR]: No Result!')
      connection.close()
      f.close()
      sock.close()
      return 1

  finally:
    connection.close()
    f.close()

  sock.close()
  return 1
# end serve

def parser(unparsed_args):
  parser = optparse.OptionParser(
    usage = "%prog [options]",
    description = "Transmit image over the air to the esp8266 module with OTA support."
  )

  # destination ip and port
  group = optparse.OptionGroup(parser, "Destination")
  group.add_option("-i", "--ip",
    dest = "esp_ip",
    action = "store",
    help = "ESP8266 IP Address.",
    default = False
  )
  group.add_option("-I", "--host_ip",
    dest = "host_ip",
    action = "store",
    help = "Host IP Address.",
    default = "0.0.0.0"
  )
  group.add_option("-p", "--port",
    dest = "esp_port",
    type = "int",
    help = "ESP8266 ota Port. Default 8266",
    default = 8266
  )
  group.add_option("-P", "--host_port",
    dest = "host_port",
    type = "int",
    help = "Host server ota Port. Default random 10000-60000",
    default = random.randint(10000,60000)
  )
  parser.add_option_group(group)

  # auth
  group = optparse.OptionGroup(parser, "Authentication")
  group.add_option("-a", "--auth",
    dest = "auth",
    help = "Set authentication password.",
    action = "store",
    default = ""
  )
  parser.add_option_group(group)

  # image
  group = optparse.OptionGroup(parser, "Image")
  group.add_option("-f", "--file",
    dest = "image",
    help = "Image file.",
    metavar="FILE",
    default = None
  )
  group.add_option("-s", "--spiffs",
    dest = "spiffs",
    action = "store_true",
    help = "Use this option to transmit a SPIFFS image and do not flash the module.",
    default = False
  )
  parser.add_option_group(group)

  # output group
  group = optparse.OptionGroup(parser, "Output")
  group.add_option("-d", "--debug",
    dest = "debug",
    help = "Show debug output. And override loglevel with debug.",
    action = "store_true",
    default = False
  )
  group.add_option("-r", "--progress",
    dest = "progress",
    help = "Show progress output. Does not work for ArduinoIDE",
    action = "store_true",
    default = False
  )
  parser.add_option_group(group)

  (options, args) = parser.parse_args(unparsed_args)

  return options
# end parser


def flashing(args):
 # get options
  options = parser(args)

  ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+"[DEBUG]: Options: "+str(options))

  # check options
  global PROGRESS
  PROGRESS = options.progress
  if (not options.esp_ip or not options.image):
    ui.textEdit.insertPlainText((time.strftime("%H:%M:%S", time.gmtime()))+"[CRITICAL]: Not enough arguments.")

    return 1
  # end if

  command = FLASH
  if (options.spiffs):
    command = SPIFFS
  # end if

  return serve(options.esp_ip, options.host_ip, options.esp_port, options.host_port, options.auth, options.image, command)
# end main

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

