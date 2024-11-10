import math
import random

"""TODO LINK TO FILE HANDLING"""


def calculate_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


class PrinterConfig:
    def __init__(
        self, max_x=120, max_y=120, nozzle_diameter=2, extrusion_coefficient=0.002935
    ):
        self.max_x = max_x
        self.max_y = max_y
        self.nozzle_diameter = nozzle_diameter
        self.extrusion_coefficient = extrusion_coefficient
        self.center_x = max_x / 2
        self.center_y = max_y / 2


class RosetteParameters:

    def __init__(
        self,
        n=2,
        d=7,
        ticul=False,
        radius=5,
        layer_height=0.4,
        vase_height=5,
        initial_z_height=1,
        precision=1,
        z_variance_enabled=False,
        z_variance_max=6,
        z_variance_start_layer=24,
        z_variance_transition_layers=60,
        stretch_factor_x=1.0,
        stretch_factor_y=1.0,
        inner_layer_end_height=0,
        y_wave_amplitude=0,
        y_wave_frequency=0,
        x_wave_amplitude=0,
        x_wave_frequency=0,
        natural=True,
        noise_amplitude=0,
        noise_scale=0,
        octaves=0,
        persistence=0,
        lacunarity=0,
    ):
        self.n = n  # Numerator for k = n/d
        self.d = d  # Denominator for k = n/d
        self.ticul = ticul
        self.radius = radius
        self.layer_height = layer_height  # Layer height
        self.vase_height = vase_height  # Total vase height
        self.initial_z_height = initial_z_height
        self.precision = precision
        self.z_variance_enabled = z_variance_enabled
        self.z_variance_max = z_variance_max
        self.z_variance_start_layer = z_variance_start_layer
        self.z_variance_transition_layers = z_variance_transition_layers
        self.stretch_factor_x = stretch_factor_x
        self.stretch_factor_y = stretch_factor_y
        self.inner_layer_end_height = inner_layer_end_height
        self.x_wave_amplitude = x_wave_amplitude
        self.x_wave_frequency = x_wave_frequency
        self.y_wave_amplitude = y_wave_amplitude
        self.y_wave_frequency = y_wave_frequency
        self.natural = natural
        self.noise_amplitude = noise_amplitude
        self.noise_scale = noise_scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity


