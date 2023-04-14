from src.menu import menu_principal
import math
from src.menu import menu_principal
from gcode_utils import gcode_class

def main():
    gcode_file_selected=""
    gcode_file_selected = menu_principal(gcode_file_selected)
    print(gcode_file_selected)
    gcode = gcode_class.Gcode(gcode_file_selected)
    # print(gcode.max_height)
    # print('---------------------------------')
    # print('gcode.first_part_comments_end')
    # print(gcode.first_part_comments_end)
    # print('---------------------------------')
    # print('gcode.last_part_comments_start')
    # print(gcode.last_part_comments_start)
    # print('---------------------------------')
    # print('gcode.layers')
    # for index, layer in enumerate(gcode.layers):
    #     print(layer, "\n")
    # print('number of layers : ', len(gcode.layers))
    # print('---------------------------------')
    # print('gcode.spirals')
    # for index, spiral in enumerate(gcode.spirals):
    #     print(spiral, "\n")
    # print('number of spirals : ', len(gcode.spirals))
    # print('---------------------------------')
    

# TODO
# select a file => create instance
# instances can be multiples
# 
def generate_circle_gcode():
    #clear_console()
    # Définition des paramètres par l'utilisateur
    Xmax = 290 # Taille maximale de l'axe X en mm
    Ymax = 290 # Taille maximale de l'axe Y en mm
    diametre_cercle = 100 # Diamètre du cercle à extruder en mm
    diametre_buse = 2 # Diamètre de la buse en mm
    espacement_lignes = 3.2 # Espacement entre les lignes de remplissage en mm
    hauteur_first_Z = 2.25
    hauteur_de_couche = 1.5
    rayon=diametre_cercle/2
    pas_deplacement=3.6
    nb_couches_fond=6 #nombre de couches pleines (fond du vase)
    hauteur_vase=150 #hauteur totale du vase
    
    
    #variance de Z(ondulation...)
    variance_z_max=6 #mm de variance de hauteur maximum
    variance_enable=1
    variance_starting_layer=10 #couche à laquelle débuter l'ondulation
    variance_actual_z=0
    variance_transition_layer=20 #nb de couche pour la transition entre flat a full ondulation
    
    # Définition des constantes
    rayon_cercle = diametre_cercle / 2
    centre_x = Xmax / 2
    centre_y = Ymax / 2
    # Calcul de la longueur totale du déplacement
    deplacement_total = math.pi * diametre_cercle

    # Calcul du nombre total d'extrusions nécessaires
    extrusions_total = deplacement_total / diametre_buse

    # Calcul de l'extrusion à chaque étape
    extrusion = deplacement_total / extrusions_total

    # Calcul de la longueur de filament nécessaire pour une extrusion complète d'un cercle
    longueur_filament = math.pi * rayon_cercle * (diametre_buse / 2)

    # Fonction pour calculer les coordonnées X, Y d'un point sur le cercle
    def coordonnees_cercle(angle,variance=0):
        x = centre_x + (rayon_cercle+variance) * math.cos(math.radians(angle))
        y = centre_y + (rayon_cercle+variance) * math.sin(math.radians(angle))
        return x, y

    # Début de la génération du fichier Gcode
    gcode = ""

    # Ajout de la commande d'homming etc.
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

    inverser_sens = False
    actual_z_height = hauteur_first_Z
    couche=0
    angle_depart = 0
    while actual_z_height<hauteur_vase:
        
        # Calcul des coordonnées du point de départ sur le cercle
        if nb_couches_fond>couche:
            angle_depart += 180
        
        angle = angle_depart
      
        angle_max=angle+360
        coeff_reduction_variance_xy=(couche-variance_starting_layer)/variance_transition_layer
        coeff_reduction_variance_z=const((couche-variance_starting_layer)/variance_transition_layer,0,1)
        variance_global=variance_z_max*math.cos(math.radians(angle)*4)*coeff_reduction_variance_xy
        variance_actual_z=actual_z_height+variance_z_max*math.cos(math.radians(angle)*10)*coeff_reduction_variance_z
        if variance_enable==1 and variance_starting_layer<couche:        
            x_depart, y_depart = coordonnees_cercle(angle,variance_global)
        else:
            x_depart, y_depart = coordonnees_cercle(angle)
        gcode += "G1 X{:.2f} Y{:.2f}\n".format(x_depart, y_depart)
        gcode += "M101 ; extruder on\n"
        gcode += "G1 F1800\n"
        
        couche+=1
        actual_z_height = hauteur_first_Z+hauteur_de_couche*couche
        gcode += "G1 Z{:.2f}\n".format( actual_z_height)
        
        # Boucle pour générer les commandes de déplacement pour le cercle avec l'extrusion proportionnelle
        

        
        if variance_enable==1 and variance_starting_layer<couche:
            
            coeff_reduction_variance_xy=(couche-variance_starting_layer)/variance_transition_layer
            coeff_reduction_variance_z=const((couche-variance_starting_layer)/variance_transition_layer,0,1)
            while angle < angle_max:
                variance_global=variance_z_max*math.cos(math.radians(angle)*4)*coeff_reduction_variance_xy
                variance_actual_z=actual_z_height+variance_z_max*math.cos(math.radians(angle)*10)*coeff_reduction_variance_z
                
                x, y = coordonnees_cercle(angle,variance_global)
                
                gcode += "G1 X{:.2f} Y{:.2f} Z{:.2f}  E{:.2f}\n".format(x, y,variance_actual_z, longueur_filament)
                angle += 2 # resolution plus fine

            # Retour au point de départ pour fermer le cercle
            variance_global=variance_z_max*math.cos(math.radians(angle)*10)*coeff_reduction_variance_xy
            variance_actual_z=actual_z_height+variance_z_max*math.cos(math.radians(angle)*10)*coeff_reduction_variance_z
            x, y = coordonnees_cercle(angle,variance_global)
            gcode += "G1 X{:.2f} Y{:.2f} Z{:.2f}  E{:.2f}\n".format(x, y,variance_actual_z, longueur_filament)
        
        else:
        
            while angle < angle_max:
                x, y = coordonnees_cercle(angle)
                
                gcode += "G1 X{:.2f} Y{:.2f} E{:.2f}\n".format(x, y, longueur_filament)
                angle += 5 # Augmenter l'angle de 5 degrés à chaque itération pour déterminer les points du cercle

            # Retour au point de départ pour fermer le cercle
            gcode += "G1 X{:.2f} Y{:.2f} E{:.2f}\n".format(x_depart, y_depart, longueur_filament)



        # Variable pour inverser la direction de déplacement
        inverser_direction = False
        if nb_couches_fond>couche:
            #retractation avant remplissage
            gcode += "G1 E-2 F2400\n"
            gcode += "M103 ; extruder off\n"

            # Calcul du nombre de passes nécessaires pour couvrir le diamètre du cercle
            nombre_passes = int((rayon-pas_deplacement)*2 / pas_deplacement)
            # Boucle pour générer les mouvements de remplissage rectilinéaire
            for passe in range(nombre_passes + 1):
                
                if inverser_sens:
                    
                    # Calcul des coordonnées du point de départ de la hachure parallèle
                    x_depart = centre_x - math.sqrt((rayon-pas_deplacement)**2 - ((rayon-pas_deplacement) - passe * pas_deplacement)**2)
                    y_depart = centre_y - ((rayon-pas_deplacement) - passe * pas_deplacement)

                    # Calcul des coordonnées du point d'arrivée de la hachure parallèle
                    x_arrivee = centre_x + math.sqrt((rayon-pas_deplacement)**2 - ((rayon-pas_deplacement) - passe * pas_deplacement)**2)
                    y_arrivee = centre_y - ((rayon-pas_deplacement) - passe * pas_deplacement)
                else:
                    # Calcul des coordonnées du point de départ de la hachure parallèle
                    y_depart = centre_y - math.sqrt((rayon-pas_deplacement)**2 - ((rayon-pas_deplacement) - passe * pas_deplacement)**2)
                    x_depart = centre_x - ((rayon-pas_deplacement) - passe * pas_deplacement)

                    # Calcul des coordonnées du point d'arrivée de la hachure parallèle
                    y_arrivee = centre_y + math.sqrt((rayon-pas_deplacement)**2 - ((rayon-pas_deplacement) - passe * pas_deplacement)**2)
                    x_arrivee = centre_x - ((rayon-pas_deplacement) - passe * pas_deplacement)


                # Inversion des points de départ et d'arrivée pour alterner la direction de déplacement
                if inverser_direction:
                    x_depart, x_arrivee = x_arrivee, x_depart
                    y_depart, y_arrivee = y_arrivee, y_depart

                if passe>0:
                    # Ajout de la commande de déplacement vers le point de départ de la hachure parallèle
                    gcode += "G1 X{:.2f} Y{:.2f}  E{:.2f}\n".format(x_depart, y_depart,  extrusion)
                    # Ajout de la commande de déplacement vers le point d'arrivée de la hachure parallèle
                    gcode += "G1 X{:.2f} Y{:.2f}  E{:.2f}\n".format(x_arrivee, y_arrivee,  extrusion)
                else:
                    gcode += "G1 X{:.2f} Y{:.2f} E0\n".format(x_depart, y_depart)
                    gcode += "G1 X{:.2f} Y{:.2f} E0\n".format(x_arrivee, y_arrivee)
                    gcode += "M101 ; extruder on\n"
                    gcode += "G1 F7400\n"

                # Inversion de la direction de déplacement pour la prochaine passe
                inverser_direction = not inverser_direction
                
            gcode += "G1 E-2 F2400\n"
            gcode += "M103 ; extruder off\n"
            inverser_sens = not inverser_sens


            
        
        
        
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
    
    
    # Écriture du fichier Gcode
    with open("gcode_extrusion_cercle.gcode", "w") as f:
        f.write(gcode)

    print("Fichier Gcode généré avec succès !")
    input("")

if __name__=="__main__":
	main()
        