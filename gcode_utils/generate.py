import math
from .utils import const

def calculate_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

"""TODO LINK TO FILE HANDLING"""

class PrinterConfig:
    """Configuration de base pour l'imprimante"""
    def __init__(self, max_x=290, max_y=290, nozzle_diameter=2, extrusion_coefficient=0.002935):
        self.max_x = max_x
        self.max_y = max_y
        self.nozzle_diameter = nozzle_diameter
        self.extrusion_coefficient = extrusion_coefficient
        self.center_x = max_x / 2
        self.center_y = max_y / 2


class VaseParameters:
    """Paramètres de génération du vase"""
    def __init__(self, circle_diameter=100, layer_height=0.4, vase_height=150, bottom_layers=16,
                 initial_z_height=1, line_spacing=4, z_variance_enabled=True, z_variance_max=6,
                 z_variance_start_layer=24, z_variance_transition_layers=60, wave_count=8, 
                 star_count=13, petal_size=0.3):
        self.circle_radius = circle_diameter / 2
        self.layer_height = layer_height
        self.vase_height = vase_height
        self.bottom_layers = bottom_layers
        self.initial_z_height = initial_z_height
        self.line_spacing = line_spacing
        self.z_variance_enabled = z_variance_enabled
        self.z_variance_max = z_variance_max
        self.z_variance_start_layer = z_variance_start_layer
        self.z_variance_transition_layers = z_variance_transition_layers
        self.wave_count = wave_count
        self.star_count = star_count
        self.petal_size = petal_size


class GCodeGenerator:
    """Classe responsable de la génération du G-code"""
    def __init__(self, printer_config, vase_params):
        self.printer_config = printer_config
        self.vase_params = vase_params
        self._x, self._y, self._z, self._e = 0, 0, 0, 0
        self.extrude_active = False

    def generate_circle_gcode(self):
        vase = self.vase_params
        printer = self.printer_config
        gcode = self._initialize_gcode()

        z_height = vase.initial_z_height
        layer = 0
        angle_start = 0

        while z_height < vase.vase_height:
            # Définition de l'angle de départ pour chaque couche
            if layer < vase.bottom_layers:
                angle_start += 180  # Alternance pour remplir les couches de base
            else:
                angle_start = 0

            angle = angle_start
            angle_max = angle + 360
            
            # Calcul des coefficients de variance en XY et Z en fonction de la couche
            if vase.z_variance_enabled and layer >= vase.z_variance_start_layer:
                xy_variance_coefficient = (layer - vase.z_variance_start_layer) / vase.z_variance_transition_layers
                z_variance_coefficient = const((layer - vase.z_variance_start_layer) / vase.z_variance_transition_layers, 0, 1)
            else:
                xy_variance_coefficient = 0
                z_variance_coefficient = 0
            
            # Calcul des coordonnées de départ avec variance si applicable
            variance_xy = vase.z_variance_max * math.cos(math.radians(angle) * vase.star_count) * xy_variance_coefficient * vase.petal_size
            variance_z = z_height + vase.z_variance_max * math.cos(math.radians(angle) * vase.wave_count) * z_variance_coefficient
            start_x, start_y = self._circle_coordinates(angle, variance_xy)
            gcode += self._send_gcode(start_x, start_y, variance_z if variance_z != 0 else z_height, extrude=False)

            # Extrusion de la couche circulaire avec variations
            while angle < angle_max:
                if layer >= vase.bottom_layers:
                    z_height += vase.layer_height / 180  # Incrémentation en fonction de la résolution de l'angle
                
                # Application des variations pour les coordonnées (XY) et Z
                variance_xy = vase.z_variance_max * math.cos(math.radians(angle) * vase.star_count) * xy_variance_coefficient * vase.petal_size
                variance_z = z_height + vase.z_variance_max * math.cos(math.radians(angle) * vase.wave_count) * z_variance_coefficient
                
                x, y = self._circle_coordinates(angle, variance_xy)
                gcode += self._send_gcode(x, y, variance_z if variance_z != 0 else z_height, extrude=True)

                angle += 2  # Résolution de l'angle

            layer += 1

        gcode += self._end_gcode()
        self._write_gcode_file("vase_circle_with_variance.gcode", gcode)
        print("Gcode file with variances generated successfully!")

    def _circle_coordinates(self, angle, variance=0):
        """Calcul des coordonnées X, Y d'un point sur le cercle avec une variance optionnelle"""
        x = self.printer_config.center_x + (self.vase_params.circle_radius + variance) * math.cos(math.radians(angle))
        y = self.printer_config.center_y + (self.vase_params.circle_radius + variance) * math.sin(math.radians(angle))
        return x, y

    def _send_gcode(self, x, y, z, extrude=False):
        """Envoie une commande de mouvement et d'extrusion avec ou sans extrusion"""
        gcode = "G1 "
        if x != self._x:
            gcode += f"X{x:.3f} "
        if y != self._y:
            gcode += f"Y{y:.3f} "
        if z != self._z:
            gcode += f"Z{z:.3f} "
        if extrude and self.extrude_active:
            distance = calculate_distance(x, y, z, self._x, self._y, self._z)
            extrusion_amount = distance * math.pi * (self.printer_config.nozzle_diameter / 2) ** 2 * self.printer_config.extrusion_coefficient
            self._e += extrusion_amount
            gcode += f"E{self._e:.5f} "
        
        gcode += "\n"
        self._x, self._y, self._z = x, y, z
        self.extrude_active = extrude
        return gcode

    def _initialize_gcode(self):
        """Initialise le G-code avec des commandes de base et de préparation"""
        return (
            "G28\n"  # Home axes
            "G1 Z5 F5000 ; lift nozzle\n"
            "M73 P0 ; printing progress 0%\n"
            f"G1 Z{self.vase_params.initial_z_height:.2f} F7800\n"
            "G1 E-2 F2400\n"
            "M103 ; extruder off\n"
            "G1 F7800\n"
            ";END OF HOMING\n"
            ";\n"
            ";START OF GCODE\n"
        )

    def _end_gcode(self):
        """Ajoute les commandes de fin au G-code"""
        return (
            "G91 ; use relative positioning for the XYZ axes\n"
            "G1 Z10 F4000 ; move 10mm to the right of the current location\n"
            "G90 ; absolute positioning\n"
            "M106 S0 ; turn off cooling fan\n"
            "M104 S0 ; turn off extruder\n"
            "M140 S0 ; turn off bed\n"
            "G92 E0 ; set current filament position to E=0\n"
            "G1 E-8 F800 ; retract filament\n"
            "M84 ; disable motors\n"
        )

    def _write_gcode_file(self, filename, gcode):
        """Écrit le code G-code dans un fichier spécifié"""
        with open(filename, "w") as f:
            f.write(gcode)


def generate_vase():
    printer_config = PrinterConfig()
    vase_params = VaseParameters()
    gcode_generator = GCodeGenerator(printer_config, vase_params)
    gcode_generator.generate_circle_gcode()
