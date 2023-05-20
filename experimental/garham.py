import math
import matplotlib.pyplot as plt

def orientation(p, q, r):
    """
    Calcule l'orientation de trois points (p, q, r).
    Renvoie 0 si les points sont colinéaires, 1 si dans le sens des aiguilles d'une montre,
    et 2 si dans le sens inverse des aiguilles d'une montre.
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2

def distance(p, q):
    """
    Calcule la distance entre deux points (p et q).
    """
    return math.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)

def next_to_top(stack):
    """
    Renvoie l'avant-dernier élément de la pile.
    """
    return stack[-2]

def convex_hull(points):
    """
    Trouve l'enveloppe convexe d'un ensemble de points en utilisant l'algorithme du balayage de Graham.
    Renvoie une liste contenant les indices des points faisant partie de l'enveloppe convexe dans l'ordre
    antihoraire à partir du point le plus à gauche.
    """
    n = len(points)
    if n < 3:
        return []

    # Trouver le point le plus à gauche
    leftmost = min(points, key=lambda point: point[0])

    # Trier les points selon l'angle qu'ils forment avec le point le plus à gauche
    sorted_points = sorted(points, key=lambda point: math.atan2(point[1] - leftmost[1], point[0] - leftmost[0]))

    # Construire l'enveloppe convexe
    stack = [sorted_points[0], sorted_points[1]]

    for i in range(2, n):
        while len(stack) > 1 and orientation(next_to_top(stack), stack[-1], sorted_points[i]) != 2:
            stack.pop()
        stack.append(sorted_points[i])

    return [points.index(point) for point in stack]

# Exemple d'utilisation avec vos points

# Lecture des points à partir du fichier
points = []
with open("2.point", "r") as file:
    for line in file:
        x, y = map(float, line.strip().split(","))
        points.append((x, y))

# Recherche de l'enveloppe convexe
convex_hull_indices = convex_hull(points)

# Affichage des points de l'enveloppe convexe
convexpoints = []
for index in convex_hull_indices:
    convexpoints.append(points[index])

# Extraire les coordonnées x et y séparément
x_coords = [point[0] for point in convexpoints]
y_coords = [point[1] for point in convexpoints]

xa_coords = [point[0] for point in points]
ya_coords = [point[1] for point in points]

# Créer le tracé du contour
plt.plot(x_coords, y_coords)
plt.plot(xa_coords, ya_coords)

# Ajouter des étiquettes et un titre
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Contour du polygone')

# Afficher le graphique
plt.show()