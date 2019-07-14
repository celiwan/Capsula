""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr

Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""

#Bibliothèques nécessaires
from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

def laserOnFirst(): #crée et affiche le message "Please turn on laser(s) first"
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Please turn on laser(s) first")
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def makeBlankFirst(): #crée et affiche le message "Please make reference first"
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Please make reference first")
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()
