import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(100, 200))
palette = sns.color_palette("flare", 8)

# GLOBALS
x_coords = []
y_coords = []
z_coords = []

# Parameters
Xmax = 290
Ymax = 290
diametre_cercle = 100
espacement_lignes = 4
hauteur_first_Z = 1
hauteur_de_couche = 0.4
rayon = diametre_cercle / 2
nb_couches_fond = 16
hauteur_vase = 150
variance_enable = 1
variance_z_max = 6
variance_starting_layer = 24
variance_actual_z = 0
variance_transition_layer = 60
nb_de_vaguelette = 8
nb_etoile = 13
taille_petale = 0.3
centre_x = Xmax / 2
centre_y = Ymax / 2

# parametre extrusion
x = 0
y = 0
z = 0
e = 0
extrude = False
diametre_buse = 2
coefficient_extrusion = 0.008388 * 0.35

def initialize_values():
    global x_coords, y_coords, z_coords, Xmax, Ymax, diametre_cercle, espacement_lignes, hauteur_first_Z, hauteur_de_couche, rayon, nb_couches_fond, hauteur_vase, variance_enable, variance_z_max, variance_starting_layer, variance_actual_z, variance_transition_layer, nb_de_vaguelette, nb_etoile, taille_petale, centre_x, centre_y, x, y, z, e, extrude, diametre_buse, coefficient_extrusion

    x_coords = []
    y_coords = []
    z_coords = []

    # Assign values to variables
    Xmax = 290
    Ymax = 290
    diametre_cercle = 100
    espacement_lignes = 4
    hauteur_first_Z = 1
    hauteur_de_couche = 0.4
    rayon = diametre_cercle / 2
    nb_couches_fond = 16
    hauteur_vase = 150
    variance_enable = 1
    variance_z_max = 6
    variance_starting_layer = 24
    variance_actual_z = 0
    variance_transition_layer = 60
    nb_de_vaguelette = 8
    nb_etoile = 13
    taille_petale = 0.3
    centre_x = Xmax / 2
    centre_y = Ymax / 2

    # Reset other variables if needed
    x = 0
    y = 0
    z = 0
    e = 0
