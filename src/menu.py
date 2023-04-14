import gcode_utils
from tabulate import tabulate 
from src.directories import scan_repertoire
from src.menu_utils import clear_console, quitter

def menu_modif(gcode_file_selected):
    # Boucle principale du menu
    while True:
        # clear_console()
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
            # clear_console()
            gcode_file_selected=scan_repertoire()
        elif choix == "2":
            # clear_console()
            gcode_utils.modify_gcode_speed(gcode_file_selected)
            input("")
        elif choix == "3":
            # clear_console()
            gcode_utils.clean_gcode_marlin2(gcode_file_selected)
            input("")
        elif choix == "4":
            # clear_console()
            gcode_utils.scale_gcode(gcode_file_selected)
            input("")
        elif choix == "5":
            # clear_console()
            gcode_utils.taille_buse(gcode_file_selected)
            input("")
        elif choix == "6":
            menu_principal()
        elif choix == "7":
            return gcode_file_selected# quitter()
            # quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")
    

def menu_principal(gcode_file_selected):
    # Boucle principale du menu
    while True:
        # clear_console()
        print("\nMenu Principal:\n")
        print(tabulate([["1", "Modifier un fichier Gcode"],
                    ["2", "Généré un fichier Gcode"],
                    ["3", "Quitter"]],
                    headers=['Option', 'Description'], tablefmt='plain'))  # Utilisation de tabulate pour afficher le menu

      
        choix = input("\nVeuillez entrer le numéro de votre choix : ")

        if choix == "1":
            gcode_file_selected=scan_repertoire()
            menu_modif(gcode_file_selected)
        elif choix == "2":
            gcode_utils.generate_circle_gcode()
        elif choix == "3":
            return # quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")
        return gcode_file_selected
