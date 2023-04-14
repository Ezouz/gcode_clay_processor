import re
import os
from tabulate import tabulate  # Importation de la bibliothèque tabulate


def taille_buse(nom_fichier_gcode):
    # Demande à l'utilisateur les valeurs de diamètre de base et nouveau diamètre en mm
    diametre_base = float(input("Veuillez entrer le diamètre de base de la buse en mm : "))
    diametre_nouveau = float(input("Veuillez entrer le nouveau diamètre de la buse en mm : "))

    # Calcule le pourcentage de réduction d'extrusion
    pourcentage_reduction = ( diametre_nouveau/diametre_base) * 100

    # Ouvre le fichier Gcode en lecture
    with open(nom_fichier_gcode, 'r') as fichier:
        lignes = fichier.readlines()

    # Parcours chaque ligne du fichier Gcode et modifie les valeurs d'extrusion (E)
    for i in range(len(lignes)):
        if lignes[i].startswith('G1'):
            valeurs = lignes[i].split(' ')
            for j in range(len(valeurs)):
                if valeurs[j].startswith('E'):
                    extrusion = float(valeurs[j][1:])
                    extrusion *= (pourcentage_reduction / 100)  # Applique le pourcentage de réduction d'extrusion
                    lignes[i] = lignes[i].replace('E{}'.format(float(valeurs[j][1:])), 'E{}'.format(float(extrusion)))
                    
           

    # Crée le nom du nouveau fichier Gcode avec le suffixe "dm_"
    nom_fichier_nouveau_gcode = "tb_" + nom_fichier_gcode

    # Écrit le contenu modifié dans le nouveau fichier Gcode
    with open(nom_fichier_nouveau_gcode, 'w') as fichier:
        for ligne in lignes:
            fichier.write(ligne)

    # Affiche le pourcentage de réduction d'extrusion
    print("Pourcentage de réduction d'extrusion : {:.2f}%".format(pourcentage_reduction))
    input("")

def scale_gcode(nom_fichier_gcode):
    clear_console()
    print(f"Le fichier gcode sélectionné est : {nom_fichier_gcode}\n")
    print("Redimensioner un fichier Gcode :\n")
    # Demande à l'utilisateur la valeur de hauteur maximale en Z ou le pourcentage de réduction
    hauteur_max = input("Veuillez entrer la hauteur maximale en Z en mm ou le pourcentage de réduction (ex: 10 ou 25%): ")

    # Lit le contenu du fichier Gcode
    with open(nom_fichier_gcode, 'r') as fichier:
        lignes = fichier.readlines()


    # Vérifie si l'utilisateur a entré un pourcentage ou une hauteur maximale
    if '%' in hauteur_max:
        # Si c'est un pourcentage, extrait la valeur numérique et convertit en float
        pourcentage = float(hauteur_max.strip('%'))
        hauteur_max_mm = None
    else:
        hauteur_max_mm = float(hauteur_max)
        # Obtenir la hauteur maximum d'impression (Z) et les changements de hauteur
        max_height = get_max_z(lignes)
        pourcentage = hauteur_max_mm / max_height * 100
        

    reduction = float(pourcentage / 100)
                
    # Parcourt toutes les lignes du fichier Gcode
    for i in range(len(lignes)):
        ligne = lignes[i].strip()
        if ligne.startswith('G1'):
            # Récupère les valeurs X, Y, Z, E de la ligne Gcode
            valeurs = ligne.split(' ')
            x = None
            y = None
            z = None
            e = None
            f = None
            for valeur in valeurs:
                if valeur.startswith('X'):
                    x = float(valeur[1:])
                elif valeur.startswith('Y'):
                    y = float(valeur[1:])
                elif valeur.startswith('Z'):
                    z = float(valeur[1:])
                elif valeur.startswith('E'):
                    e = float(valeur[1:])
                elif valeur.startswith('F'):
                    f = float(valeur[1:])
            
            # Applique la réduction en fonction de la hauteur maximale ou du pourcentage
            if pourcentage is not None:
                if z is not None:
                    z = (z * reduction)
                if x is not None:
                    x = (x * reduction)
                if y is not None:
                    y = (y * reduction)
                if e is not None:
                    e = (e * reduction)
               
                    
            # Met à jour la ligne Gcode avec les nouvelles valeurs
            nouvelle_ligne = 'G1'
            if x is not None:
                nouvelle_ligne += ' X{:.2f}'.format(x)
            if y is not None:
                nouvelle_ligne += ' Y{:.2f}'.format(y)
            if z is not None:
                nouvelle_ligne += ' Z{:.2f}'.format(z)
            if e is not None:
                nouvelle_ligne += ' E{:.2f}'.format(e)
            if f is not None:
                nouvelle_ligne += ' F{:.2f}'.format(f)
            # Remplace la ligne originale par la nouvelle ligne
            lignes[i] = nouvelle_ligne + '\n'

    # Obtient les dimensions maximales en X, Y et Z
    x_max = None
    y_max = None
    z_max = None
    for ligne in lignes:
        if ligne.startswith('G1'):
            valeurs = ligne.split(' ')
            for valeur in valeurs:
                if valeur.startswith('X'):
                    x = float(valeur[1:])
                    if x_max is None or x > x_max:
                        x_max = x
                elif valeur.startswith('Y'):
                    y = float(valeur[1:])
                    if y_max is None or y > y_max:
                        y_max = y
                elif valeur.startswith('Z'):
                    z = float(valeur[1:])
                    if z_max is None or z > z_max:
                        z_max = z

    # Affiche les dimensions maximales en X, Y et Z
    print("Dimensions maximales :")
    print("X : {:.2f} mm".format(x_max))
    print("Y : {:.2f} mm".format(y_max))
    print("Z : {:.2f} mm".format(z_max))

    # Crée le nom du nouveau fichier Gcode avec le suffixe "dm_"
    nom_fichier_nouveau_gcode = "dm_" + nom_fichier_gcode

    # Écrit le contenu modifié dans le nouveau fichier Gcode
    with open(nom_fichier_nouveau_gcode, 'w') as fichier:
        for ligne in lignes:
            fichier.write(ligne)
    input("")



