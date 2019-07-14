""" Code écrit par :
Nelson HELAINE
nelson.helaine@institutoptique.fr

Eric MORET
eric.moret@institutoptique.fr

Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à nous contacter"""

#Classes nécessaires
import capsule
import thread
import thread_detect_with_vid as thread2

# Bibliothèques nécessaires
import camera
import datetime
import information as info
import laser as las
import moteur as mot
import os
import picamera
import pygame
import RPi.GPIO as GPIO
import serial
import sys

from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from pyqtgraph import PlotWidget
from time import sleep

# Interface faite via QtDesigner
import capsula
class MainWindow(QMainWindow, capsula.Ui_MainWindow):

    def __init__(self):
        
        #Initialisation de la GUI, des connections actionneurs/fonctions et des modules supplémentaires non supportés par QtCreator
        os.chdir("/home/pi/Desktop/Résultats Capsula") #dossier de travail
        super(self.__class__, self).__init__()
        self.setupUi(self) #initialisation de la GUI Capsula
        #Ajout des Widgets non proposés par QtDesigner
        #Graphe intensité du laser
        self.graphicsViewLaserBeamProfile = PlotWidget(self.tabWidgetLaserControl)
        self.graphicsViewLaserBeamProfile.setGeometry(QtCore.QRect(310, 60, 475, 300))
        self.graphicsViewLaserBeamProfile.setXRange(0,480)
        self.graphicsViewLaserBeamProfile.setYRange(0,255)
        self.graphicsViewLaserBeamProfile.setObjectName("graphicsViewLaserBeamProfile")
        #Graphe détection 
        self.graphicsViewRealPlot = PlotWidget(self.tabWidgetDetection)
        self.graphicsViewRealPlot.setGeometry(QtCore.QRect(10, 10, 550, 310))
        self.graphicsViewRealPlot.setXRange(0,400)
        self.graphicsViewRealPlot.setYRange(0,1)
        self.graphicsViewRealPlot.setObjectName("graphicsViewRealPlot")
        #Message "Making reference, please wait"
        self.messageBoxBlank = QtGui.QProgressDialog("Making reference, please wait...", "Cancel",0, 100, self.tabWidgetDetection)
        self.messageBoxBlank.setWindowTitle("Wait...")

        #Initialisation des threads
        self.thread1 = thread.LoadingBar(self.messageBoxBlank) 
        self.thread2 = thread.MakeBlank(self.messageBoxBlank)

        #Connexion boutons/méthodes
        self.checkBoxLaser532nm.clicked.connect(lambda: las.togglelaser532nm(self.checkBoxLaser532nm.isChecked()))
        self.checkBoxLaser635nm.clicked.connect(lambda: las.togglelaser635nm(self.checkBoxLaser635nm.isChecked()))
        self.pushButtonDutyCycleM.clicked.connect(lambda: mot.dutyCycleM(int(self.lcdNumberDutyCycleM.value())))
        self.pushButtonBlank.clicked.connect(self.makeBlank)
        self.pushButtonClear.clicked.connect(self.on_init)
        self.pushButtonChangeDirectionM.clicked.connect(mot.changeDirectionM)
        self.pushButtonRunAndGoBackM.clicked.connect(mot.runAndGoBackM)
        self.pushButtonSeeCamera.clicked.connect(lambda: las.cameraStart(self.graphicsViewLaserBeamProfile, self.labelBeamImage, self.labelHHWValue, int(self.lineEditExposureTime.displayText())))
        self.pushButtonStart.clicked.connect(self.startAcquisition)
        self.pushButtonStartMotor.clicked.connect(mot.startM)
        self.pushButtonStop.clicked.connect(self.stopAcquisition)
        self.pushButtonStopMotor.clicked.connect(mot.stopM)
        self.radioButtonContinu.clicked.connect(self.continuousDisplay)
        self.radioButtonSegmente.clicked.connect(self.segmentedDisplay)
        
        #Connexion actions/méthodes
        self.actionOpen_detection_configuration.triggered.connect(self.openDetectionConfiguration)
        self.actionOpen_pump_configuration.triggered.connect(self.openPumpConfiguration)
        self.actionOpen_motor_configuration.triggered.connect(self.openMotorConfiguration)
        self.actionPause.triggered.connect(self.pauseAcquisition)
        self.actionQuit.triggered.connect(self.closeEvent)
        self.actionSave_detection_configuration.triggered.connect(self.saveDetectionConfiguration)
        self.actionSave_pump_configuration.triggered.connect(self.savePumpConfiguration)
        self.actionSave_motor_configuration.triggered.connect(self.saveMotorConfiguration)
        self.actionStart_Aquisition.triggered.connect(self.startAcquisition)
        self.actionStop_Aquisition.triggered.connect(self.stopAcquisition)

        #Initialisation timer
        self.timer = QtCore.QTimer()
        self.pasDeTemps = float(self.lineEditSamplingPeriod.displayText()) #vitesse d'affichage
        self.timer.setInterval(self.pasDeTemps)
        self.timer.timeout.connect(self.update) #connexion timer out/update data
        
        #Initialisation graphe
        self.on_init()

        #Initialisation lasers
        GPIO.output(22, True)
        GPIO.output(32, True)

        #Déclaration variables
        self.blankDone = False
        self.inCaps = False
        self.noFloatDetected = True
        self.oldLineEdit = ""
        self.pause = False
        self.start = False
        self.stop = False        
        self.withlVid = False
        self.withrVid = False

        #Connexion Rpi/Arduino via USB
        self.ser = serial.Serial('/dev/ttyACM0', 250000)

