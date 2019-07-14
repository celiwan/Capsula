""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr
Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""

#Classe nécessaire
import mainwindow as mw

# Bibliothèques nécessaires
import sys
import serial
import os
import RPi.GPIO as GPIO
import datetime
from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

#Lecture des ports GPIO selon leurs positions
GPIO.setmode(GPIO.BOARD)
        
def main():
    #Initialisation des ports GPIO
    GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW) 
    #Affichage de la GUI Capsula
    app = QApplication(sys.argv) 
    form = mw.MainWindow()
    form.show()
    sys.exit(app.exec_())       
 
if __name__ == "__main__":
    main()   
