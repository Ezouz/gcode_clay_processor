import tensorflow as tf
import numpy as np
import os
import shapely.geometry as sg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
import seaborn as sns

# Définition des constantes
RECTANGLE_WIDTH = 10  # Largeur du rectangle
RECTANGLE_HEIGHT = 10  # Hauteur du rectangle
NUM_FORMES = 120  # Nombre de formes à placer à chaque itération
NUM_ITERATIONS = 100  # Nombre d'itérations pour l'entraînement
BATCH_SIZE = 64  # Taille du lot pour l'entraînement


def trouver_enveloppe_convexe(points):
    hull = ConvexHull(points)
    enveloppe_convexe = points[hull.vertices]
    return enveloppe_convexe

NUM_SAMPLES = 615  # Specify the desired number of samples

# Génération de données d'entraînement aléatoires
def generer_formes():
    formes = []
    for _ in range(NUM_SAMPLES):
        nb_points = np.random.randint(3, 13)  # Nombre aléatoire de points pour chaque forme
        forme = np.random.rand(nb_points, 2)  # Coordonnées (x, y) des points de la forme
        forme = trouver_enveloppe_convexe(forme)
        formes.append(forme)
    return formes

# Génération de données d'entraînement pour le placement aléatoire initial
def generer_placements_initiaux():
    placements = []
    for _ in range(NUM_SAMPLES):
        placement = np.random.rand(2) * [RECTANGLE_WIDTH, RECTANGLE_HEIGHT]  # Placement initial aléatoire
        placements.append(placement)
    return placements

# Fonction de vérification des superpositions avec contrainte du rectangle
def verifier_superposition(forme, placement, autres_formes, autres_placements):
    polygone = sg.Polygon(forme + placement)  # Polygone de la forme actuelle

    # Vérifier si la forme dépasse les limites du rectangle
    if not sg.Polygon([(0, 0), (RECTANGLE_WIDTH, 0), (RECTANGLE_WIDTH, RECTANGLE_HEIGHT), (0, RECTANGLE_HEIGHT)]).contains(polygone):
        return True  # Forme en dehors du rectangle

    for autre_forme, autre_placement in zip(autres_formes, autres_placements):
        autre_polygone = sg.Polygon(autre_forme + autre_placement)  # Polygone de l'autre forme

        if polygone.touches(autre_polygone) or polygone.intersects(autre_polygone):
            return True  # Superposition ou contact détecté

    return False  # Pas de superposition ou de contact détecté

# Définition du modèle de l'IA
input_shape = (None, 4)  # Shape de l'entrée du modèle (nombre de points x 2 + 2)
input_layer = tf.keras.layers.Input(shape=input_shape)
hidden_layer1 = tf.keras.layers.Dense(64, activation='relu')(input_layer)
hidden_layer2 = tf.keras.layers.Dense(64, activation='relu')(hidden_layer1)
output_layer = tf.keras.layers.Dense(2)(hidden_layer2)

output_translation = tf.keras.layers.Dense(2)(hidden_layer2)
output_rotation = tf.keras.layers.Dense(1)(hidden_layer2)
model = tf.keras.models.Model(inputs=input_layer, outputs=[output_translation, output_rotation])


# Fonction de perte (loss) personnalisée
def custom_loss(y_true, y_pred):
    translation_loss = tf.reduce_sum(tf.square(y_true - y_pred))
    return translation_loss


# Compilation du modèle
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss=custom_loss)

formes = generer_formes()  # Générer de nouvelles formes à chaque itération
placements_initiaux = generer_placements_initiaux()  # Générer de nouveaux placements initiaux à chaque itération

