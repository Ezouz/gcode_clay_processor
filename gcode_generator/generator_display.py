import matplotlib.pyplot as plt
from .settings import initialize_values, palette, fig, x, y, z, e, x_coords, y_coords, z_coords, extrude, diametre_buse, coefficient_extrusion, Xmax, Ymax, diametre_cercle, espacement_lignes, hauteur_first_Z, hauteur_de_couche, rayon, variance_enable, variance_z_max,variance_starting_layer, variance_actual_z, variance_transition_layer, nb_de_vaguelette, nb_couches_fond, hauteur_vase, nb_etoile, taille_petale, centre_x, centre_y

def update_diametre(diametre):
    diametre_cercle = diametre

def update_plot(x, y, z):
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect([1, 1, 1])  # Adjust the aspect ratio of the plot (x, y, z)
    fig.tight_layout()
    plt.axis('off')
    ax.plot(x, y, z, c=palette[0], linestyle='dashed', linewidth=0.2, markersize=0.5, dash_joinstyle='miter') #'miter', 'round', 'bevel'}
    
    # Set plot labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Gcode Path')
    plt.show()
