import re
from gcode_utils import Modification

# clean useless "m102", "m103" et "m486" (for marlin 2)
def clean_gcode_marlin2(object):
    print(f"Le fichier gcode sélectionné est : {object.name}\n")
    print("Nettoyage des instructions m102|m103|m486 :\n")

    new_lines = object.modified_gcode_lines

    # Initialiser le compteur de lignes supprimées
    lignes_supprimees = 0

    # Créer une liste pour stocker les dernières lignes supprimées
    dernieres_lignes_supprimees = []
    lignes_conserved = []
    # Parcourir toutes les lignes du fichier
    for ligne in new_lines:
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
    
    # Afficher le compte rendu du nombre de lignes supprimées
    print(f"Nombre de lignes supprimées : {lignes_supprimees}")
    if lignes_supprimees > 0:
        # Afficher un aperçu des dernières lignes supprimées
        print("Dernières lignes supprimées :")
        for ligne_supprimee in dernieres_lignes_supprimees:
            print(ligne_supprimee.rstrip())

    params = []
    modif = Modification("instructions cleaning m102|m103|m486", params)
    object.modifications.append(modif)
    object.modified_gcode_lines = lignes_conserved

    return object