class GCodeGenerator:
    def __init__(self, printer_config, rosette_params):
        self.printer_config = printer_config
        self.rosette_params = rosette_params
        self._x, self._y, self._z, self._e = 0, 0, 0, 0
        self.extrude_active = False
        self.gradient = {}

    def calculate_max_angle(self):
        return (
            360
            * self.rosette_params.d
            / gcd(self.rosette_params.n, self.rosette_params.d)
        )

    def generate_rosette_gcode(self):
        params = self.rosette_params
        printer = self.printer_config
        gcode = self._initialize_gcode()

        z_height = params.initial_z_height
        layer = 0
        angle_step = params.precision
        max_angle = self.calculate_max_angle()
        k = params.n / float(params.d)

        while z_height < params.vase_height:
            angle = 0

            while angle < max_angle:

                if params.n == 1 and params.d == 1:
                    r = params.radius  # Cercle parfait
                else:
                    # Calcul du rayon r pour obtenir des lobes intérieurs et extérieurs
                    if params.ticul:
                        r = params.radius * abs(math.cos(math.radians(k * angle))) 
                    else:
                        r = params.radius * math.cos(math.radians(k * angle))


                # Calcul des coordonnées initiales sans distorsion
                base_x = r * math.cos(math.radians(angle))
                base_y = r * math.sin(math.radians(angle))

                # Ajout des ondes pour déformer le tracé de manière équilibrée
                wave_x = params.x_wave_amplitude * math.cos(
                    math.radians(params.x_wave_frequency * angle)
                )
                wave_y = params.y_wave_amplitude * math.sin(
                    math.radians(params.y_wave_frequency * angle)
                )

                if params.natural:
                    noise = params.noise_amplitude * self._generate_combined_noise(
                        z_height, angle, params
                    )
                else:
                    noise = params.noise_amplitude * self._blop(
                        z_height * params.noise_scale,
                        angle * params.noise_scale,
                        params.noise_scale,
                        params.octaves,
                        params.persistence,
                        params.lacunarity,
                    )

                # Calcul des coordonnées x et y
                x = printer.center_y + (base_x + wave_x + noise)
                y = printer.center_y + (base_y + wave_y + noise)

                x += params.x_wave_amplitude * math.cos(
                    math.radians(params.x_wave_frequency * angle)
                )
                y += params.y_wave_amplitude * math.sin(
                    math.radians(params.y_wave_frequency * angle)
                )

                # Calcul de la variance en Z si activé
                if params.z_variance_enabled and layer >= params.z_variance_start_layer:
                    z_variance_coefficient = min(
                        1,
                        (layer - params.z_variance_start_layer)
                        / params.z_variance_transition_layers,
                    )
                    variance_z = (
                        z_height
                        + params.z_variance_max
                        * math.sin(math.radians(k * angle))
                        * z_variance_coefficient
                    )
                else:
                    variance_z = z_height

                gcode += self._send_gcode(
                    x,
                    y,
                    variance_z if variance_z != 0 else z_height,
                    extrude=True,
                )

                angle += angle_step

            layer += 1
            z_height += params.layer_height

        gcode += self._end_gcode()
        self._write_gcode_file("rosette_pattern.gcode", gcode)
        print("G-code pour le motif de rosace généré avec succès!")

    def _generate_gradient(self, x, y):
        """Génère un vecteur aléatoire pour un point de la grille"""
        angle = random.uniform(0, 2 * math.pi)
        return math.cos(angle), math.sin(angle)

    def _dot_grid_gradient(self, ix, iy, x, y):
        """Calcule le produit scalaire entre le vecteur de gradient et le vecteur de distance"""
        if (ix, iy) not in self.gradient:
            self.gradient[(ix, iy)] = self._generate_gradient(ix, iy)

        grad_x, grad_y = self.gradient[(ix, iy)]
        dx = x - ix
        dy = y - iy
        return dx * grad_x + dy * grad_y

    def _fade(self, t):
        """Fonction d'adoucissement de Perlin"""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a, b, t):
        """Interpolation linéaire"""
        return a + t * (b - a)

    def _perlin_noise(self, x, y, scale, octaves, persistence, lacunarity):
        total = 0
        frequency = scale
        amplitude = 1
        max_value = 0  # Normalisation

        for _ in range(octaves):
            # Convertir x, y en coordonnées de la grille
            x_scaled = x * frequency
            y_scaled = y * frequency

            x0 = int(x_scaled)
            x1 = x0 + 1
            y0 = int(y_scaled)
            y1 = y0 + 1

            # Calculer les coordonnées relatives
            sx = self._fade(x_scaled - x0)
            sy = self._fade(y_scaled - y0)

            # Interpolation des points de la grille
            n0 = self._dot_grid_gradient(x0, y0, x_scaled, y_scaled)
            n1 = self._dot_grid_gradient(x1, y0, x_scaled, y_scaled)
            ix0 = self._lerp(n0, n1, sx)

            n0 = self._dot_grid_gradient(x0, y1, x_scaled, y_scaled)
            n1 = self._dot_grid_gradient(x1, y1, x_scaled, y_scaled)
            ix1 = self._lerp(n0, n1, sx)

            value = self._lerp(ix0, ix1, sy)
            total += value * amplitude

            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity

        return total / max_value

    def _generate_combined_noise(self, x, y, params):
        """Générer un bruit avec des variations de largeur"""
        # Couche 1 : Bruit principal
        primary_noise = self._perlin_noise(
            x,
            y,
            params.noise_scale,
            params.octaves,
            params.persistence,
            params.lacunarity,
        )

        # Couche 2 : Bruit pour moduler la largeur
        scale_variation = self._perlin_noise(
            x * 0.1, y * 0.1, params.noise_scale * 0.5, 3, 0.5, 2.0
        )

        # Appliquer la modulation sur le bruit principal
        adjusted_noise = primary_noise * (1 + 0.5 * scale_variation)

        return adjusted_noise

    # def _blop(self, x, y):
    #     return math.sin(x * 2 * math.pi) * math.cos(y * 2 * math.pi)

    def _blop(self, x, y, scale, octaves, persistence, lacunarity):
        """
        Génère un bruit de Perlin 2D avec octaves pour obtenir des ondulations naturelles.

        Paramètres :
        - x, y : coordonnées
        - scale : échelle du bruit
        - octaves : nombre d'octaves pour ajouter des détails
        - persistence : impact de chaque octave supplémentaire (amplitude décroissante)
        - lacunarity : facteur d'augmentation de la fréquence pour chaque octave

        Retourne :
        - valeur du bruit entre -1 et 1
        """
        total = 0
        frequency = 3
        amplitude = 0.3
        max_value = 0  # Utilisé pour normaliser le résultat final

        for _ in range(octaves):
            # Générer du bruit pseudo-aléatoire
            noise_value = math.sin(frequency * x) * math.cos(frequency * y)
            total += noise_value * amplitude * scale
            max_value += amplitude

            # Ajuster la fréquence et l'amplitude pour la prochaine octave
            amplitude *= persistence
            frequency *= lacunarity

        return total / max_value

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
            extrusion_amount = (
                distance
                * math.pi
                * (self.printer_config.nozzle_diameter / 2) ** 2
                * self.printer_config.extrusion_coefficient
            )
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

    rosette_params = RosetteParameters(
        # Base rules
        radius=5,  # Overall size of the petal pattern
        vase_height=30,  # hauteur finale (z * layer_height)
        layer_height=0.4,  # Hauteur de couche
        initial_z_height=1,  # Hauteur de couche initiale
        precision=0.5,  # Angular resolution in degrees
        # Rosace params
        n=1,  # Numerator for k = n/d
        d=2,  # Denominator for k = n/d
        ticul=True,  # ptit cul sur les 1/2, 1/3
        # Transformation pour ajouter des ondulations
        stretch_factor_x=0,  # Étirement sur l'axe X (horizontal)
        stretch_factor_y=0,  # Compression sur l'axe Y (vertical)
        # Variance en z
        z_variance_enabled=False,
        z_variance_max=6,
        z_variance_start_layer=24,
        z_variance_transition_layers=60,
        # double le fond sur une certaine hauteur
        inner_layer_end_height=7,
        # wave
        x_wave_amplitude=0,
        x_wave_frequency=0,
        y_wave_amplitude=0,
        y_wave_frequency=0,
        # noise
        natural=True,
        noise_amplitude=0.4,
        noise_scale=0.29,  # froufrous
        octaves=4,
        persistence=0.5,
        lacunarity=1.5,
        # TODO possibilité de faire ,ca un layer de tant de couches sur 2
        # TODO rotations
        # TODO faire reuire le diamettre de la forme sur la hauteur
    )
    gcode_generator = GCodeGenerator(printer_config, rosette_params)

    gcode_generator.generate_rosette_gcode()
