import gcode_utils
from tabulate import tabulate 
import settings
from src.directories import scan_repertoire
from src.menu_utils import continue_or_restart, clear_console, quitter
from gcode_utils import gcode_class

def menu_modif():
    # Boucle principale du menu
    while True:
        # clear_console()
        print(f"Le fichier gcode sélectionné est : {settings.gcode_file_selected.name}")
        print("\nMenu:\n")
        print(tabulate([
                            ["1", "Scanner le répertoire pour trouver les fichiers *.gcode"],
                            ["2", "Réduction de vitesse selon la hauteur"],
                            ["3", "Nettoyage des instructions m102|m103|m486"],
                            ["4", "Redimensioner un fichier Gcode"],
                            ["5", "Changer de taille de Buse"],
                            ["6", "Retour"],
                            ["7", "Quitter"],
                            ([], ["8", "Export modified file"])[len(settings.gcode_file_selected.modifications) > 0]
                        ],
                        headers=['Option', 'Description'], 
                        tablefmt='plain')
            )

      
        choix = input("\nVeuillez entrer le numéro de votre choix : ")

        if choix == "1":
            # clear_console()
            file_selected=scan_repertoire()
            settings.gcode_file_selected = gcode_class.Gcode(file_selected)
        elif choix == "2":
            # clear_console()
            settings.gcode_file_selected = gcode_utils.modify_gcode_speed(continue_or_restart(settings.gcode_file_selected))
            print("\n")
            print(settings.gcode_file_selected.describeModifications())
            input("")
        elif choix == "3":
            # clear_console()
            settings.gcode_file_selected = gcode_utils.clean_gcode_marlin2(continue_or_restart(settings.gcode_file_selected))
            print("\n")
            print(settings.gcode_file_selected.describeModifications())
            input("")
        elif choix == "4":
            # clear_console()
            settings.gcode_file_selected = gcode_utils.scale_gcode(continue_or_restart(settings.gcode_file_selected))
            print("\n")
            print(settings.gcode_file_selected.describeModifications())
            input("")
        elif choix == "5":
            # clear_console()
            settings.gcode_file_selected = gcode_utils.taille_buse(continue_or_restart(settings.gcode_file_selected))
            print("\n")
            print(settings.gcode_file_selected.describeModifications())
            input("")
        elif choix == "6":
            menu_principal(settings.gcode_file_selected)
        elif choix == "7":
            quitter()
        elif choix == "8":
            settings.gcode_file_selected.export()
        else:
            print("Choix invalide. Veuillez réessayer.")
    

def menu_principal():
    # Boucle principale du menu
    while True:
        # clear_console()
        print("\nMenu Principal:\n")
        print(tabulate([
                            ["1", "Modifier un fichier Gcode"],
                            ["2", "Généré un fichier Gcode"],
                            ["3", "Quitter"]
                        ],
                        headers=['Option', 'Description'], 
                        tablefmt='plain')
            )
         
        choix = input("\nVeuillez entrer le numéro de votre choix : ")
        if choix == "1":
            file_selected=scan_repertoire()
            settings.gcode_file_selected = gcode_class.Gcode(file_selected)
            menu_modif()
        elif choix == "2":
            gcode_utils.generate_circle_gcode()
        elif choix == "3":
            quitter()
        else:
            print("Choix invalide. Veuillez réessayer.")
