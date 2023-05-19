import math
from .settings import initialize_values, fig, x, y, z, e, x_coords, y_coords, z_coords, extrude, diametre_buse, coefficient_extrusion, Xmax, Ymax, diametre_cercle, espacement_lignes, hauteur_first_Z, hauteur_de_couche, rayon, variance_enable, variance_z_max,variance_starting_layer, variance_actual_z, variance_transition_layer, nb_de_vaguelette, nb_couches_fond, hauteur_vase, nb_etoile, taille_petale, centre_x, centre_y
# from .settings import *

## generator_utils ##
# Écriture du fichier Gcode
# def export_gcode_file():
#     with open("gcode_extrusion_cercle.gcode", "w") as f:
#         f.write(gcode)
#     print("Fichier Gcode généré avec succès !")
#     input("")

# Ajout de la commande d'homming etc.
def create_base():
    gcode = ""
    gcode += "G28\n"
    gcode += "G1 Z5 F5000 ; lift nozzle\n"
    gcode += "M73 P0 ;printing progress 0%\n"
    gcode += "G1 Z{:.2f} F7800\n".format(hauteur_first_Z)
    gcode += "G1 E-2 F2400\n"
    gcode += "M103 ; extruder off\n"
    gcode += "G1 F7800\n"
    gcode += ";END OF HOMING\n"
    gcode += ";\n"
    gcode += ";START OF GCODE\n"
    return gcode

def create_EOF():
    # Fin de la génération du fichier Gcode
    gcode += "G91 ; use relative positioning for the XYZ axes\n" 
    gcode += "G1 Z10 F4000 ; move 10mm to the right of the current location\n"
    gcode += "G90;\n" # position absolue
    gcode += "M106 S0 ; turn off cooling fan\n" 
    gcode += "M104 S0 ; turn off extruder\n" 
    gcode += "M140 S0 ; turn off bed\n" 
    gcode += "G92 E0 ; set the current filament position to E=0\n" 
    gcode += "G1 E-8 F800 ; retract 10mm of filament\n" 
    gcode += "M84 ; disable motors\n"
    return gcode

# Fonction pour calculer les coordonnées X, Y d'un point sur le cercle
def coordonnees_cercle(angle, variance=0):
    x = centre_x + (rayon + variance) * math.cos(math.radians(angle))
    y = centre_y + (rayon + variance) * math.sin(math.radians(angle))
    return x, y

def distance_point(x1, y1, z1, x2, y2, z2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance
