# from src.menu import menu_principal
# from gcode_utils import gcode_class
import pygame
import math
from pygame.locals import *
import sys

def visualize(object):
    print(f"Le fichier gcode sélectionné est : {object.name}\n")
    print("\n")
    print(object.describeModifications())
    object.show()

   # Paramètres d'affichage
    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 600
    BG_COLOR = (255, 255, 255)
    LINE_COLOR = (0, 0, 0)
    LINE_WIDTH = 1

    # Paramètres de rotation
    ROTATION_SPEED = 0.01  # Vitesse de rotation en radians par frame

    # Charger le fichier G-code
    def load_gcode(file_path):
        lines = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines

    # Parser les coordonnées X, Y et Z à partir d'une ligne de G-code
    def parse_coordinates(line):
        x = None
        y = None
        z = None
        parts = line.split()
        for part in parts:
            if part.startswith('X'):
                x = float(part[1:])
            elif part.startswith('Y'):
                y = float(part[1:])
            elif part.startswith('Z'):
                z = float(part[1:])
        return x, y, z

    # Initialiser Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Affichage G-code en 3/4 avec rotation en Pygame')

    # Charger le fichier G-code
    gcode_file_path = "Ressources/" + object.name  # Mettez ici le chemin vers votre fichier G-code
    gcode_lines = load_gcode(gcode_file_path)

    # Récupérer les coordonnées min et max du modèle
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    for line in gcode_lines:
        if line.startswith('G1'):
            x, y, z = parse_coordinates(line)
            if x is not None and y is not None and z is not None:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    # Calculer la taille du modèle
    model_width = max_x - min_x
    model_height = max_y - min_y

    # Centrer le modèle au milieu de l'écran
    offset_x = (SCREEN_WIDTH - model_width) / 2
    offset_y = (SCREEN_HEIGHT - model_height) / 2

    # Rotation initiale
    rotation_angle = 0

    # Boucle principale de jeu
    while True:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Effacer l'écran
        screen.fill(BG_COLOR)

        # Dessiner les lignes du G-code
        prev_x = None
        prev_y = None
        for line in gcode_lines:
            if line.startswith('G1'):
                x, y, z = parse_coordinates(line)
                if x is not None and y is not None and z is not None:
                    # Appliquer la rotation
                    x_rot = x * math.cos(rotation_angle) - y * math.sin(rotation_angle)
                    y_rot = x * math.sin(rotation_angle) + y * math.cos(rotation_angle)
                    z_rot = z

                    # Projection en 3/4 avec axe Z vers le haut
                    x_proj = offset_x + x_rot
                    y_proj = offset_y + y_rot + z_rot * 0.5
                    if prev_x is not None and prev_y is not None:
                        pygame.draw.line(screen, LINE_COLOR, (x_proj, y_proj), (prev_x, prev_y), LINE_WIDTH)

                    prev_x = x_proj
                    prev_y = y_proj

        # Mettre à jour l'angle de rotation
        rotation_angle += ROTATION_SPEED

        # Mettre à jour l'affichage
        pygame.display.flip()
        
if __name__=="__main__":
	main()
        