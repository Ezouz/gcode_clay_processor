
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
import seaborn as sns

# **************************************
#         CLASS
# **************************************

class Box:
    def __init__(self, file,ox,oy, x, y, angle, count):
        self.file = str(file)
        self.x = float(x)                   #width
        self.y = float(y)                   #height
        self.ox = float(ox)                 #originX
        self.oy = float(oy)                 #originY
        self.angle =  float(angle)
        self.count = int(count)
        


# **************************************
#         ROTATION GCODE
# **************************************

recx=0.0
recy=0.0
lastx=0.0
lasty=0.0


# Fonction pour appliquer une rotation en 2D autour de l'axe Z
def rotate_2d(x, y, angle):
    angle_rad = math.radians(angle)
    ox=0
    oy=0
    new_x = ox + math.cos(angle_rad) * (x - ox) - math.sin(angle_rad) * (y - oy)
    new_y = oy + math.sin(angle_rad) * (x - ox) + math.cos(angle_rad) * (y - oy)
    return new_x, new_y

# Fonction pour parser une ligne et effectuer la rotation si nécessaire
def process_line(line,rotation_angle):
    global recx, recy, lastx, lasty
    
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





def rotateGcode(file_path,rotation_angle,ninety):

    # Ouvrir le fichier G-code en lecture et en écriture
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Ouvrir un nouveau fichier pour écrire les résultats
    
    new_file_path, _ = os.path.splitext(file_path)
    if(ninety):
        new_file_path = new_file_path + "_m.nc"
    else:
        new_file_path = new_file_path + "_m_r.nc"
        
    with open(new_file_path, 'w') as new_file:
        # Parcourir le fichier G-code ligne par ligne
        for line in lines:
            # Appliquer la rotation si nécessaire
            new_line = process_line(line,rotation_angle)
            
            # Écrire la ligne mise à jour dans le nouveau fichier
            new_file.write(new_line)


# **************************************
#         RANGER DES BOITES
# **************************************

def aranger(box,surface):
    
    # file_name= []
    # Placement des boîtes
    packer = newPacker(rotation=True) # Autoriser la rotation des boîtes
    for b in box:
        for _ in range(b.count):
            packer.add_rect(b.x, b.y,b.file)
            #file_name.append(b.file)
        packer.add_bin(surface[0],surface[1])

    total_boxes = sum([b.count for b in box])
    palette = sns.color_palette("flare",total_boxes)
    packed_boxes = 0
    while packed_boxes < total_boxes:
        # Ajout d'une nouvelle surface si toutes les boîtes n'ont pas été placées
        packer.pack()
        packed_boxes = sum([len(abin) for abin in packer])
        if packed_boxes < total_boxes:
            packer.add_bin(surface[0], surface[1])

    # Génération de couleurs uniques pour chaque boîte
    colors = []
    for _ in range(total_boxes):
        colors.append((random.random(), random.random(), random.random()))

    # Affichage de la solution
    surface_x_offset = 0
    color_index = 0
    for abin in packer:
        # Ajout d'un contour à la surface
        plt.gca().add_patch(plt.Rectangle((surface_x_offset, 0), surface[0], surface[1], fill=False))
        for rect in abin.rect_list():
            x, y, w, h, rid = rect
            #print(f"x: {x}, y: {y}, w: {w}, h: {h}, rid: {rid}")
            
            plt.gca().add_patch(plt.Rectangle((x + surface_x_offset , y ), w, h, facecolor=palette[color_index]))
            
            fichier_md5 = 'checksums.md5'
            md5_dict = {}
            if os.path.exists(fichier_md5):
                with open(fichier_md5, 'r') as f:
                    for ligne in f:
                        md5_hash, chemin, angle,ox,oy,oxr,oyr,sizex,sizey = ligne.strip().split('  ')
                        md5_dict[chemin] = (md5_hash, angle,ox,oy,oxr,oyr,sizex,sizey)
            angle,ox,oy,oxr,oyr,sizex,sizey = get_box_from_md5(rid, md5_dict)
            
            
            fichier_export, _ = os.path.splitext(rid)
            if(sizex==w):
                fichier_export = fichier_export + ".point"
            else:
                fichier_export = fichier_export + "_r.point"
            points_importes = importer_points(fichier_export)
            points_importes=translate_points(points_importes,-x - surface_x_offset,0,-y,0)
            points_importes = np.array(points_importes)  # Convertir la liste en un tableau NumPy
            plt.plot(points_importes[:, 0], points_importes[:, 1], color='black', label='Forme avec rotation')
            plt.plot([points_importes[-1, 0], points_importes[0, 0]], [points_importes[-1, 1], points_importes[0, 1]], color='green')  # Relier le dernier point au premier
                
            
            
            color_index += 1
        surface_x_offset += surface[0] + 1
    plt.xlim(0, surface[0])
    plt.ylim(0, surface[1])
    plt.axis('equal')
    plt.show()




# **************************************
#     TROUVE LE MEILLEUR ANGLE
# **************************************

