"""
trouver la meilleure rotation possible pour etre contenu dans un rectangle

"""
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import math

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
gcode_file = '1.nc'


# points = []
# with open(gcode_file, 'r') as file:
#     for line in file:
#         if 'X' in line or 'Y' in line:
#             tokens = line.split()
#             x_index = None
#             y_index = None
#             for i, token in enumerate(tokens):
#                 if token.startswith('X'):
#                     x_index = i
#                 elif token.startswith('Y'):
#                     y_index = i
#             if x_index is not None and y_index is not None:
#                 x = float(tokens[x_index][1:])
#                 y = float(tokens[y_index][1:])
#                 if [x, y] not in points:
#                     points.append([x, y])



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
                print("G2")
                direction = -1
            else:
                print("G3")                
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
 
            print (start_angle)
            end_angle = math.atan2(y-(lasty+j) , x-(lastx+i) )
            print (end_angle )
            
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
                    points.append([px, py])
        else:
            if x is not None and y is not None:
                points.append([x, y])            
        
        lastx=x
        lasty=y
        if line.startswith('G2') or line.startswith('G3'):
            last_command = line[0:2]




# Conversion en tableau numpy
points = np.array(points)

# Supprimer les points identiques
# points = np.unique(points, axis=0)

# Supprimer les points proches


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

for angle in np.arange(0, 181, 0.1):
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

