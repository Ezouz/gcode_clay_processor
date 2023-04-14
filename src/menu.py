import gcode_utils
from tabulate import tabulate 
from src.directories import scan_repertoire
from src.menu_utils import clear_console, quitter

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
                    ["6", "Retour"],
                    ["7", "Quitter"]],
                    headers=['Option', 'Description'], tablefmt='plain'))  # Utilisation de tabulate pour afficher le menu

      
        choix = input("\nVeuillez entrer le numéro de votre choix : ")

        if choix == "1":
            gcode_file_selected=scan_repertoire()
        elif choix == "2":
            gcode_utils.modify_gcode_speed(gcode_file_selected)
        elif choix == "3":
            gcode_utils.clean_gcode_marlin2(gcode_file_selected)
        elif choix == "4":
            gcode_utils.scale_gcode(gcode_file_selected)
        elif choix == "5":
            gcode_utils.taille_buse(gcode_file_selected)
        elif choix == "6":
            menu_principal()
        elif choix == "7":
            quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")

def menu_principal():
    

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
        # elif choix == "2":
        #     generate_circle_gcode()
        elif choix == "3":
            quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")    
