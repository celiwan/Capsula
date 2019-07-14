""" Code écrit par :
Eric MORET
eric.moret@institutoptique.fr
Mai/Aout 2018
Si vous avez la moindre question, n'hésitez pas à me contacter"""

class Capsule:

    def __init__(self,taille, label,absorption): #initialisation de la classe
        self.taille = taille #initialisation de sa taille
        self.label = label #initialisation de son ID
        self.absorption = absorption #initialisation de son absorption

    def afficher(self): #affiche ses caractéristiques
        return ("Capsule #" + str(self.label) + ":\n" + "Taille : " + str(self.taille) + "\nAbsorption : " + str(self.absorption))
        
    def afficher2(self):
        return (str(self.label) + "\t" + str(self.taille) + "\t" + str(self.absorption))
