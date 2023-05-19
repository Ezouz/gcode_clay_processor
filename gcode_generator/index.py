import math
from ..gcode_utils.utils import const
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button
from .generator_utils import distance_point
from .generator_display import update_plot
import matplotlib.pyplot as plt
from .settings import initialize_values, fig, x, y, z, e, x_coords, y_coords, z_coords, extrude, diametre_buse, coefficient_extrusion, Xmax, Ymax, diametre_cercle, espacement_lignes, hauteur_first_Z, hauteur_de_couche, rayon, variance_enable, variance_z_max,variance_starting_layer, variance_actual_z, variance_transition_layer, nb_de_vaguelette, nb_couches_fond, hauteur_vase, nb_etoile, taille_petale, centre_x, centre_y

# convertisseur syntax gcode
def gcode_sender(tmp_x, tmp_y, tmp_z, extrusion):
    global x, y, z, e, extrude

    gcode = "G1 "
    if(tmp_x != x):
            gcode += "X{:.3f} ".format(tmp_x)
    if(tmp_y != y):
            gcode += "Y{:.3f} ".format(tmp_y)
    if(tmp_z != z):
            gcode += "Z{:.3f} ".format(tmp_z)
    if(extrusion and extrude):
        e+=distance_point(tmp_x,tmp_y,tmp_z,x,y,z) * math.pi * ((diametre_buse/2)**2) * coefficient_extrusion
        gcode += "E{:.5f} ".format(e)
    
    gcode += "\n" 
    x = tmp_x
    y = tmp_y
    z = tmp_z
    extrude=extrusion

    x_coords.append(float(tmp_x))
    y_coords.append(float(tmp_y))
    z_coords.append(float(tmp_z))

    if gcode == "G1 \n":
        return ""
    else :
        return gcode
    
