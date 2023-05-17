"""
ok
ranger des boites de differentes tailles sur une surface si plus de place décaller à droite une nouvelle surface

"""


import matplotlib.pyplot as plt
from rectpack import newPacker
import random

# Collecte des informations
surface_width = 10
surface_height = 10
boxes = [(2.12, 4.157), (5.8, 3.453), (1.12, 3.8111),(6.333333,2.3333333),(3.21111,2.28888)]
box_counts = [14, 3, 16,25,10]

# Placement des boîtes
packer = newPacker(rotation=True) # Autoriser la rotation des boîtes
for i in range(len(boxes)):
    for _ in range(box_counts[i]):
        packer.add_rect(*boxes[i])
packer.add_bin(surface_width, surface_height)

total_boxes = sum(box_counts)
packed_boxes = 0
while packed_boxes < total_boxes:
    # Ajout d'une nouvelle surface si toutes les boîtes n'ont pas été placées
    packer.pack()
    packed_boxes = sum([len(abin) for abin in packer])
    if packed_boxes < total_boxes:
        packer.add_bin(surface_width, surface_height)

# Génération de couleurs uniques pour chaque boîte
colors = []
for _ in range(total_boxes):
    colors.append((random.random(), random.random(), random.random()))

# Affichage de la solution
surface_x_offset = 0
color_index = 0
for abin in packer:
    # Ajout d'un contour à la surface
    plt.gca().add_patch(plt.Rectangle((surface_x_offset, 0), surface_width, surface_height, fill=False))
    for rect in abin.rect_list():
        x, y, w, h, rid = rect
        plt.gca().add_patch(plt.Rectangle((x + surface_x_offset , y ), w, h, facecolor=colors[color_index]))
        color_index += 1
    surface_x_offset += surface_width + 1
plt.xlim(0, surface_x_offset)
plt.ylim(0, surface_height)
plt.show()