from gcode_utils import modification_class

def taille_buse(object):
    print(f"Le fichier gcode sélectionné est : {object.name}\n")
    print("Paramètrer le diamètre de la buse :\n")
    # Demande à l'utilisateur les valeurs de diamètre de base et nouveau diamètre en mm
    diametre_base = float(input("Veuillez entrer le diamètre de base de la buse en mm : "))
    diametre_nouveau = float(input("Veuillez entrer le nouveau diamètre de la buse en mm : "))

    # Calcule le pourcentage de réduction d'extrusion
    pourcentage_reduction = ( diametre_nouveau/diametre_base) * 100

    new_lines = object.modified_gcode_lines

    # Parcours chaque ligne du fichier Gcode et modifie les valeurs d'extrusion (E)
    for i in range(len(new_lines)):
        if new_lines[i].startswith('G1'):
            valeurs = new_lines[i].split(' ')
            for j in range(len(valeurs)):
                if valeurs[j].startswith('E'):
                    extrusion = float(valeurs[j][1:])
                    extrusion *= (pourcentage_reduction / 100)  # Applique le pourcentage de réduction d'extrusion
                    new_lines[i] = new_lines[i].replace('E{}'.format(float(valeurs[j][1:])), 'E{:.5f}'.format(float(extrusion)))
                    
    
    params = []
    params.append({'key': 'Extrusion reduction percentage', 'value': pourcentage_reduction})
    params.append({'key': 'base diameter', 'value': diametre_base})
    params.append({'key': 'new diameter', 'value': diametre_nouveau})
    modif = modification_class.Modification("scale nozzle diameter proportionally", params)
    object.modifications.append(modif)
    object.modified_gcode_lines = new_lines
    return object