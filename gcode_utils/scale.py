from gcode_utils import Modification

def scale_gcode(object):
    print(f"Le fichier gcode sélectionné est : {object.name}\n")
    print("Redimensioner un fichier Gcode :\n")
    # Demande à l'utilisateur la valeur de hauteur maximale en Z ou le pourcentage de réduction
    hauteur_max = input("Veuillez entrer la hauteur maximale en Z en mm ou le pourcentage de réduction (ex: 10 ou 25%): ")

    # Vérifie si l'utilisateur a entré un pourcentage ou une hauteur maximale
    if '%' in hauteur_max:
        # Si c'est un pourcentage, extrait la valeur numérique et convertit en float
        pourcentage = float(hauteur_max.strip('%'))
        hauteur_max_mm = None
    else:
        hauteur_max_mm = float(hauteur_max)
        # Obtenir la hauteur maximum d'impression (Z) et les changements de hauteur
        pourcentage = hauteur_max_mm / object.max_height * 100

    reduction = float(pourcentage / 100)
    new_lines = object.modified_gcode_lines
                
    # Parcourt toutes les lignes du fichier Gcode
    for i in range(len(new_lines)):
        ligne = new_lines[i].strip()
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
            if pourcentage != None:
                if z != None:
                    z = (z * reduction)
                if x != None:
                    x = (x * reduction)
                if y != None:
                    y = (y * reduction)
                if e != None:
                    e = (e * reduction)
               
                    
            # Met à jour la ligne Gcode avec les nouvelles valeurs
            nouvelle_ligne = 'G1'
            if x != None:
                nouvelle_ligne += ' X{:.3f}'.format(x)
            if y != None:
                nouvelle_ligne += ' Y{:.3f}'.format(y)
            if z != None:
                nouvelle_ligne += ' Z{:.3f}'.format(z)
            if e != None:
                nouvelle_ligne += ' E{:.5f}'.format(e)
            if f != None:
                nouvelle_ligne += ' F{}'.format(f)
            # Remplace la ligne originale par la nouvelle ligne
            new_lines[i] = nouvelle_ligne + '\n'

    # Obtient les dimensions maximales en X, Y et Z
    x_max = None
    y_max = None
    z_max = None
    for ligne in object.modified_gcode_lines:
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

    params = []
    params.append({'key': 'maximale en Z en mm ou le pourcentage de réduction', 'value': hauteur_max})
    params.append({'key': 'pourcentage de réduction', 'value': pourcentage})
    params.append({'key': 'Dimensions maximales X', 'value': x_max})
    params.append({'key': 'Dimensions maximales Y', 'value': y_max})
    params.append({'key': 'Dimensions maximales Z', 'value': z_max})
    modif = Modification("proportional scaling of gcode", params)
    object.modifications.append(modif)
    object.modified_gcode_lines = new_lines
    return object