# Fonction pour scanner le répertoire et récupérer les fichiers *.gcode
def scan_repertoire():
    clear_console()
    print("Liste des fichiers Gcode :\n")
    j=0
    gcode_files = []  # Liste pour stocker les fichiers *.gcode
    for i, filename in enumerate(os.listdir()):  # Parcours des fichiers dans le répertoire du script
        if filename.endswith('.gcode'):  # Vérification de l'extension du fichier
            gcode_files.append(filename)  # Ajout du fichier à la liste
            print(f"{j+1}. {filename}")  # Affichage du numéro et du nom du fichier
            j+=1
     # Demande à l'utilisateur de sélectionner un fichier
     
    while True:
        try:
            choix = int(input("\nVeuillez entrer le numéro du fichier gcode souhaité : "))
            if choix < 1 or choix > len(gcode_files):
                print("Numéro invalide. Veuillez réessayer.")
            else:
                break
        except ValueError:
            print("Numéro invalide. Veuillez réessayer.")

    # Récupération du nom du fichier sélectionné dans une variable
    gcode_file = gcode_files[choix - 1]
    
    return gcode_file

def clean_gcode_marlin2(nom_fichier):
    clear_console()
    print(f"Le fichier gcode sélectionné est : {nom_fichier}\n")
    print("Nettoyage des instructions m102|m103|m486 :\n")
    with open(nom_fichier, "r") as fichier:
        # Lire toutes les lignes du fichier dans une liste
        lignes = fichier.readlines()

        # Initialiser le compteur de lignes supprimées
        lignes_supprimees = 0

        # Créer une liste pour stocker les dernières lignes supprimées
        dernieres_lignes_supprimees = []
        lignes_conserved = []
        # Parcourir toutes les lignes du fichier
        for ligne in lignes:
            # Utiliser une expression régulière pour chercher les motifs "m102", "m103" et "m486" (sans respecter la case)
            if re.search(r"(?i)m102|m103|m486", ligne):
                # Incrémenter le compteur de lignes supprimées
                lignes_supprimees += 1

                # Ajouter la ligne à la liste des dernières lignes supprimées
                dernieres_lignes_supprimees.append(ligne)

                # Remplacer la ligne par une chaîne vide pour la supprimer
                ligne = ""
            else:
                lignes_conserved.append(ligne)
            # Afficher la ligne
            #print(ligne.rstrip())
        
        # Afficher le compte rendu du nombre de lignes supprimées
        print(f"Nombre de lignes supprimées : {lignes_supprimees}")
        if lignes_supprimees>0:
            # Afficher un aperçu des dernières lignes supprimées
            print("Dernières lignes supprimées :")
            for ligne_supprimee in dernieres_lignes_supprimees:
                print(ligne_supprimee.rstrip())

            # Demander confirmation à l'utilisateur pour exporter le résultat dans un nouveau fichier
            confirmation = input("Voulez-vous exporter le résultat dans un nouveau fichier ? : ")

            # Si l'utilisateur confirme, écrire le résultat dans un nouveau fichier
            if confirmation.lower() == "":
                # Créer un nom de fichier pour le nouveau fichier gcode avec le préfixe "cl_"
                nouveau_nom_fichier = "cl_" + nom_fichier

                # Ouvrir le nouveau fichier en mode écriture
                with open(nouveau_nom_fichier, "w") as nouveau_fichier:
                    # Écrire les lignes restantes dans le nouveau fichier
                    for ligne in lignes_conserved:
                        nouveau_fichier.write(ligne)
                print(f"Le fichier '{nouveau_nom_fichier}' a été créé avec succès.")
                input("")
            else:
                print("Le fichier n'a pas été exporté.")
        input("")

def get_max_z(lines):
    # Obtenir la hauteur maximum d'impression (Z) et les changements de hauteur
    max_height = 0.0
  
    for line in lines:
        if 'Z' in line:
            height_match = re.search(r'Z(\d+\.\d+)', line)
            if height_match:
                height = float(height_match.group(1))
                #print(height)
                if height > max_height:
                    max_height = height
    return max_height
               
    
    

