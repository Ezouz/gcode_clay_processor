if __name__ == "__main__":

    import math
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button
    from mpl_toolkits import mplot3d

    ##### GLOBALS #####
    
    # Écriture du fichier Gcode
    def export_gcode_file():
        with open("gcode_extrusion_cercle.gcode", "w") as f:
            f.write(gcode)
        print("Fichier Gcode généré avec succès !")
        input("")

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

    ##### GLOBALS #####

    # Créer une figure et un axe 3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')


    # plateau
    Xmax = 290 # Taille maximale de l'axe X en mm
    Ymax = 290 # Taille maximale de l'axe Y en mm

    # hauteur de couche
    espacement_lignes = 4 # Espacement entre les lignes de remplissage en mm
    hauteur_first_Z = 1
    hauteur_de_couche = 0.4

    # paramètres extrusion
    diametre_buse = 2 # Diamètre de la buse en mm
    coefficient_extrusion=.008388*.35
    _x=0
    _y=0
    _z=0
    _e=0
    extrude=False

    # variance de Z (ondulation...)
    variance_enable=1
    variance_z_max=6 #mm de variance de hauteur maximum
    variance_starting_layer=24 #couche à laquelle débuter l'ondulation
    variance_actual_z=0

    # parametre forme
    nb_couches_fond=16 #nombre de couches pleines (fond du vase)
    hauteur_vase=150 #hauteur totale du vase

    diametre_cercle = 100 # Diamètre du cercle à extruder en mm
    rayon=diametre_cercle/2

    variance_transition_layer=60 #nb de couche pour la transition entre flat a full ondulation
    nb_de_vaguelette=8

    nb_etoile=13
    taille_petale=.3

    # Définition des constantes
    centre_x = Xmax / 2
    centre_y = Ymax / 2

    ##### GCODE #####

    def calculer_distance_point(x1, y1, z1, x2, y2, z2):
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return distance

    # convertisseur syntax gcode
    def gcode_sender(x, y, z, extrusion):
        global _x
        global _y
        global _z
        global _e
        global extrude
        global diametre_buse
        global coefficient_extrusion
        
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

    # Fonction pour calculer les coordonnées X, Y d'un point sur le cercle
    def coordonnees_cercle(angle, variance=0):
        x = centre_x + (rayon + variance) * math.cos(math.radians(angle))
        y = centre_y + (rayon + variance) * math.sin(math.radians(angle))
        return x, y

    ##### AFFICHAGE #####

    def reset():
        # plateau
        Xmax = 290
        Ymax = 290

        # hauteur de couche
        espacement_lignes = 4
        hauteur_first_Z = 1
        hauteur_de_couche = 0.4

        # paramètres extrusion
        diametre_buse = 2
        coefficient_extrusion=.008388*.35
        _x=0
        _y=0
        _z=0
        _e=0
        extrude=False

        # variance de Z (ondulation...)
        variance_enable=1
        variance_z_max=6 
        variance_starting_layer=24
        variance_actual_z=0

        # parametre forme
        nb_couches_fond=16
        hauteur_vase=150

        diametre_cercle = 100
        rayon=diametre_cercle/2

        variance_transition_layer=60
        nb_de_vaguelette=8

        nb_etoile=13
        taille_petale=.3

        # Définition des constantes
        centre_x = Xmax / 2
        centre_y = Ymax / 2

        update_graph()

    def update_graph():
        ax.clear()
        

    def display():
        btn_increase_a = Button(reset, 'Reset Params')
        btn_increase_a.on_clicked(diametre_cercle)

##### MAIN #####

def main():
    create_base()
    
    # Afficher le graphique interactif
    plt.show()