for ff in range(NUM_ITERATIONS):
    print("Training started for iteration", ff)
    

    inputs = []
    outputs_translation = []
    outputs_rotation = []

    max_attempts =2  # Nombre maximum d'essais pour éviter la boucle infinie

    for forme, placement_initial in zip(formes, placements_initiaux):
        attempts = 0
        while verifier_superposition(forme, placement_initial, formes, placements_initiaux):
            placement_initial = np.random.rand(2) * [RECTANGLE_WIDTH, RECTANGLE_HEIGHT]
            attempts += 1
            if attempts >= max_attempts:
                break

        if attempts < max_attempts:
            input_data = np.concatenate([forme, np.tile(placement_initial, (len(forme), 1))], axis=1)
            inputs.append(input_data)

            output_translation = np.random.rand(len(forme), 2)
            output_rotation = np.random.rand(1)
            outputs_translation.append(output_translation)
            outputs_rotation.append(output_rotation)

    if len(inputs) > 0:
        inputs = np.concatenate(inputs, axis=0)
    else:
        continue  # Passer à la prochaine itération si la liste est vide
    outputs_translation = np.concatenate(outputs_translation, axis=0)
    outputs_rotation = np.concatenate(outputs_rotation, axis=0)
    outputs = [outputs_translation, outputs_rotation]

    num_samples = min(inputs.shape[0], outputs_translation.shape[0], outputs_rotation.shape[0])
    inputs = inputs[:num_samples]
    outputs_translation = outputs_translation[:num_samples]
    outputs_rotation = outputs_rotation[:num_samples]
    outputs = [outputs_translation, outputs_rotation]

    model.fit(inputs, outputs, batch_size=BATCH_SIZE, epochs=1, verbose=0)



    # Affichage graphique toutes les 10 itérations
    if (ff + 1) % 1 == 0:
        fig, ax = plt.subplots()

        colors = sns.color_palette("hls", len(formes))  # Generate unique colors

        for i, (forme, placement_initial) in enumerate(zip(formes, placements_initiaux)):
            placement_data = np.concatenate([forme, np.tile(placement_initial, (len(forme), 1))], axis=1)
            placement = model.predict(placement_data)

            ax.add_patch(patches.Polygon(forme, alpha=0.5, fc=colors[i]))  # Ajouter cette ligne

            placement_translation, placement_rotation = model.predict(placement_data)

            # Appliquer la translation et la rotation à la forme initiale
            placement = np.array(placement)
            placement_transformed = np.array([
                placement[:, 0] + placement_initial[0] + placement_translation[:, 0],
                placement[:, 1] + placement_initial[1] + placement_translation[:, 1]
            ]).T

            rotation_center = np.mean(placement_initial, axis=0)
            placement_transformed = rotate_points(placement_transformed, rotation_center, placement_rotation)

            # Afficher la forme générée
            ax.add_patch(patches.Polygon(forme, alpha=0.5, fc=colors[i]))

            # Afficher le placement prédit par l'IA
            ax.add_patch(patches.Polygon(placement_transformed, alpha=0.5, fc=colors[i], ec='r'))

            # Annotation du numéro de forme à l'emplacement placement_transformed
            ax.text(placement_transformed[0, 0], placement_transformed[0, 1], str(i+1), color='b', ha='center', va='center', fontsize=4)


        ax.set_xlim(0, RECTANGLE_WIDTH)
        ax.set_ylim(0, RECTANGLE_HEIGHT)
        ax.set_aspect('equal')
        # Exporter le graphique en tant qu'image JPG
        output_folder = "test ML"
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"iteration_{ff+1}.jpg")
        plt.savefig(output_file, format='jpg', dpi=400)

        plt.pause(0.1)  # Pause pour afficher l'aperçu graphique (en secondes)
        plt.close(fig)  # Fermer la figure pour éviter l'accumulation de fenêtres

# Utilisation du modèle pour placer les formes
formes = generer_formes()
placements_initiaux = generer_placements_initiaux()

fig, ax = plt.subplots()

colors = sns.color_palette("hls", len(formes))  # Generate unique colors

for i, (forme, placement_initial) in enumerate(zip(formes, placements_initiaux)):
    placement_data = np.concatenate([forme, np.tile(placement_initial, (len(forme), 1))], axis=1)
    placement = model.predict(placement_data)

    # Affichage de la forme générée
    ax.add_patch(patches.Polygon(forme, alpha=0.5, fc=colors[i]))

    # Affichage du placement prédit par l'IA
    placement_transformed = np.array([
        placement[:, 0] + placement_initial[0],  # Coordonnées x
        placement[:, 1] + placement_initial[1]  # Coordonnées y
    ]).T
    ax.add_patch(patches.Polygon(placement_transformed, alpha=0.5, fc='none', ec='r'))

    # Annotation du numéro de forme
    ax.text(placement_initial[0], placement_initial[1], str(i+1), color='b', ha='center', va='center')

ax.set_xlim(0, RECTANGLE_WIDTH)
ax.set_ylim(0, RECTANGLE_HEIGHT)
ax.set_aspect('equal')
plt.show()
