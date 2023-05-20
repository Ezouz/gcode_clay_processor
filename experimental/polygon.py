from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

# Lire les points à partir du fichier 1.point et les stocker dans une liste
points = []
with open("1.point", "r") as file:
    for line in file:
        x, y = map(float, line.strip().split(","))
        points.append((x, y))

# Créer un polygone à partir des points
polygon = Polygon(points)

# Vérifier les collisions
point_to_check = Point(50,15)  # Point à vérifier s'il se trouve dans le polygone
if polygon.contains(point_to_check):
    print("Le point se trouve à l'intérieur du polygone.")
else:
    print("Le point se trouve à l'extérieur du polygone.")
    
# Extraire les coordonnées x et y du polygone
x, y = polygon.exterior.xy

# Créer le graphique
fig, ax = plt.subplots()
ax.plot(x, y)

# Ajouter des options de style
ax.set_aspect('equal', adjustable='box')  # Réglez les proportions des axes
ax.grid(True)  # Afficher la grille
plt.show()