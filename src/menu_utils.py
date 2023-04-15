import os

def continue_or_restart(object):
    if (len(object.modifications) > 0):
        answer = input("Voulez-vous poursuivre la modification du fichier ou recommencer (r) ?")
        if answer is "r":
            object.modifications = []
            object.modified_gcode_lines = object.gcode_lines
            return object
        else:
            print("Continuing modifications\n")
    return object

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
