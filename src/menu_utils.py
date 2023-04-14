import os

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
