""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr
Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""

# Bibliothèques nécessaires
import io
import time
import os
import sys
import picamera
import pygame
import pygame.camera
import datetime
from moteur import *

from PIL import Image

     
def startCamera(expTime): #démarre la caméra et sa preview
    #initialise pygame et ecran
    pygame.init()
    
    screen = pygame.display.set_mode((640,480),0)

    #initialisation de la caméra
    camera = picamera.PiCamera() #création de l'objet caméra
    camera.resolution = (1280,720) #paramétrage de la résolution
    camera.crop = (0.0, 0.0, 1.0, 1.0)
    camera.framerate = float(24) #paramétrage des FPS
    camera.shutter_speed = expTime #paramétrage du temps d'exposition
    x = (screen.get_width() - camera.resolution[0]) / 2
    y = (screen.get_height() - camera.resolution[1]) / 2

    # Init buffer
    rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
    #camera.start_preview(fullscreen=False, window = (0, 0, width, height))#démarre la preview
    global pad, target, already #création de variables semi-locales
    target = Image.open('/home/pi/Desktop/Capsula/Icon/target.png') #ouverture de l'image "target"
    already = False #état : cible non affichée
    pad = Image.new('RGBA', (((target.size[0] + 31) // 32) * 32,((target.size[1] + 15) // 16) * 16,))
    pad.paste(target, (0, 0))
    #ajout des raccourcis sous forme de texte sur la vidéo
    #camera.annotate_text_size = 25
    #camera.annotate_foreground = picamera.Color('white')
    #camera.annotate_text = "P : capture image\nV : Start recording video (v again to stop)\nC: Enable/Disable target\nBackspace : Exit"
    
    
    running = True #état : caméra active
    while running: #tant que la caméra est active
        stream = io.BytesIO()
        camera.capture(stream, use_video_port=True, format='rgb')
        stream.seek(0)
        stream.readinto(rgb)
        stream.close()
        img = pygame.image.frombuffer(rgb[0:
            (camera.resolution[0] * camera.resolution[1] * 3)],
            camera.resolution, 'RGB')

        screen.fill(0)
        if img:
            screen.blit(img, (x,y))

        pygame.display.update()


        for event in pygame.event.get(): #si il se produit une action sur le clavier
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: #si la touche p est enfoncée
                    take_pic(camera)
                elif event.key == pygame.K_v: #si la touche v est enfoncée
                    take_video(camera)
                elif event.key == pygame.K_c: #si la touche c est enfoncée
                    print_target(camera)
                elif event.key == pygame.K_BACKSPACE: #si la touche retour est enfoncée
                    running = False #état : caméra inactive
                    quit_app(camera)
                    #quit_app(camera) #quitte la preview et la caméra
                elif event.key == pygame.K_UP: #if  up key is pressed
                    startM()    #start motor
                elif event.key == pygame.K_DOWN: #if down key is pressed
                    stopM()
                elif event.key == pygame.K_SPACE: #if space key is pressed
                    changeDirectionM()
                elif event.key == pygame.K_TAB: #if tab key is pressed
                    stepM()
                elif event.key == pygame.K_LSHIFT: #if left shift is pressed
                    stepmM()
    camera.close()
    pygame.display.quit()



def take_pic(camera): #prendre une photo en preview
    Ymd = datetime.datetime.now().strftime("%Y-%m-%d") #récupération de la date
    Ymdhms = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") #récupération de l'heure
    #vérification et/ou création du dossier "Photos"
    os.makedirs("Photos", exist_ok=True)
    os.chdir("Photos")
    os.makedirs(Ymd, exist_ok=True)
    os.chdir(Ymd)
    camera.capture(Ymdhms + '.jpg') #prise de la photo
    os.chmod('.', 0o777) #changement des droits : tout le monde peut écrire dans le dossier et y supprimer des éléments
    #retour au dossier de travail
    os.chdir("..")
    os.chdir("..") 
 
def take_video(camera): #prendre une vidéo en preview
    Ymd = datetime.datetime.now().strftime("%Y-%m-%d") #récupération de la date
    Ymdhms = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") #récupération de l'heure
    #vérification et/ou création du dossier "Videos"
    os.makedirs("Videos", exist_ok=True)
    os.chdir("Videos")
    os.makedirs(Ymd, exist_ok=True)
    os.chdir(Ymd)
    camera.start_recording(Ymdhms + '.tiff') #début de l'enregistrement vidéo
    continuer = True #état : en cours d'enregistrement
    while continuer: #tant que l'enregistrement est en cours
        for event in pygame.event.get(): #si il se produit une action sur le clavier
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v: #si la touche v est enfoncée
                    continuer = False #état : enregistrement stoppé
    camera.stop_recording() #fin de l'enregistrement vidéo
    os.chmod('.', 0o777) #changement des droits : tout le monde peut écrire dans le dossier et y supprimer des éléments
    #retour au dossier de travail
    os.chdir("..")
    os.chdir("..")

def print_target(camera): #permet d'afficher la cible
    global already, pad, target, o
    if not already: #si la cible n'est pas affichée
        #affichage d'une surcouche avec la cible sur fond transparent
        o = camera.add_overlay(pad.tobytes(), size=target.size)
        o.alpha = 255
        o.layer = 3
        already = True #état : cible affichée
    else: #si la cible est affichée
        camera.remove_overlay(o) #la surcouche est enlevée
        already = False #état : cible non affichée
    
def quit_app(camera): #quitte proprement la caméra
    camera.annotate_text = "" #réinitialise le texte affiché
    Ymd = datetime.datetime.now().strftime("%Y-%m-%d") #récupération de la date
    #vérification et/ou création du dossier "Photos"
    os.makedirs("Photos", exist_ok=True)
    os.chdir("Photos")
    os.makedirs(Ymd, exist_ok=True)
    os.chdir(Ymd)
    camera.capture('last_image_saved.jpg', resize=(299,168)) #prise d'un cliché pour l'interface graphique
    os.chmod('.', 0o777) #changement des droits : tout le monde peut écrire dans le dossier et y supprimer des éléments
    #retour au dossier de travail
    os.chdir("..")
    os.chdir("..")
    #quitte et ferme la caméra
    camera.close()
    pygame.display.quit()