#Onglet Lasers

        """voir laser.py"""
        
#Onglet Fluidics

        """rien pour l'instant"""

#Onglet Results


    def on_init(self): #Initialise la GUI
        os.chdir("/home/pi/Desktop/Résultats Capsula") #dossier de travail
        global blank, curve, datan, k, maxi, mini, n, ptr, label, tabCaps #variables utilisées dans plusieurs fonctions
        self.graphicsViewRealPlot.clear() #efface la courbe du graphe
        self.graphicsViewRealPlot.setXRange(0,300) #mise à l'echelle X 
        
        datan = [0] #initialise le tableau datas normalisées
        curve = self.graphicsViewRealPlot.plot(datan)#initialise la courbe
        #initialisation des variables semi-locales
        k = 0
        label = 0
        maxi = 0 #maxi et mini sont changés à la première itération
        mini = 1000
        n = 300
        ptr = 0
        tabCaps = [] #initialise le tableau qui stocke les cellules à leur passage
        self.labelCurrentValue.setText("") #reset l'affichage de Current value
        self.lcdNumberCapsuleCounter.display(0) #reset le compteur de capsules
        self.labelConsole.setText("") #reset l'affichage de la mini console
        self.segmented = True #par défaut : affichage segmenté

    def makeBlank(self): #fait la reference et affiche son chargement via les threads
        if (self.checkBoxLaser635nm.isChecked() | self.checkBoxLaser532nm.isChecked()):
            #reset des threads
            self.thread1 = thread.LoadingBar(self.messageBoxBlank)
            self.thread2 = thread.MakeBlank(self.messageBoxBlank)
            #start des threads
            self.thread1.start()
            self.thread2.start()
            #autorise l'utilisateur à faire une acquisition
            self.pushButtonClear.setEnabled(True) 
            self.pushButtonStart.setEnabled(True)
            self.pushButtonStop.setEnabled(True)
            self.lcdNumberCapsuleCounter.setEnabled(True)
            #la référence est désormais fait
            self.blankDone = True
        else:
            info.laserOnFirst() #demande de faire le blanc en premier

    def startAcquisition(self):#se produit en lançant l'acquisition
        
        if self.blankDone: #si la référence a été faite
             global f, fn, fs, fp #les fichiers seront des variables semi-locales
             
             self.on_init() #réinitialise tous les paramètres
             #récupération du jour et de l'heure de l'acquisiton
             Ymd = datetime.datetime.now().strftime("%Y-%m-%d")
             YmdHMS = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
             #vérification et/ou création du dossier de l'acquisition
             os.makedirs("Datas", exist_ok=True)
             os.chdir("Datas")
             os.makedirs(Ymd, exist_ok=True)
             os.chdir(Ymd)
             os.chmod('.', 0o777) #changement des droits : tout le monde peut écrire dans le dossier et y supprimer des éléments
             #création des fichiers de sauvegardes
             f = open("data" + YmdHMS + ".txt", "w")
             fn = open("datan" + YmdHMS + ".txt", "w")
             fs = open("stats" + YmdHMS + ".txt", "w")
             fp = open("plotbeam" + YmdHMS + ".txt", "w")
             fs.write("Statistiques de cette acquisiton :\n")
             os.chdir("/home/pi/Desktop/Résultats Capsula") #retour au dossier de travail
             #Changement des états
             self.pause = False
             self.start = True
             self.stop = False
             #Lancement de l'acquisition
             
             if self.actionLive_and_record_video_with_detection.isChecked() and self.actionRecord_video_with_detection.isChecked():
                #affiche "Choose only one option" si les deux options sont cochées
                 msg = QMessageBox()
                 msg.setIcon(QMessageBox.Information)
                 msg.setText("Choose only one option")
                 msg.setWindowTitle("Information")
                 msg.setStandardButtons(QMessageBox.Ok)
                 msg.exec_()
             elif self.actionLive_and_record_video_with_detection.isChecked():
                 #pour l'option Live + record :
                 self.pasDeTemps = int(self.lineEditSamplingPeriod.displayText()) #période d'échantillonage modifiée car l'affichage ralentit le programme
                 self.timer.setInterval(self.pasDeTemps)
                 self.thread3 = thread2.PreviewCam(int(self.lineEditExposureTime.displayText())) #initialise le thread d'affichage de la caméra
                 self.thread3.start() #affiche la caméra (voir thread_detect_with_vid.py
                 self.withlVid = True #état : live + record
                 self.actionLive_and_record_video_with_detection.setCheckable(False) #pour ne pas changer l'option en cours d'acquisition
                 self.timer.start() #lance le timer
             elif self.actionRecord_video_with_detection.isChecked():
                 #pour l'option record :
                 i = 1
                 global cam #variable semi-locale
                 self.pasDeTemps = int(self.lineEditSamplingPeriod.displayText()) #vitesse d'affichage
                 self.timer.setInterval(self.pasDeTemps)
                 #initialisation de la caméra pour filmer (voir camera.py)
                 cam = picamera.PiCamera()
                 cam.resolution = (640, 480)
                 cam.framerate = float(40)
                 cam.shutter_speed = int(self.lineEditExposureTime.displayText())
                 #vérification et/ou création du dossier de l'acquisition
                 os.makedirs("Datas", exist_ok=True)
                 os.chdir("Datas")
                 os.makedirs(Ymd, exist_ok=True)
                 os.chdir(Ymd)
                 cam.start_recording("vdata" + YmdHMS + '.h264') #création du fichier
                 os.chdir("/home/pi/Desktop/Résultats Capsula") #retour au dossier de travail
                 
                 self.withrVid = True #état : record
                 self.actionRecord_video_with_detection.setCheckable(False) #pour ne pas changer l'option en cours d'acquisition
                 self.timer.start() #lance le timer
                 
                 
             else:
                 #sans option :
                 self.pasDeTemps = float(self.lineEditSamplingPeriod.displayText()) #vitesse d'affichage
                 self.timer.setInterval(self.pasDeTemps)               
                 self.timer.start() #lance le timer
        else: #si la référence n'est pas faite, la faire d'abord
            info.makeBlankFirst()          

    def update(self): #met à jour les données en temps réel sur le graphe
        
        self.ser.write(bytes(b'1')) #demande une donnée à Arduino
        value = float(self.ser.readline().strip().decode('ascii')) #reçoit la donnée
        if self.pasDeTemps > 10:
            self.saveData(value) #lance saveData
            #self.capsule(value) #lance capsule
            self.labelCurrentValue.setText(str(round(value,5))) #affiche la current value avec 6 chiffres

        if self.pasDeTemps < 10:
            self.saveData2(value) #lance saveData
            #self.capsule(value) #lance capsule
            self.labelCurrentValue.setText(str(round(value,5))) #affiche la current value avec 6 chiffres 
        
    def saveData2(self,value)
        global curve, datan, ptr, mini, maxi, n, k, blank, label #récupère les variables semi-locales
        blank = self.thread2.blank #récupère la valeur de reference
        mini = min(value, mini) #récupère le signal min et max pour le fichier stats
        maxi = max(value, maxi)
        datan.append(value/blank) #normalisation de la donnée par rapport au blanc
        f.write(str(round((len(datan)-1)*self.pasDeTemps/1000,8)) + "\t" + str(value) + "\n") #écriture dans le txt data
        fn.write(str(round((len(datan)-1)*self.pasDeTemps/1000,8)) + "\t" + str(value/blank) + "\n") #écriture dans le txt datan

    def saveData(self,value): #sauve la donnée dans le txt et l'affiche sur le graphe
        global curve, datan, ptr, mini, maxi, n, k, blank, label #récupère les variables semi-locales
        blank = self.thread2.blank #récupère la valeur de reference
        mini = min(value, mini) #récupère le signal min et max pour le fichier stats
        maxi = max(value, maxi)
        #mode affichage segmenté
        if self.segmented:
            if  len(datan) < 300: #tant que le graphe n'est pas rempli
                datan.append(value/blank) #normalisation de la donnée par rapport au blanc
                f.write(str(round((len(datan)-1)*self.pasDeTemps/1000,8)) + "\t" + str(value) + "\n") #écriture dans le txt data
                fn.write(str(round((len(datan)-1)*self.pasDeTemps/1000,8)) + "\t" + str(value/blank) + "\n") #écriture dans le txt datan
                k += 1
            else:
                if k>=300: #lorsque le tableau est rempli, n'affiche que 300 valeurs
                    k = 0
                    self.graphicsViewRealPlot.setXRange(n, n+300) #mise à l'échelle X
                    n += 300
                datan[:-1] = datan[1:] #datan est décalé de 1 vers la gauche
                datan[-1] = value/blank #ajoute à datan la nouvelle donnée normalisée
                f.write(str(round((ptr + 300)*self.pasDeTemps/1000,8)) + "\t" + str(value) + "\n") #écriture dans le txt data
                fn.write(str(round((ptr + 300)*self.pasDeTemps/1000,8)) + "\t" + str(value/blank) + "\n") #écriture dans le txt datan
                ptr += 1 #incrémente le pointeur
                k += 1
                curve.setPos(ptr, 0) #positionne l'origine du graphe
        #mode affichage continu
        else:
            if  len(datan) < 300: #tant que le graphe n'est pas rempli
                datan.append(value/blank) #normalisation de la donnée par rapport au blanc
                f.write(str(round((len(datan)-1)*self.pasDeTemps/1000,8)) + "\t" + str(value) + "\n") #écriture dans le txt data
                fn.write(str(round((len(datan)-1)*self.pasDeTemps/1000,8)) + "\t" + str(value/blank) + "\n") #écriture dans le txt datan
            else: #lorsque le graphe est rempli, n'affiche que 300 valeurs
                self.graphicsViewRealPlot.setXRange(ptr,ptr+300) #mise à l'échelle X
                datan[:-1] = datan[1:] #data est décalé de 1 vers la gauche
                datan[-1] = value/blank #ajoute à data la nouvelle donnée
                f.write(str(round((ptr + 300)*self.pasDeTemps/1000,8)) + "\t" + str(value) + "\n") #écriture dans le txt data
                fn.write(str(round((ptr + 300)*self.pasDeTemps/1000,)) + "\t" + str(value/blank) + "\n") #écriture dans le txt datan
                ptr += 1 #incrémente le pointeur
                curve.setPos(ptr, 0) #positionne l'origine du graphe
        label += 1 #incrémente le label
        curve.setData(datan) #mise à jour du graphe

    def capsule(self,value): #définit si ce qui est observé est une capsule ou non
        global datan, d, invabsorption, label, tabCaps, blank
        try: #si on arrive à récupérer une valeur du seuil de détection
            lineEdit = self.lineEditDetectionThreshold.displayText() #la récupère
            if lineEdit != self.oldLineEdit: #si le seuil a été changé
                if lineEdit == "": #si il n'y a pas de seuil
                    self.noFloatDetected = True #état : pas de seuil détecté
                else:
                    self.noFloatDetected = False #état : seuil détecté
            self.oldLineEdit = lineEdit #le nouveau devient l'ancien
            if not self.inCaps: #si on est pas déjà dans une capsule
                if datan[-1] < float(self.lineEditDetectionThreshold.displayText()) and label > 3: #si on entre dans une capsule 
                    self.inCaps = True #état : on est dans une capsule
                    d = -1 #pour aller chercher la taille de la capsule
                    invabsorption = value/blank #pour définir l'absorption
            if self.inCaps: #si on est déjà dans une capsule
                d -= 1 #on décale le début de 1 à gauche
                if invabsorption > value/blank: #si l'absorption est plus grande
                    invabsorption = value/blank #nouvelle valeur pour l'inverse de l'absorption
                if datan[-1] > float(self.lineEditDetectionThreshold.displayText()): #si on sort d'une capsule
                    self.inCaps = False #état : on est pas dans une capsule
                    absorption = 1 - invabsorption #calcul de l'absorption
                    while (1-datan[d])/absorption<0.5: #pour trouver la position du début de la capsule
                        d+=1
                    f = d
                    while (1-datan[f])/absorption>=0.5: #pour trouver la position de la fin de la capsule
                        f+=1
                    taille = abs(f-d) #calcul de la taille
                    if taille > float(self.lineEditLength.displayText()): #si la taille de la capsule est assez grande
                        self.lcdNumberCapsuleCounter.display(self.lcdNumberCapsuleCounter.value()+1) #on incrémente le compteur de 1
                        tabCaps.append(capsule.Capsule(taille, label-taille, absorption)) #on ajoute la capsule au tableau de capsules
                        self.labelConsole.setText(tabCaps[-1].afficher()) #affiche les données de la capsule dans la mini console
        except ValueError: #si on ne détecte pas de seuil
            if self.noFloatDetected: #si on n'était pas déjà dans ce cas précedemment
                print("no float in Detection Threshold")
                self.noFloatDetected = False

    def pauseAcquisition(self): #gère les pauses d'acquisition 
        if self.blankDone: #si la référence est faite
            if not (self.withlVid or self.withrVid): #si on peut mettre pause
                if not self.pause: #si la pause n'est pas active
                    self.timer.stop() #mise en pause du timer
                    self.pause = True #la pause est active
                else: #si la pause est active
                    self.timer.start() #remise en route du timer
                    self.pause = False  #la pause n'est plus active
        else: #si la référence n'est pas faite
            self.makeBlankFirst() #faire la référence d'abord

    def stopAcquisition(self): #se produit en stoppant l'acquisition
        if self.blankDone: #si la référence est faite
            if self.start == True: #si une acquisition est en cours
                if self.withrVid:
                    #pour l'option Record :
                    global cam #récupère la variable semi-locale cam
                    #Arrête et ferme la  caméra
                    cam.stop_recording()
                    cam.close()
                    self.actionRecord_video_with_detection.setCheckable(True) #option à nouveau modifiable
                    self.actionRecord_video_with_detection.setChecked(True) #option cochée
                if self.withlVid:
                    #pour l'option Live + record :
                    self.thread3.stop() #arrête la preview (voir thread_detect_with_vid.py)
                    self.actionLive_and_record_video_with_detection.setCheckable(True) #option à nouveau modifiable
                    self.actionLive_and_record_video_with_detection.setChecked(True) #option cochée
                self.saveStats() #sauvegarde les stats
                self.timer.stop() #arrête le timer
                #fermeture des fichiers
                f.close()
                fn.close()
                os.chdir("/home/pi/Desktop/Résultats Capsula") #retour dans le dossier de travail
            #réinitialisation des états
            self.withrVid = False
            self.withlVid = False
            self.start = False
            self.stop = True
            mot.stopM()
        else: #si la référence n'est pas faite
            self.makeBlankFirst() #faire la référence d'abord

    def continuousDisplay(self): #mode d'affichage continu
        self.segmented = False

    def segmentedDisplay(self): #mode d'affichage segmenté
        global ptr, k, n
        n = ptr+300
        self.graphicsViewRealPlot.setXRange(n,n+300) #mise à l'echelle X
        n +=300
        k = 0
        self.segmented = True

