import math
from .utils import const

def calculer_distance_point(x1, y1, z1, x2, y2, z2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance


_x=0
_y=0
_z=0
_e=0
extrude=False


def gcode_sender(x,y,z,extrusion):

    global _x
    global _y
    global _z
    global _e
    global extrude
    
    diametre_buse = 2 # Diamètre de la buse en mm
    coefficient_extrusion=.008388*.35
    
    gcode = "G1 "
    if(x != _x):
            gcode += "X{:.3f} ".format(x)
    if(y != _y):
            gcode += "Y{:.3f} ".format(y)
    if(z != _z):
            gcode += "Z{:.3f} ".format(z)
            
    if(extrusion and extrude):
        _e+=calculer_distance_point(x,y,z,_x,_y,_z) * math.pi * ((diametre_buse/2)**2) * coefficient_extrusion
        gcode += "E{:.5f} ".format(_e)
    
    gcode += "\n" 

    _x=x
    _y=y
    _z=z
    extrude=extrusion
    if gcode == "G1 \n":
        return ""
    else :
        return gcode


def generate_circle_gcode():
    
    fond_en_cours=1
    global _x
    global _y
    global _z
    global _e
    global extrude
    
    
    #clear_console()
    # Définition des paramètres par l'utilisateur
    Xmax = 290 # Taille maximale de l'axe X en mm
    Ymax = 290 # Taille maximale de l'axe Y en mm
    diametre_cercle = 100 # Diamètre du cercle à extruder en mm
    espacement_lignes = 4 # Espacement entre les lignes de remplissage en mm
    hauteur_first_Z = 1
    hauteur_de_couche = 0.4
    rayon=diametre_cercle/2
    nb_couches_fond=16 #nombre de couches pleines (fond du vase)
    hauteur_vase=150 #hauteur totale du vase
    
    
    #variance de Z(ondulation...)
    variance_enable=1
    variance_z_max=6 #mm de variance de hauteur maximum
    variance_starting_layer=24 #couche à laquelle débuter l'ondulation
    variance_actual_z=0
    variance_transition_layer=60 #nb de couche pour la transition entre flat a full ondulation
    nb_de_vaguelette=8
    nb_etoile=13
    taille_petale=.3
    
    # Définition des constantes
    centre_x = Xmax / 2
    centre_y = Ymax / 2

    # Fonction pour calculer les coordonnées X, Y d'un point sur le cercle
    def coordonnees_cercle(angle,variance=0):
        x = centre_x + (rayon+variance) * math.cos(math.radians(angle))
        y = centre_y + (rayon+variance) * math.sin(math.radians(angle))
        return x, y

    

    # Ajout de la commande d'homming etc.
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
                gcode +=gcode_sender(x,y,variance_actual_z,True)
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
    
    
    
