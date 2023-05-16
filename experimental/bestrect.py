"""
trouver la meilleure rotation possible pour etre contenu dans un rectangle

"""

import numpy as np
import matplotlib.pyplot as plt

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
gcode_file = '4.nc'


points = []
with open(gcode_file, 'r') as file:
    for line in file:
        if 'X' in line or 'Y' in line:
            tokens = line.split()
            x_index = None
            y_index = None
            for i, token in enumerate(tokens):
                if token.startswith('X'):
                    x_index = i
                elif token.startswith('Y'):
                    y_index = i
            if x_index is not None and y_index is not None:
                x = float(tokens[x_index][1:])
                y = float(tokens[y_index][1:])
                points.append([x, y])

# Conversion en tableau numpy
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

for angle in range(0, 181, 1):
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

