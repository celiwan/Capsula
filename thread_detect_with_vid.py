""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr
Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""

# Bibliothèques nécessaires
import serial
from PyQt5.QtWidgets import *
from threading import Thread
import io, os, sys, picamera, pygame, datetime
from PIL import Image

#Thread : Permet l'affichage la vidéo en preview sans interrompre le programme principal
class PreviewCam(Thread):

    def __init__(self, expTime): #initialisation du thread
        Thread.__init__(self)
        #initialise pygame et ecran
        pygame.init()
        screen = pygame.display.set_mode((640,480),0)
        # Initialisation de la caméra
        self.camera = picamera.PiCamera() #création de l'objet caméra
        self.camera.resolution = (1280, 720) #paramétrage de la résolution
        self.camera.framerate = float(24) #paramétrage des FPS
        self.camera.shutter_speed = expTime #paramétrage du temps d'exposition
        x = (screen.get_width() - self.camera.resolution[0]) / 2
        y = (screen.get_height() - self.camera.resolution[1]) / 2

        # Init buffer
        rgb = bytearray(self.camera.resolution[0] * self.camera.resolution[1] * 3)
        global pad, target, already #création de variables semi-locales
        target = Image.open('/home/pi/Desktop/Capsula/Icon/target.png') #ouverture de l'image "target"
        already = False #état : cible non affichée
        pad = Image.new('RGBA', (((target.size[0] + 31) // 32) * 32,((target.size[1] + 15) // 16) * 16,))
        pad.paste(target, (0, 0))

    def run(self): #s'execute lors de thread.start() : démarre la preview
        #récupération du jour et de l'heure de l'acquisiton
        Ymd = datetime.datetime.now().strftime("%Y-%m-%d")
        YmdHMS = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        #vérification et/ou création du dossier de l'acquisition
        os.makedirs("Datas", exist_ok=True)
        os.chdir("Datas")
        os.makedirs(Ymd, exist_ok=True)
        os.chdir(Ymd)
        self.camera.start_recording("vdata" + YmdHMS + '.h264') #création du fichier
        os.chdir("/home/pi/Desktop/Résultats Capsula") #retour au dossier de travail
        running = True #état : caméra active
        while running: #tant que la caméra est active
            stream = io.BytesIO()
            self.camera.capture(stream, use_video_port=True, format='rgb')
            stream.seek(0)
            stream.readinto(rgb)
            stream.close()
            img = pygame.image.frombuffer(rgb[0:
                (self.camera.resolution[0] * self.camera.resolution[1] * 3)],
                self.camera.resolution, 'RGB')

            screen.fill(0)
            if img:
                screen.blit(img, (x,y))

            pygame.display.update()


            for event in pygame.event.get(): #si il se produit une action sur le clavier
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p: #si la touche p est enfoncée
                        take_pic(self.camera)
                    elif event.key == pygame.K_v: #si la touche v est enfoncée
                        take_video(self.camera)
                    elif event.key == pygame.K_c: #si la touche c est enfoncée
                        print_target(self.camera)
                    elif event.key == pygame.K_BACKSPACE: #si la touche retour est enfoncée
                        running = False #état : caméra inactive
                        stop(self)
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
    


        
    def stop(self): #quitte proprement la caméra
        self.camera.close()
        pygame.display.quit()
