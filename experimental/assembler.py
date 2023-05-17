"""
assemblage de plusieurs Gcode - obsolete mais translation surement a recuperer

"""


import numpy as np
import glob
import re
import os

def print_file_sizes(file_paths):
    print("Tailles des fichiers G-code disponibles :")
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            gcode_lines = f.readlines()
        piece_size = calculate_piece_size(gcode_lines)
        print(f"{os.path.basename(file_path)} - Taille X: {piece_size[0]}, Taille Y: {piece_size[1]}")

def calculate_piece_size(gcode_lines):
    x_values = []
    y_values = []
    pattern = re.compile(r'([XY])\s*([-]?[\d.]+)')  # Expression régulière mise à jour
    for line in gcode_lines:
        matches = re.findall(pattern, line)
        for match in matches:
            coordinate = match[0] + match[1]  # Concaténer le préfixe et la valeur
            try:
                float_value = float(match[1])
                if coordinate.startswith('X'):
                    x_values.append(float_value)
                elif coordinate.startswith('Y'):
                    y_values.append(float_value)
            except ValueError:
                pass
    if not x_values or not y_values:  # Vérifier si les listes sont vides
        print("Aucune coordonnée X ou Y n'a été trouvée.")
        return 0, 0  # Valeurs par défaut si aucune coordonnée X ou Y n'est trouvée
    piece_x = max(x_values) - min(x_values)
    piece_y = max(y_values) - min(y_values)
    return piece_x, piece_y

def combine_pieces(pieces, quantities, margin, raw_size):
    combined_gcode = []
    current_x = 0
    current_y = 0

    for i, piece in enumerate(pieces):
        quantity = quantities[i]
        piece_gcode = piece["gcode"]  # Access the G-code lines
        piece_x, piece_y = piece["size"]  # Access the piece size

        for _ in range(quantity):
            translated_gcode = translate_piece(piece_gcode, current_x, current_y)
            combined_gcode.extend(translated_gcode)

            current_x += piece_x + margin
            if current_x + piece_x + margin > raw_size[0]:
                current_x = 0
                current_y += piece_y + margin
                if current_y + piece_y + margin > raw_size[1]:
                    print("Erreur : Les pièces ne rentrent pas dans la taille brute spécifiée.")
                    return []

    return combined_gcode

def translate_piece(piece_gcode, x_offset, y_offset):
    translated_gcode = []
    for line in piece_gcode:
        if 'X' in line:
            x_match = re.search(r'X([-]?[\d.]+)', line)
            y_match = re.search(r'Y([-]?[\d.]+)', line)
            if x_match:
                x_value = float(x_match.group(1)) + x_offset
                line = re.sub(r'X([-]?[\d.]+)', 'X{:.4f}'.format(x_value), line)
            if y_match:
                y_value = float(y_match.group(1)) + y_offset
                line = re.sub(r'Y([-]?[\d.]+)', 'Y{:.4f}'.format(y_value), line)
        translated_gcode.append(line)
    return translated_gcode

def main():
    clear_terminal()
    # Ask the user to select the G-code files
    file_paths = glob.glob('*.nc')
    print_file_sizes(file_paths)

    selected_files = input("Sélectionnez les fichiers G-code à combiner (séparés par des virgules): ")
    selected_files = selected_files.split(",")
    quantities = []
    for file in selected_files:
        quantity = int(input(f"Entrez la quantité pour le fichier {file}: "))
        quantities.append(quantity)

    raw_size_x = float(input("Entrez la taille du brut (axe X): "))
    raw_size_y = float(input("Entrez la taille du brut (axe Y): "))
    raw_size = (raw_size_x, raw_size_y)

    margin = float(input("Entrez la marge entre les pièces: "))

    pieces = []
    for file in selected_files:
        with open(file, 'r') as f:
            gcode_lines = f.readlines()
        piece_size = calculate_piece_size(gcode_lines)
        pieces.append({"gcode": gcode_lines, "size": piece_size})

    # Optimiser les positions des pièces
    piece_sizes = [piece["size"] for piece in pieces]
    positions = optimize_piece_positions(piece_sizes, quantities, raw_size, margin)

    combined_gcode = []
    for i, piece in enumerate(pieces):
        quantity = quantities[i]
        piece_gcode = piece["gcode"]
        piece_x, piece_y = piece["size"]

        for j in range(quantity):
            translated_gcode = translate_piece(piece_gcode, positions[j][0], positions[j][1])
            combined_gcode.extend(translated_gcode)

    if combined_gcode:
        output_file = input("Entrez le nom du fichier G-code de sortie: ")
        with open(output_file, 'w') as file:
            file.write('\n'.join(combined_gcode))  # Write the combined G-code with line breaks
        print(f"Le fichier G-code combiné a été enregistré sous {output_file}.")
    else:
        print("Toutes les pièces ne rentrent pas sur le brut. Des fichiers G-code optimisés ont été créés.")

def optimize_piece_positions(piece_sizes, quantities, raw_size, margin):
    # Create an array to store the optimized positions of the pieces
    positions = np.zeros((sum(quantities), 2))

    current_x = 0
    current_y = 0
    index = 0

    for i in range(len(piece_sizes)):
        quantity = quantities[i]
        piece_x, piece_y = piece_sizes[i]

        for _ in range(quantity):
            positions[index] = [current_x, current_y]
            index += 1

            current_x += piece_x + margin
            if current_x + piece_x + margin > raw_size[0]:
                current_x = 0
                current_y += piece_y + margin
                if current_y + piece_y + margin > raw_size[1]:
                    print("Erreur : Les pièces ne rentrent pas dans la taille brute spécifiée.")
                    return positions

    return positions

def clear_terminal():
    # Vérifiez si le système d'exploitation est Windows ou Unix/Linux
    if os.name == 'nt':  # Pour Windows
        _ = os.system('cls')
    else:  # Pour Unix/Linux/Mac
        _ = os.system('clear')


if __name__ == "__main__":
    main()