def generate_circle_gcode():
    gcode = ""

    # Fonction pour calculer les coordonnées X, Y d'un point sur le cercle
    def coordonnees_cercle(angle,variance=0):
        x = centre_x + (rayon+variance) * math.cos(math.radians(angle))
        y = centre_y + (rayon+variance) * math.sin(math.radians(angle))
        return x, y

    inverser_sens = False
    actual_z_height = hauteur_first_Z
    couche=0
    angle_depart = 0

    while actual_z_height<hauteur_vase:
        # Calcul des coordonnées du point de départ sur le cercle
        if nb_couches_fond>couche:
            angle_depart += 180
            angle = angle_depart
            actual_z_height = hauteur_first_Z+hauteur_de_couche*couche
        else:
            angle_depart =0
            angle = angle_depart
    
        angle_max=angle+360
        coeff_reduction_variance_xy=(couche-variance_starting_layer)/variance_transition_layer
        coeff_reduction_variance_z=const((couche-variance_starting_layer)/variance_transition_layer,0,1)
        if nb_couches_fond<couche:
            actual_z_height += hauteur_de_couche/360*2
        variance_global=(variance_z_max*math.cos(math.radians(angle)*nb_etoile)*coeff_reduction_variance_xy)*taille_petale
        variance_actual_z=actual_z_height+variance_z_max*math.cos(math.radians(angle)*nb_de_vaguelette)*coeff_reduction_variance_z
        if variance_enable==1 and variance_starting_layer<couche:        
            x_depart, y_depart = coordonnees_cercle(angle,variance_global)
            gcode +=gcode_sender(x_depart,y_depart,variance_actual_z,False)
        else:
            x_depart, y_depart = coordonnees_cercle(angle)
            gcode +=gcode_sender(x_depart,y_depart,actual_z_height,False)
        gcode += "M101 ; extruder on\n"
        gcode += "G1 F1800\n"
        
        
        if nb_couches_fond>couche:
            gcode += "G1 Z{:.2f}\n".format( actual_z_height)
        
        if variance_enable==1 and variance_starting_layer<couche:
            coeff_reduction_variance_xy=(couche-variance_starting_layer)/variance_transition_layer
            coeff_reduction_variance_z=const((couche-variance_starting_layer)/variance_transition_layer,0,1)
            while angle < angle_max:
                if nb_couches_fond<couche:
                    actual_z_height += hauteur_de_couche/360*2
                
                variance_global=(variance_z_max*math.cos(math.radians(angle)*nb_etoile)*coeff_reduction_variance_xy)*taille_petale
                variance_actual_z=actual_z_height+variance_z_max*math.cos(math.radians(angle)*nb_de_vaguelette)*coeff_reduction_variance_z
                x, y = coordonnees_cercle(angle,variance_global)
                gcode += gcode_sender(x,y,variance_actual_z,True)
                angle += 2 # resolution plus fine

            # Retour au point de départ pour fermer le cercle
            if nb_couches_fond<couche:
                actual_z_height += hauteur_de_couche/360*2
            variance_global=(variance_z_max*math.cos(math.radians(angle)*nb_de_vaguelette)*coeff_reduction_variance_xy)*taille_petale
            variance_actual_z=actual_z_height+variance_z_max*math.cos(math.radians(angle)*nb_de_vaguelette)*coeff_reduction_variance_z
        
            x, y = coordonnees_cercle(angle,variance_global)
            gcode +=gcode_sender(x,y,variance_actual_z,True)

        else:
            while angle < angle_max:
                if nb_couches_fond<couche:
                    actual_z_height += hauteur_de_couche/360*5
                
                x, y = coordonnees_cercle(angle)
                gcode +=gcode_sender(x,y,actual_z_height,True)
                angle += 5 # Augmenter l'angle de 5 degrés à chaque itération pour déterminer les points du cercle
            # Retour au point de départ pour fermer le cercle
        
            gcode +=gcode_sender(x_depart,y_depart,actual_z_height,True)

        # Variable pour inverser la direction de déplacement
        inverser_direction = False
        if nb_couches_fond>couche:
            #retractation avant remplissage
            gcode += "M103 ; extruder off\n"

            # Calcul du nombre de passes nécessaires pour couvrir le diamètre du cercle
            nombre_passes = int((rayon-espacement_lignes)*2 / espacement_lignes)
            # Boucle pour générer les mouvements de remplissage rectilinéaire
            for passe in range(nombre_passes + 1):
                if inverser_sens:
                    # Calcul des coordonnées du point de départ de la hachure parallèle
                    x_depart = centre_x - math.sqrt((rayon-espacement_lignes)**2 - ((rayon-espacement_lignes) - passe * espacement_lignes)**2)
                    y_depart = centre_y - ((rayon-espacement_lignes) - passe * espacement_lignes)
                    # Calcul des coordonnées du point d'arrivée de la hachure parallèle
                    x_arrivee = centre_x + math.sqrt((rayon-espacement_lignes)**2 - ((rayon-espacement_lignes) - passe * espacement_lignes)**2)
                    y_arrivee = centre_y - ((rayon-espacement_lignes) - passe * espacement_lignes)
                else:
                    # Calcul des coordonnées du point de départ de la hachure parallèle
                    y_depart = centre_y - math.sqrt((rayon-espacement_lignes)**2 - ((rayon-espacement_lignes) - passe * espacement_lignes)**2)
                    x_depart = centre_x - ((rayon-espacement_lignes) - passe * espacement_lignes)
                    # Calcul des coordonnées du point d'arrivée de la hachure parallèle
                    y_arrivee = centre_y + math.sqrt((rayon-espacement_lignes)**2 - ((rayon-espacement_lignes) - passe * espacement_lignes)**2)
                    x_arrivee = centre_x - ((rayon-espacement_lignes) - passe * espacement_lignes)

                # Inversion des points de départ et d'arrivée pour alterner la direction de déplacement
                if inverser_direction:
                    x_depart, x_arrivee = x_arrivee, x_depart
                    y_depart, y_arrivee = y_arrivee, y_depart
                if passe>0:
                    # Ajout de la commande de déplacement vers le point de départ de la hachure parallèle
                    gcode +=gcode_sender(x_depart,y_depart,actual_z_height,True)
                    gcode +=gcode_sender(x_arrivee,y_arrivee,actual_z_height,True)
                else:
                    gcode +=gcode_sender(x_depart,y_depart,actual_z_height,False)
                    gcode +=gcode_sender(x_arrivee,y_arrivee,actual_z_height,False)
                    gcode += "M101 ; extruder on\n"
                    gcode += "G1 F1800\n"

                # Inversion de la direction de déplacement pour la prochaine passe
                inverser_direction = not inverser_direction
                
            gcode += "G1 F2400\n"
            gcode += "M103 ; extruder off\n"
            inverser_sens = not inverser_sens

        couche+=1
    # Update the plot
    update_plot(x_coords, y_coords, z_coords)

def reset_values():
    initialize_values()

def main():
    # Create the interactive interface
    plt.subplots_adjust(left=0.25, bottom=0.25,wspace=500,hspace=500)
    plt.axis('off')

    initialize_values()


    # Create the slider for 'diametre_cercle'
    slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    diametre_slider = Slider(
        ax=slider_ax,
        label='Diametre',
        valmin=0.1,
        valmax=30,
        valinit=diametre_cercle,
    #  orientation="vertical"   
    )
    diametre_slider.on_changed(update_plot)

    # Create the reset button
    reset_ax = plt.axes([0.8, 0.1, 0.1, 0.04])
    reset_button = Button(reset_ax, 'Reset')
    reset_button.on_clicked(reset_values)

    generate_circle_gcode()

main()