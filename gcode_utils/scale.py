from gcode_utils.utils import get_max_z

def scale_gcode(nom_fichier_gcode):
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
    nom_fichier_nouveau_gcode = "dm_" + nom_fichier_gcode[11:]

    # Écrit le contenu modifié dans le nouveau fichier Gcode
    with open('../Generated_files/' + nom_fichier_nouveau_gcode, 'w') as fichier:
        for ligne in lignes:
            fichier.write(ligne)
