""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr

Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""
#Classe nécessaire
import camera

# Bibliothèques nécessaires
import datetime
import numpy
import picamera
import RPi.GPIO as GPIO
import os

from PIL import Image
from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

# Bibliothèques nécessaires
GPIO.setmode(GPIO.BOARD)

def togglelaser532nm(state): #laser 532 nm ON/OFF
    if state:
        GPIO.output(32, False)
    else:
        GPIO.output(32, True)
            
def togglelaser635nm(state): #laser 635 nm ON/OFF
    if state:
        GPIO.output(22, False)
    else:
        GPIO.output(22, True)

def cameraStart(graphic, labelBeamImage, labelHHWValue, expTime): #lance la caméra en plein écran
    camera.startCamera(expTime) #start la preview, voir camera.py
    Ymd = datetime.datetime.now().strftime("%Y-%m-%d") #récupération du jour
    #Recherche de la dernière image sauvée
    os.makedirs("Photos", exist_ok=True)
    os.chdir("Photos")
    os.makedirs(Ymd, exist_ok=True)
    os.chdir(Ymd)
    last_image_saved = "last_image_saved.jpg"
    labelBeamImage.setPixmap(QtGui.QPixmap(last_image_saved)) #affiche l'image dans le widget
    graphic.clear() #reset le graphe d'intensité du faisceau
    plotBeam(graphic, labelHHWValue, last_image_saved) #trace le graphe d'intensité du faisceau
    os.chdir("/home/pi/Desktop/Résultats Capsula") #retourne dans le bon dossier de travail

def plotBeam(graphic, labelHHWValue, image): #calcule et trace le graphe d'intensité du faisceau
    im = Image.open(image) #ouvre la dernière image sauvée par la caméra
    imarray = numpy.array(im) #transforme cette image en matrice
    imarrayutile = imarray[:,:,0] #ne retient que le premier layer (pas d'importance en b&w)
    h = len(imarrayutile[:,0]) #calcule la hauteur de l'image
    w = len(imarrayutile[0,:]) #calcule la largeur de l'image
    x = range(0,w) #création de l'axe des abscisses
    y = imarrayutile[h//2,:] #création de l'axe des ordonnées :
    #on prend la ligne qui correspond au milieu de l'image, c'est pourquoi
    #le faisceau doit être bien au centre de l'image au préalable
    #l'affichage de la cible sur la caméra permet un bon alignement
    maxig = max(y) #recherche du maximum
    #Calcul de la largeur à mi-hauteur
    k = 0
    while y[k] <= maxig/2 and k < len(y)-1:
        k+=1
    hhwg = k
    while y[k] > maxig/2 and k < len(y)-1:
        k+=1
    labelHHWValue.setText(str(k-hhwg)) #affichage de la largeur à mi-hauteur (en pixels)
    graphic.setXRange(0,w) #mise à l'echelle X 
    graphic.plot(x,y) #trace le graphe d'intensité du faisceau
