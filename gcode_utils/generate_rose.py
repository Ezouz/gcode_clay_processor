import math

def calculate_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

"""TODO LINK TO FILE HANDLING"""

class PrinterConfig:
    def __init__(self, max_x=290, max_y=290, nozzle_diameter=2, extrusion_coefficient=0.002935):
        self.max_x = max_x
        self.max_y = max_y
        self.nozzle_diameter = nozzle_diameter
        self.extrusion_coefficient = extrusion_coefficient
        self.center_x = max_x / 2
        self.center_y = max_y / 2

class RosetteParameters:
    def __init__(self, n=1, d=3, petal_size=10, layer_height=0.4, vase_height=5, 
                 initial_z_height=1, z_variance_enabled=False, z_variance_max=6, 
                 z_variance_start_layer=24, z_variance_transition_layers=60):
        self.n = n                          # Numerator for k = n/d
        self.d = d                          # Denominator for k = n/d
        self.petal_size = petal_size        # Overall size of the petal pattern
        self.layer_height = layer_height    # Layer height
        self.vase_height = vase_height      # Total vase height
        self.initial_z_height = initial_z_height
        self.z_variance_enabled = z_variance_enabled
        self.z_variance_max = z_variance_max
        self.z_variance_start_layer = z_variance_start_layer
        self.z_variance_transition_layers = z_variance_transition_layers

class GCodeGenerator:
    def __init__(self, printer_config, rosette_params):
        self.printer_config = printer_config
        self.rosette_params = rosette_params
        self._x, self._y, self._z, self._e = 0, 0, 0, 0
        self.extrude_active = False

    def generate_rosette_gcode(self):
        params = self.rosette_params
        printer = self.printer_config
        gcode = self._initialize_gcode()

        z_height = params.initial_z_height
        layer = 0
        angle_step = 5  # Angular resolution in degrees

        # Calcul de k pour r = petal_size * cos(k * theta)
        k = params.n / params.d

        while z_height < params.vase_height:
            angle = 0
                        # Utiliser un angle de 0 à 720 pour couvrir deux cycles de cosinus
            while angle < 10000:
                # Calcul du rayon r pour obtenir des lobes intérieurs et extérieurs
                r = params.petal_size * math.cos(math.radians(k * angle))
                x = printer.center_x + r * math.cos(math.radians(angle))
                y = printer.center_y + r * math.sin(math.radians(angle))
                
                # Incrémenter l'angle
                angle += 2  # Résolution angulaire de 2 degrés
                
                # Calcul de la variance en Z si activé
                if params.z_variance_enabled and layer >= params.z_variance_start_layer:
                    z_variance_coefficient = min(1, (layer - params.z_variance_start_layer) / params.z_variance_transition_layers)
                    variance_z = z_height + params.z_variance_max * math.sin(math.radians(k * angle)) * z_variance_coefficient
                else:
                    variance_z = z_height

                # Envoi du G-code pour chaque point
                gcode += self._send_gcode(x, y, variance_z if variance_z != 0 else z_height, extrude=True)
                angle += angle_step

            layer += 1
            z_height += params.layer_height  # Incrémentation de la hauteur Z par la hauteur de couche

        gcode += self._end_gcode()
        self._write_gcode_file("rosette_pattern.gcode", gcode)
        print("G-code pour le motif de rosace généré avec succès!")

    def _send_gcode(self, x, y, z, extrude=False):
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
        return (
            "G28\n"
            "G1 Z5 F5000 ; lift nozzle\n"
            "M73 P0 ; printing progress 0%\n"
            f"G1 Z{self.rosette_params.initial_z_height:.2f} F7800\n"
            "G1 E-2 F2400\n"
            "M103 ; extruder off\n"
            "G1 F7800\n"
            ";END OF HOMING\n"
            ";\n"
            ";START OF GCODE\n"
        )

    def _end_gcode(self):
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
        with open(filename, "w") as f:
            f.write(gcode)

def generate_rose():
    printer_config = PrinterConfig()
    rosette_params = RosetteParameters()
    gcode_generator = GCodeGenerator(printer_config, rosette_params)
    gcode_generator.generate_rosette_gcode()
