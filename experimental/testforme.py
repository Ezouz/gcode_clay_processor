"""
ranger des rectangles de differentes tailles dans un plus grand rectangle

"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rectpack import newPacker
import itertools

# Dimensions du rectangle
width = 15
height = 35

# Génération des formes
class Shape:
    def __init__(self, dimensions, occurrences, color):
        self.dimensions = dimensions
        self.occurrences = occurrences
        self.color = color


shapes = [
    Shape((2.153, 4.813), 8, 'red'),     # Cercle
    Shape((3.3333, 1), 8, 'yellow'),      # Triangle
    Shape((10.34, 1.65), 6, 'pink'),      # Autre
    Shape((1.1, 1.24), 12, 'green'),        # Carré
    Shape((2.57, 4.33),8, 'blue')         # Carré
]

repeated_shapes = []
colors = []

for shape in shapes:
    repeated_shapes.extend([shape.dimensions] * shape.occurrences)
    colors.extend([shape.color] * shape.occurrences)


# Création du packer
packer = newPacker(rotation=True)

# Ajout des formes répétées au packer
for i, shape in enumerate(repeated_shapes):
    packer.add_rect(*shape, rid=i)

# Calcul de l'emboîtement
packer.add_bin(width, height)
packer.pack()

# Récupération des formes emboîtées
packed_rects = packer[0]

# Offset entre les formes
offset = 0.1

# Calcul de l'échelle
scale = max(width, height)

# Création du rectangle brut
raw_rectangle = Rectangle((0, 0), width, height, facecolor='none', edgecolor='black', linewidth=3)

# Affichage des formes emboîtées
fig, ax = plt.subplots(figsize=(width, height))
ax.add_patch(raw_rectangle)

for rect in packed_rects:
    shape = repeated_shapes[rect.rid]  # Récupère la forme correspondante à partir de l'indice rid
    color = colors[rect.rid]  # Récupère la couleur correspondante à partir du dictionnaire
    x, y, w, h = rect.x + offset, rect.y + offset, rect.width - 2 * offset, rect.height - 2 * offset
    rectangle = Rectangle((x, y), w, h, facecolor=color, edgecolor='black')
    ax.add_patch(rectangle)

ax.set_xlim(0, scale)
ax.set_ylim(0, scale)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Formes complexes emboîtées')
ax.set_aspect('equal')  # Échelle égale sur les axes x et y
ax.grid(True)
plt.show()