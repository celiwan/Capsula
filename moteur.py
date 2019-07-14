""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr

Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""

# Bibliothèque nécessaire
import serial
ser = serial.Serial('/dev/ttyACM1', 9600)

#Moteur :
def changeDirectionM():
    ser.write(str(200).encode('utf-8')) #envoie un signal change direction à Arduino
    
def dutyCycleM(value):
    ser.write(str(value).encode('utf-8')) #envoie le duty cycle à Arduino
    
def runAndGoBackM(): 
    ser.write(str(300).encode('utf-8')) #envoie un signal aller/retour à Arduino

def startM():
    ser.write(str(400).encode('utf-8')) #envoie un signal start à Arduino        
    
def stopM():
    ser.write(str(500).encode('utf-8')) #envoie un signal stop à Arduino
    
def changeBrakeM(state):
    if state:
        ser.write(str(600).encode('utf-8')) #envoie un signal active frein à Arduino
    else:
        ser.write(str(601).encode('utf-8')) #envoie un signal désactive frein à Arduino
def stepM():
    ser.write(str(700).encode('utf-8')) #send a "step" signal to the arduino

def stepmM():
    ser.write(str(800).encode('utf-8')) #send a smaller "step" signal to the arduino
#Pump :
def changeDirectionP():
    ser.write(str(1200).encode('utf-8')) #envoie un signal change direction à Arduino
    
def dutyCycleP(value):
    ser.write(str(value+1000).encode('utf-8')) #envoie le duty cycle à Arduino
    
def runAndGoBackP(): 
    ser.write(str(1300).encode('utf-8')) #envoie un signal aller/retour à Arduino
    
def startP():
    ser.write(str(1400).encode('utf-8')) #envoie un signal start à Arduino        
    
def stopP():
    ser.write(str(1500).encode('utf-8')) #envoie un signal stop à Arduino
    
def changeBrakeP(state):
    if state:
        ser.write(str(1600).encode('utf-8')) #envoie un signal active frein à Arduino
    else:
        ser.write(str(1601).encode('utf-8')) #envoie un signal désactive frein à Arduino
