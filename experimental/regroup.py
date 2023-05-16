
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import math
import glob
import os
import hashlib
from rectpack import newPacker
import random

# **************************************
#         CLASS
# **************************************

class Box:
    def __init__(self, x, y, count):
        self.x = x
        self.y = y
        self.count = count


# **************************************
#         RANGER DES BOITES
# **************************************

def aranger(box,surface):
    # Collecte des informations
    surface=1.2,1.2
    # Placement des boîtes
    packer = newPacker(rotation=True) # Autoriser la rotation des boîtes
    for i in range(len(box)):
        for _ in range(box.count[i]):
            packer.add_rect(*box.x,box.y)
    packer.add_bin(surface)

    total_boxes = sum(box.count)
    packed_boxes = 0
    while packed_boxes < total_boxes:
        # Ajout d'une nouvelle surface si toutes les boîtes n'ont pas été placées
        packer.pack()
        packed_boxes = sum([len(abin) for abin in packer])
        if packed_boxes < total_boxes:
            packer.add_bin(surface)

    # Génération de couleurs uniques pour chaque boîte
    colors = []
    for _ in range(total_boxes):
        colors.append((random.random(), random.random(), random.random()))

    # Affichage de la solution
    surface_x_offset = 0
    color_index = 0
    for abin in packer:
        # Ajout d'un contour à la surface
        plt.gca().add_patch(plt.Rectangle((surface_x_offset, 0), surface, fill=False))
        for rect in abin.rect_list():
            x, y, w, h, rid = rect
            plt.gca().add_patch(plt.Rectangle((x + surface_x_offset , y ), w, h, facecolor=colors[color_index]))
            color_index += 1
        surface_x_offset += surface[0] + 1
    plt.xlim(0, surface[0])
    plt.ylim(0, surface[1])
    plt.show()




# **************************************
#     TROUVE LE MEILLEUR ANGLE
# **************************************

def rotate_points(points, angle):
    """Effectue une rotation de `angle` degrés sur les points donnés."""
    theta = np.radians(angle)
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                                [np.sin(theta), np.cos(theta)]])
    return np.dot(points, rotation_matrix)

def calculate_bounding_rectangle(points):
    """Calcule les coordonnées du rectangle englobant pour les points donnés."""
    min_x = np.min(points[:, 0])
    max_x = np.max(points[:, 0])
    min_y = np.min(points[:, 1])
    max_y = np.max(points[:, 1])
    return min_x, max_x, min_y, max_y

def visualize(points, rotated_points, rectangle_points, rotated_rectangle_points):
    """Visualise les points et les rectangles englobants."""
    plt.figure(figsize=(10, 5))
    
    # Affichage de la forme d'origine à gauche
    plt.subplot(1, 2, 1)
    plt.plot(points[:, 0], points[:, 1], color='blue', label='Forme d\'origine')
    plt.plot([points[-1, 0], points[0, 0]], [points[-1, 1], points[0, 1]], color='blue')  # Relier le dernier point au premier
    plt.axis('equal')
    plt.legend()
    plt.title('Forme d\'origine')

    # Affichage de la forme avec la meilleure rotation à droite
    plt.subplot(1, 2, 2)
    plt.plot(rotated_points[:, 0], rotated_points[:, 1], color='green', label='Forme avec rotation')
    plt.plot([rotated_points[-1, 0], rotated_points[0, 0]], [rotated_points[-1, 1], rotated_points[0, 1]], color='green')  # Relier le dernier point au premier
    plt.plot(rotated_rectangle_points[:, 0], rotated_rectangle_points[:, 1], color='red', label='Rectangle englobant')
    plt.axis('equal')
    plt.legend()
    plt.title('Forme avec meilleure rotation et rectangle englobant')

    plt.show()

