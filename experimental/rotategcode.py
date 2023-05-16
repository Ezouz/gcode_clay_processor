"""
rotation d'un fichier gcode

"""

import math
import numpy as np
import re

recx=0.0
recy=0.0
lastx=0.0
lasty=0.0
rotation_angle = 90


# Fonction pour appliquer une rotation en 2D autour de l'axe Z
def rotate_2d(x, y, angle):
    angle_rad = math.radians(angle)
    ox=0
    oy=0
    new_x = ox + math.cos(angle_rad) * (x - ox) - math.sin(angle_rad) * (y - oy)
    new_y = oy + math.sin(angle_rad) * (x - ox) + math.cos(angle_rad) * (y - oy)
    return new_x, new_y

# Fonction pour parser une ligne et effectuer la rotation si nécessaire
def process_line(line):
    global recx, recy, rotation_angle, lastx, lasty
    
    if 'I' in line and 'J' in line:
        if 'X' in line:
            x_match = re.search(r'X([-]?[\d.]+)', line)
            if x_match:
                try:
                    recx = float(x_match.group(1))
                except ValueError:
                    print("Erreur de conversion en float pour la valeur de X")
                
        if 'Y' in line:
            y_match = re.search(r'Y([-]?[\d.]+)', line)
            if y_match:
                try:
                    recy = float(y_match.group(1))
                    
                except ValueError:
                    print("Erreur de conversion en float pour la valeur de Y")
        
        rotated_x, rotated_y = rotate_2d(recx, recy, rotation_angle)
        new_line = re.sub(r'X([-]?[\d.]+)', 'X'+str(rotated_x), line)
        new_line = re.sub(r'Y([-]?[\d.]+)', 'Y'+str(rotated_y), new_line)
        
        i_match = re.search(r'I([-]?[\d.]+)', line)
        j_match = re.search(r'J([-]?[\d.]+)', line)
        if i_match and j_match:
            i = float(i_match.group(1))
            j = float(j_match.group(1))
            rotated_i, rotated_j = rotate_2d(lastx + i, lasty + j, rotation_angle)
            lastrotated_x, lastrotated_y = rotate_2d(lastx, lasty, rotation_angle)
            print(str(rotated_i - lastrotated_x) + " :: " + str(rotated_x))
            new_line = re.sub(r'I([-]?[\d.]+)', 'I'+str(rotated_i - lastrotated_x), new_line)
            new_line = re.sub(r'J([-]?[\d.]+)', 'J'+str(rotated_j - lastrotated_y), new_line)
        
        lastx = recx
        lasty = recy
        return new_line
    elif 'X' in line or 'Y' in line :
        if 'X' in line:
            x_match = re.search(r'X([-]?[\d.]+)', line)
            if x_match:
                try:
                    recx = float(x_match.group(1))
                except ValueError:
                    print("Erreur de conversion en float pour la valeur de X :", x_match.group(1))
        
        
        if 'Y' in line:
            y_match = re.search(r'Y([-]?[\d.]+)', line)
            if y_match:
                try:
                    recy = float(y_match.group(1))
                except ValueError:
                    print("Erreur de conversion en float pour la valeur de X :", y_match.group(1))
        else:
            print(line)
        
        rotated_x, rotated_y = rotate_2d(recx, recy, rotation_angle)
        new_line = re.sub(r'X([-]?[\d.]+)', 'X'+str(rotated_x), line)
        new_line = re.sub(r'Y([-]?[\d.]+)', 'Y'+str(rotated_y), new_line)
        lastx = recx
        lasty = recy
        return new_line
    else:
        return line


# Chemin vers le fichier G-code d'origine
file_path = "1.nc"



# Ouvrir le fichier G-code en lecture et en écriture
with open(file_path, 'r') as file:
    lines = file.readlines()

# Ouvrir un nouveau fichier pour écrire les résultats
new_file_path = "4.nc"
with open(new_file_path, 'w') as new_file:
    # Parcourir le fichier G-code ligne par ligne
    for line in lines:
        # Appliquer la rotation si nécessaire
        new_line = process_line(line)
        
        # Écrire la ligne mise à jour dans le nouveau fichier
        new_file.write(new_line)