def modify_gcode_speed(gcode_file):
    clear_console()
    print(f"Le fichier gcode sélectionné est : {gcode_file}\n")
    print("Réduction de vitesse selon la hauteur :\n")
    # Ouvrir le fichier GCode en lecture
    with open(gcode_file, 'r') as file:
        lines = file.readlines()

    # Obtenir la hauteur maximum d'impression (Z) et les changements de hauteur
    max_height = get_max_z(lines)

    # Demander à l'utilisateur le pourcentage de réduction de vitesse
    reduction_percentage = float(input("Veuillez entrer le pourcentage de réduction de vitesse : "))
    if reduction_percentage < 0 or reduction_percentage > 100:
        print("Pourcentage de réduction de vitesse invalide. Utilisation de la valeur par défaut (50%).")
        reduction_percentage = 50
        
    # Demander à l'utilisateur la hauteur de départ de réduction de vitesse
    height_reduction_speed = float(input("Veuillez entrer la hauteur de départ de réduction de vitesse : "))
    if height_reduction_speed < 0 or height_reduction_speed > max_height:
        print("Hauteur de départ de réduction de vitesse invalide. Utilisation de la valeur par défaut (10mm).")
        height_reduction_speed = 10
    # Modifier la vitesse d'impression en fonction de la hauteur d'impression
    new_lines = []
    for line in lines:
        if 'Z' in line:
            height_match = re.search(r'Z(\d+\.\d+)', line)
            if height_match:
                height = float(height_match.group(1))
        if 'F' in line:
            speed_match = re.search(r'F(\d+)', line)
            if speed_match:
                speed = float(speed_match.group(1))
 
                if height > height_reduction_speed:
                    new_speed = speed - (1-((max_height - height ) / (max_height-height_reduction_speed))) * speed*(100-reduction_percentage) /100
                else:
                    new_speed = speed
                line = line.replace('F{}'.format(int(speed)), 'F{}'.format(int(new_speed)))
            new_lines.append(line)
        else:
            new_lines.append(line)

    # Enregistrer les nouvelles lignes dans un nouveau fichier GCode
    new_file_name = 'va_' + gcode_file
    with open(new_file_name, 'w') as new_file:
        new_file.writelines(new_lines)

    print("Le fichier GCode a été modifié et enregistré sous le nom : ", new_file_name)
    input("")



# Fonction pour quitter le script
def quitter():
    print("Merci d'avoir utilisé le script. Au revoir!")
    exit()


def clear_console():
    # Effacer la console sur Windows
    if os.name == 'nt':  # Vérifier si le système d'exploitation est Windows
        os.system('cls')  # Exécuter la commande système "cls" pour effacer la console

    # Effacer la console sur MacOS et Linux
    else:
        os.system('clear')  # Exécuter la commande système "clear" pour effacer la console

def menu_modif():
        # Boucle principale du menu
    while True:
        clear_console()
        print(f"Le fichier gcode sélectionné est : {gcode_file_selected}")
        print("\nMenu:\n")
        print(tabulate([["1", "Scanner le répertoire pour trouver les fichiers *.gcode"],
                    ["2", "Réduction de vitesse selon la hauteur"],
                    ["3", "Nettoyage des instructions m102|m103|m486"],
                    ["4", "Redimensioner un fichier Gcode"],
                    ["5", "Changer de taille de Buse"],
                    ["6", "Quitter"]],
                    headers=['Option', 'Description'], tablefmt='plain'))  # Utilisation de tabulate pour afficher le menu

      
        choix = input("\nVeuillez entrer le numéro de votre choix : ")

        if choix == "1":
            gcode_file_selected=scan_repertoire()
        elif choix == "2":
            modify_gcode_speed(gcode_file_selected)
        elif choix == "3":
            clean_gcode_marlin2(gcode_file_selected)
        elif choix == "4":
            scale_gcode(gcode_file_selected)
        elif choix == "5":
            taille_buse(gcode_file_selected)
        elif choix == "6":
            quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")

def menu_principal():
    gcode_file_selected=scan_repertoire()
    # Appel de la fonction pour scanner le répertoire

    # Boucle principale du menu
    while True:
        clear_console()
        print("\nMenu Principal:\n")
        print(tabulate([["1", "Modifier un fichier Gcode"],
                    ["2", "Généré un fichier Gcode"],
                    ["3", "Quitter"]],
                    headers=['Option', 'Description'], tablefmt='plain'))  # Utilisation de tabulate pour afficher le menu

      
        choix = input("\nVeuillez entrer le numéro de votre choix : ")

        if choix == "1":
            gcode_file_selected=scan_repertoire()
            menu_modif()
        elif choix == "2":
            modify_gcode_speed(gcode_file_selected)
        elif choix == "3":
            quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")    

def main():
    menu_principal()
    
  

def generate_gcode_custom():
    return
    
    

if __name__=="__main__":
	main()