def translate_points(points, min_x, max_x, min_y, max_y):
    """
    Effectue une translation sur les points pour ajuster la forme.

    Arguments:
    - points : Liste de points.
    - min_x, max_x, min_y, max_y : Bords de la forme après rotation.

    Retour :
    - translated_points : Liste de points après translation.
    """
    translated_points = []
    translation_x = -min_x
    translation_y = -min_y

    for point in points:
        translated_point = [point[0] + translation_x, point[1] + translation_y]
        translated_points.append(translated_point)

    return translated_points

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
    
    translated_points = translate_points(rotated_points, min_x, max_x, min_y, max_y)
    translated_points = np.array(translated_points)
    print("Angle de rotation appliquée:", best_angle, " avec un décallage de " , min_x, " et ", min_y, " pour le fichier", gcode_file)
    chemin_fichier, _ = os.path.splitext(gcode_file)
    chemin_export = chemin_fichier + ".point"
    exporter_points(chemin_export, translated_points)
    
    
    #rotation a 90 degres
    rotated_points = rotate_points(translated_points, 90)
    min_x_r, max_x_r, min_y_r, max_y_r = calculate_bounding_rectangle(rotated_points)
    best_rectangle_points = np.array([[min_x_r, min_y_r],
                                    [max_x_r, min_y_r],
                                    [max_x_r, max_y_r],
                                    [min_x_r, max_y_r],
                                    [min_x_r, min_y_r]])
    translated_points = translate_points(rotated_points, min_x_r, max_x_r, min_y_r, max_y_r)
    translated_points = np.array(translated_points)
    print("Ratation à 90 degrès appliquée: avec un décallage de " , min_x_r, " et ", min_y_r, " pour le fichier", gcode_file)
    print("---")
    chemin_fichier, _ = os.path.splitext(gcode_file)
    chemin_export = chemin_fichier + "_r.point"
    exporter_points(chemin_export, translated_points)
    
    # Affichage de la forme d'origine et de la forme avec la meilleure rotation
    visualize(points, translated_points, rectangle_points, best_rectangle_points)
    sizex = "{:.3f}".format(abs(max_x - min_x))
    sizey = "{:.3f}".format(abs(max_y - min_y))
    
    return(best_angle, min_x,min_y,min_x_r,min_y_r,sizex,sizey)


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
                md5_hash, chemin, angle,ox,oy,oxr,oyr,sizex,sizey = ligne.strip().split('  ')
                md5_dict[chemin] = (md5_hash, angle,ox,oy,oxr,oyr,sizex,sizey)

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
                        angle,ox,oy,oxr,oyr,sizex,sizey = bestangle(fichier)  
                        md5_dict[chemin] = (md5_hash, angle,ox,oy,oxr,oyr,sizex,sizey)

    # Enregistrer les nouvelles empreintes MD5 et angles dans le fichier de checksums
    with open(fichier_md5, 'w') as f:
        for chemin, (md5_hash, angle,ox,oy,oxr,oyr,sizex,sizey) in md5_dict.items():
            f.write(f"{md5_hash}  {chemin}  {angle}  {ox}  {oy}  {oxr}  {oyr}  {sizex}  {sizey}\n")

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

    # Création du tableau de la classe Box
    box_list = []
    boxes_files =[]
    boxes =[]
    box_counts=[]

    for file in selected_files:
        quantity = int(input(f"Entrez la quantité pour le fichier {file}: "))
        angle,ox,oy,oxr,oyr,sizex,sizey = get_box_from_md5(file, md5_dict)
        boxes_files.append(file)
        tmpB=ox,oy,sizex,sizey,angle
        boxes.append(tmpB)
        box_counts.append(quantity)
        

    raw_size_x_input = input("Entrez la taille du brut (axe X): ")
    raw_size_x = float(raw_size_x_input) if raw_size_x_input else 300

    raw_size_y_input = input("Entrez la taille du brut (axe Y): ")
    raw_size_y = float(raw_size_y_input) if raw_size_y_input else 300
    
    raw_size = (raw_size_x, raw_size_y)
    # margin = float(input("Entrez la marge entre les pièces: "))
    
    
    clear_terminal()
   

    # Parcours des données des boîtes et création des objets Box
    for i in range(len(boxes_files)):
        file = boxes_files[i]
        ox,oy,x, y,angle = boxes[i]
        count = box_counts[i]
        box = Box(file,ox,oy,x, y,angle, count)
        box_list.append(box)
        info = "File: "+ box.file +"  x: "+ str(box.x) +"  y: "+ str(box.y) +"  angle: "+ str(box.angle )+"  count: "+ str(box.count)
        print(info)
    
    print("Taille du brut (axe X):", raw_size_x)
    print("Taille du brut (axe Y):", raw_size_y)
        
    
    aranger(box_list,raw_size)




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

def get_box_from_md5(filename, md5_dict):
    for chemin, (md5_hash, angle,ox,oy,oxr,oyr,sizex,sizey) in md5_dict.items():
        if "./"+os.path.basename(chemin) == filename:
            return float(angle),float(ox),float(oy),float(oxr),float(oyr),float(sizex),float(sizey)
    return

def exporter_points(chemin_fichier, points):
    """
    Exporte les points dans un fichier texte.

    Arguments :
    - chemin_fichier : Chemin du fichier de sortie.
    - points : Liste de tuples (x, y) représentant les points.

    """
    with open(chemin_fichier, 'w') as fichier:
        for point in points:
            fichier.write(f"{point[0]},{point[1]}\n")

    print("Les points ont été exportés avec succès.")

def importer_points(chemin_fichier):
    """
    Importe les points à partir d'un fichier texte.

    Argument :
    - chemin_fichier : Chemin du fichier d'entrée.

    Retour :
    - points : Liste de tuples (x, y) représentant les points.
    """
    points = []
    with open(chemin_fichier, 'r') as fichier:
        for ligne in fichier:
            x, y = ligne.strip().split(',')
            points.append((float(x), float(y)))

    return points

if __name__ == "__main__":
    main()