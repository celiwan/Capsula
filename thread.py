""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr
Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter

Il y a utilisation de deux threads ici car il n'est pas possible d'afficher la
barre de progression en temps réel en n'utilisant qu'un seul thread"""


# Bibliothèques nécessaires
import serial
from PyQt5.QtWidgets import *
from threading import Thread
from time import sleep

#Thread 1 : Afficher la barre de chargement du 'Make reference'
class LoadingBar(Thread):

    def __init__(self, QProgressDialog): #initialisation
        Thread.__init__(self) #initialisation du thread
        self.QPD = QProgressDialog #initialisation de la barre de dialogue

    def run(self): #s'execute lors de thread.start() : affiche la barre de dialogue
        self.QPD.show()

#Thread 2 : Calculer la reference et mettre à jour la barre de chargement
class MakeBlank(Thread):

    def __init__(self, QProgressDialog): #initialisation
        Thread.__init__(self) #initialisation du thread
        self.blank = 0 #initialisation de la valeur de référence
        
        self.QPD = QProgressDialog #initialisation de la barre de dialogue
        #Connexion Rpi/Arduino via port USB (vitesse de 115200 bauds)
        self.ser = serial.Serial('/dev/ttyACM0', 115200)

    def run(self): #s'execute lors de thread.start() : met à jour la barre de dialogue
        self.blank = 0
        for k in range(10):
            self.ser.write(bytes(b'1')) #demande une donnée à Arduino
            self.blank += float(self.ser.readline().strip().decode('ascii')) #reçoit la donnée
            print(self.blank)
            sleep(0.5) #attente de 0.5s pour une meilleure précision
            self.QPD.setValue(k*10+10) #mise à jour de la barre de dialogue
        self.blank /= 10 #calcul du blanc via une moyenne des 10 valeurs
        

