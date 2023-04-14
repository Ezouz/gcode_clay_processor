import os
from src.menu_utils import clear_console

# Fonction pour scanner le répertoire et récupérer les fichiers *.gcode
def scan_repertoire():
    clear_console()
    print("Liste des fichiers Gcode :\n")
    j=0
    gcode_files = []  # Liste pour stocker les fichiers *.gcode
    for i, filename in enumerate(os.listdir('Ressources')):  # Parcours des fichiers dans le répertoire du script
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