# Lecture du fichier Gcode
def bestangle(gcode_file):

    points = []
    with open(gcode_file, 'r') as file:
        lastx = None
        lasty = None
        x = None
        y = None
        i = None
        j = None
        last_command = None
        for line in file:
            i = None
            j = None
            match = re.search(r'I([-]?[\d.]+).*J([-]?[\d.]+)', line)
            if match:
                if (last_command == 'G2'or line.startswith('G2')) and not line.startswith('G3'):                    
                    direction = -1
                else:                                  
                    direction = 1
                i = float(match.group(1))
                j = float(match.group(2))
            
            match = re.search(r'(X([-]?[\d.]+))?.*(Y([-]?[\d.]+))?', line)
            if match:
                for word in line.split():
                    if word.startswith('X'):
                        x = float(word[1:])
                    elif word.startswith('Y'):
                        y = float(word[1:])
                
            if i is not None and j is not None:
                radius = math.sqrt((i) ** 2 + (j) ** 2)
                start_angle = math.atan2(lasty-(lasty+j), lastx-(lastx+i) ) 
                end_angle = math.atan2(y-(lasty+j) , x-(lastx+i) )
                
                if direction == 1:
                    if end_angle <= start_angle:
                        end_angle += 2 * math.pi
                else:
                    if start_angle <= end_angle:
                        start_angle += 2 * math.pi
                angle_step = (end_angle - start_angle) / 3
                for angle in np.arange(start_angle, end_angle + angle_step, angle_step):
                    px = lastx+i + radius * math.cos(angle)
                    py = lasty+j + radius * math.sin(angle)
                    if px is not None and py is not None:
                        if [px, py] not in points:
                            points.append([px, py])    
            else:
                if x is not None and y is not None:
                    if [x, y] not in points:
                        points.append([x, y])        
            
            lastx=x
            lasty=y
            if line.startswith('G2') or line.startswith('G3'):
                last_command = line[0:2]

    points = np.array(points)

    # Calcul du rectangle initial
    min_x, max_x, min_y, max_y = calculate_bounding_rectangle(points)
    rectangle_points = np.array([[min_x, min_y],
                                [max_x, min_y],
                                [max_x, max_y],
                                [min_x, max_y],
                                [min_x, min_y]])

    # Recherche de la meilleure rotation
    best_angle = 0
    best_score = float('inf')

    for angle in np.arange(0, 181, .8):
        rotated_points = rotate_points(points, angle)
        min_x,    max_x, min_y, max_y = calculate_bounding_rectangle(rotated_points)
        score = (max_x - min_x) + (max_y - min_y)  # Score basé sur la taille du rectangle englobant
        
        if score < best_score:
            best_score = score
            best_angle = angle

    # Rotation finale avec le meilleur angle
    rotated_points = rotate_points(points, best_angle)
    min_x, max_x, min_y, max_y = calculate_bounding_rectangle(rotated_points)
    best_rectangle_points = np.array([[min_x, min_y],
                                    [max_x, min_y],
                                    [max_x, max_y],
                                    [min_x, max_y],
                                    [min_x, min_y]])

    # Affichage de l'angle de rotation
    print("Angle de rotation appliquée:", best_angle)
    
    # Affichage de la forme d'origine et de la forme avec la meilleure rotation
    visualize(points, rotated_points, rectangle_points, best_rectangle_points)
    sizex="{:.3f}".format(max_x-min_x)
    sizey="{:.3f}".format(max_y-min_y)
    
    return(best_angle, sizex,sizey)


# **************************************
#            MAIN FUNCTION
# **************************************

