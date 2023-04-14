import re
from gcode_utils.utils import get_max_z

def modify_gcode_speed(gcode_file):
    # clear_console()
    print(f"Le fichier gcode sélectionné est : {gcode_file}\n")
    print("Réduction de vitesse selon la hauteur :\n")
    # Ouvrir le fichier GCode en lecture
    with open(gcode_file, 'r') as file:
        lines = file.readlines()

    # Obtenir la hauteur maximum d'impression (Z) et les changements de hauteur
    max_height = get_max_z(lines)

    # Demander à l'utilisateur le pourcentage de réduction de vitesse
    reduction_percentage = float(input("Veuillez entrer le pourcentage de réduction de vitesse : "))
    if reduction_percentage < 0 or reduction_percentage > 100:
        print("Pourcentage de réduction de vitesse invalide. Utilisation de la valeur par défaut (50%).")
        reduction_percentage = 50
        
    # Demander à l'utilisateur la hauteur de départ de réduction de vitesse
    height_reduction_speed = float(input("Veuillez entrer la hauteur de départ de réduction de vitesse : "))
    if height_reduction_speed < 0 or height_reduction_speed > max_height:
        print("Hauteur de départ de réduction de vitesse invalide. Utilisation de la valeur par défaut (10mm).")
        height_reduction_speed = 10
    # Modifier la vitesse d'impression en fonction de la hauteur d'impression
    new_lines = []
    for line in lines:
        if 'Z' in line:
            height_match = re.search(r'Z(\d+\.\d+)', line)
            if height_match:
                height = float(height_match.group(1))
        if 'F' in line:
            speed_match = re.search(r'F(\d+)', line)
            if speed_match:
                speed = float(speed_match.group(1))
 
                if height > height_reduction_speed:
                    new_speed = speed - (1-((max_height - height ) / (max_height-height_reduction_speed))) * speed*(100-reduction_percentage) /100
                else:
                    new_speed = speed
                line = line.replace('F{}'.format(int(speed)), 'F{}'.format(int(new_speed)))
            new_lines.append(line)
        else:
            new_lines.append(line)

    # Enregistrer les nouvelles lignes dans un nouveau fichier GCode
    new_file_name = 'va_' + gcode_file
    with open(new_file_name, 'w') as new_file:
        new_file.writelines(new_lines)

    print("Le fichier GCode a été modifié et enregistré sous le nom : ", new_file_name)
    input("")