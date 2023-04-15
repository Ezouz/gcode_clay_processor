import re
from gcode_utils import modification_class

def modify_gcode_speed(object):
    print(f"\nLe fichier gcode sélectionné est : {object.name}\n")
    print("Réduction de vitesse selon la hauteur :\n")
    # Demander à l'utilisateur le pourcentage de réduction de vitesse
    reduction_percentage = float(input("\nVeuillez entrer le pourcentage de réduction de vitesse : "))
    if reduction_percentage < 0 or reduction_percentage > 100:
        print("Pourcentage de réduction de vitesse invalide. Utilisation de la valeur par défaut (50%).")
        reduction_percentage = 50
    # Demander à l'utilisateur la hauteur de départ de réduction de vitesse
    height_reduction_speed = float(input("\nVeuillez entrer la hauteur de départ de réduction de vitesse : "))
    if height_reduction_speed < 0 or height_reduction_speed > object.max_height:
        print("Hauteur de départ de réduction de vitesse invalide. Utilisation de la valeur par défaut (10mm).")
        height_reduction_speed = 10

    # Modifier la vitesse d'impression en fonction de la hauteur d'impression
    new_lines = []

    height = 0
    for line in object.modified_gcode_lines:
        if 'Z' in line:
            height_match = re.search(r'Z(\d+\.\d+)', line)
            if height_match:
                height = float(height_match.group(1))
        if 'F' in line:
            speed_match = re.search(r'F(\d+)', line)
            if speed_match:
                speed = float(speed_match.group(1))
 
                if height > height_reduction_speed:
                    new_speed = speed - (1-((object.max_height - height ) / (object.max_height-height_reduction_speed))) * speed*(100-reduction_percentage) /100
                else:
                    new_speed = speed
                line = line.replace('F{}'.format(int(speed)), 'F{}'.format(int(new_speed)))
            new_lines.append(line)
        else:
            new_lines.append(line)


    params = []
    params.append({'key': 'reduction_percentage', 'value': reduction_percentage})
    params.append({'key': 'height_reduction_speed', 'value': height_reduction_speed})
    modif = modification_class.Modification("proportional speed reduction", params)
    object.modifications.append(modif)
    object.modified_gcode_lines = new_lines
    return object