def main():
    
    clear_terminal()
    # Ask the user to select the G-code files
    
    fichier_md5 = 'checksums.md5'
    md5_dict = {}

    if os.path.exists(fichier_md5):
        with open(fichier_md5, 'r') as f:
            for ligne in f:
                md5_hash, chemin, angle,sizex,sizey = ligne.strip().split('  ')
                md5_dict[chemin] = (md5_hash, angle,sizex,sizey)

    repertoire = './'
    files_available = []  # Liste pour stocker les fichiers G-code disponibles avec leurs numéros

    for root, dirs, files in os.walk(repertoire):
        for fichier in files:
            if fichier.endswith('.nc'):
                chemin = os.path.join(root, fichier)
                files_available.append(chemin)  # Ajouter le chemin du fichier à la liste des fichiers disponibles
                with open(chemin, 'rb') as f:
                    contenu = f.read()
                    md5_hash = hashlib.md5(contenu).hexdigest()
                    
                    if chemin in md5_dict:
                        if md5_hash != md5_dict[chemin][0]:
                            print(f"Le fichier {chemin} a été modifié.")
                    else:
                        angle,sizex,sizey = bestangle(fichier)  # Remplacez `bestangle(fichier)` par le code approprié pour obtenir la valeur de `angle` pour chaque fichier
                        md5_dict[chemin] = (md5_hash, angle,sizex,sizey)

    # Enregistrer les nouvelles empreintes MD5 et angles dans le fichier de checksums
    with open(fichier_md5, 'w') as f:
        for chemin, (md5_hash, angle,sizex,sizey) in md5_dict.items():
            f.write(f"{md5_hash}  {chemin}  {angle}  {sizex}  {sizey}\n")

    # Afficher le contenu du fichier de checksums
    print("Contenu du fichier de checksums :")
    with open(fichier_md5, 'r') as f:
        print(f.read())
    
    # Afficher la liste des fichiers disponibles avec leurs numéros
    print("Fichiers disponibles :")
    for i, fichier in enumerate(files_available, start=1):
        print(f"{i}. {fichier}")

    # Demander à l'utilisateur de sélectionner les fichiers par numéro
    selected_files_input = input("Sélectionnez les numéros des fichiers G-code à combiner (séparés par des virgules): ")
    selected_files_indices = selected_files_input.split(",")

    selected_files = []  # Liste pour stocker les fichiers sélectionnés

    # Récupérer les noms des fichiers sélectionnés à partir des numéros
    for index in selected_files_indices:
        try:
            selected_files.append(files_available[int(index) - 1])  # Soustraire 1 car les indices commencent à 0
        except (ValueError, IndexError):
            print(f"Numéro de fichier invalide : {index}")

    print("Fichiers sélectionnés :")
    for fichier in selected_files:
        print(fichier)

   
    quantities = []
    for file in selected_files:
        quantity = int(input(f"Entrez la quantité pour le fichier {file}: "))
        quantities.append(quantity)

    raw_size_x = float(input("Entrez la taille du brut (axe X): "))
    raw_size_y = float(input("Entrez la taille du brut (axe Y): "))
    raw_size = (raw_size_x, raw_size_y)
    # margin = float(input("Entrez la marge entre les pièces: "))
    
    box = Box(x, y, count)
    
    aranger(box,raw_size)




    # pieces = []
    # for file in selected_files:
    #     with open(file, 'r') as f:
    #         gcode_lines = f.readlines()
    #     piece_size = calculate_piece_size(gcode_lines)
    #     pieces.append({"gcode": gcode_lines, "size": piece_size})

    # # Optimiser les positions des pièces
    # piece_sizes = [piece["size"] for piece in pieces]
    # positions = optimize_piece_positions(piece_sizes, quantities, raw_size, margin)

    # combined_gcode = []
    # for i, piece in enumerate(pieces):
    #     quantity = quantities[i]
    #     piece_gcode = piece["gcode"]
    #     piece_x, piece_y = piece["size"]

    #     for j in range(quantity):
    #         translated_gcode = translate_piece(piece_gcode, positions[j][0], positions[j][1])
    #         combined_gcode.extend(translated_gcode)

    # if combined_gcode:
    #     output_file = input("Entrez le nom du fichier G-code de sortie: ")
    #     with open(output_file, 'w') as file:
    #         file.write('\n'.join(combined_gcode))  # Write the combined G-code with line breaks
    #     print(f"Le fichier G-code combiné a été enregistré sous {output_file}.")
    # else:
    #     print("Toutes les pièces ne rentrent pas sur le brut. Des fichiers G-code optimisés ont été créés.")

# **************************************
#              OUTILS
# **************************************

def clear_terminal():
    # Vérifiez si le système d'exploitation est Windows ou Unix/Linux
    if os.name == 'nt':  # Pour Windows
        _ = os.system('cls')
    else:  # Pour Unix/Linux/Mac
        _ = os.system('clear')


if __name__ == "__main__":
    main()