#Onglet Calibration
        
#Général

    def openDetectionConfiguration(self):
        file = QFileDialog.getOpenFileName()
        file = str(file)[2:-19]
        fodc = open(file, "r")
        detection_threshold = fodc.readline()
        length_threshold = fodc.readline()
        ratio_capsule = fodc.readline()
        sampling_period = fodc.readline()
        self.lineEditDetectionThreshold.setText(detection_threshold)
        self.lineEditLength.setText(length_threshold)
        self.lineEditMinimumSize.setText(ratio_capsule)
        self.lineEditSamplingPeriod.setText(sampling_period)
        fodc.close()
        os.chdir("/home/pi/Desktop/Résultats Capsula")

    def openPumpConfiguration(self):
        file = QFileDialog.getOpenFileName()
        file = str(file)[2:-19]
        fopc = open(file, "r")
        dutycycle = int(fopc.readline())
        self.horizontalSliderDutyCycleP.setValue(dutycycle)
        fopc.close()
        os.chdir("/home/pi/Desktop/Résultats Capsula")

    def openMotorConfiguration(self):
        file = QFileDialog.getOpenFileName()
        file = str(file)[2:-19]
        fomc = open(file, "r")
        dutycycle = int(fomc.readline())
        self.horizontalSliderDutyCycleM.setValue(dutycycle)
        fomc.close()
        os.chdir("/home/pi/Desktop/Résultats Capsula")

    def saveDetectionConfiguration(self):
        file = QFileDialog.getSaveFileName()
        if (str(file)[-23:-19] == ".txt"):
            fsdc = open(str(file)[2:-19], "w")
        else:
            fsdc = open(str(file)[2:-19] + ".txt", "w")
        detection_threshold = self.lineEditDetectionThreshold.text()
        length_threshold = self.lineEditLength.text()
        ratio_capsule = self.lineEditMinimumSize.text()
        sampling_period = self.lineEditSamplingPeriod.text()
        fsdc.write(detection_threshold + "\n")
        fsdc.write(length_threshold + "\n")
        fsdc.write(ratio_capsule + "\n")
        fsdc.write(sampling_period)
        fsdc.close()
        os.chdir("/home/pi/Desktop/Résultats Capsula")

    def savePumpConfiguration(self):
        file = QFileDialog.getSaveFileName()
        if (str(file)[-23:-19] == ".txt"):
            fspc = open(str(file)[2:-19], "w")
        else:
            fspc = open(str(file)[2:-19] + ".txt", "w")
        dutycycle = str(self.horizontalSliderDutyCycleP.value())
        fspc.write(dutycycle)
        fspc.close()
        os.chdir("/home/pi/Desktop/Résultats Capsula")

    def saveMotorConfiguration(self):
        file = QFileDialog.getSaveFileName()
        if (str(file)[-23:-19] == ".txt"):
            fsmc = open(str(file)[2:-19], "w")
        else:
            fsmc = open(str(file)[2:-19] + ".txt", "w")
        dutycycle = str(self.horizontalSliderDutyCycleM.value())
        fsmc.write(dutycycle)
        fsmc.close()
        os.chdir("/home/pi/Desktop/Résultats Capsula")
        
    def saveStats(self): #sauve des statistiques de l'acquisition
        global mini, maxi, fs #récupération de variables semi-locales
        #Ecriture dans le fichier stats et fermeture de celui ci
        fs.write("Nombres de capsules comptées :\t" + str(int(self.lcdNumberCapsuleCounter.value())) + "\n")
        fs.write("Signal maximal mesuré :\t" + str(round(maxi,2)) + "V\n")
        fs.write("Signal minimal mesuré :\t" + str(round(mini,2)) + "V\n")
        fs.write("Pas de temps :\t" + str(self.pasDeTemps))
        fs.close()

    def closeEvent(self, event): #Quitte proprement la GUI
        self.timer.stop() #arrête le timer
        #réinitialise les GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW)
        GPIO.cleanup()
        self.close() #ferme la fenêtre
