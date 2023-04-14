import re

# clean useless "m102", "m103" et "m486" (for marlin 2)
def clean_gcode_marlin2(nom_fichier):
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
                nouveau_nom_fichier = "cl_" + nom_fichier[11:]

                # Ouvrir le nouveau fichier en mode écriture
                with open('../Generated_files/' + nouveau_nom_fichier, "w") as nouveau_fichier:
                    # Écrire les lignes restantes dans le nouveau fichier
                    for ligne in lignes_conserved:
                        nouveau_fichier.write(ligne)
                print(f"Le fichier '{nouveau_nom_fichier}' a été créé avec succès.")
            else:
                print("Le fichier n'a pas été exporté.")