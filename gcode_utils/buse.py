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