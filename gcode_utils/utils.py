import re

# Obtenir la hauteur maximum d'impression (Z)
def get_max_z(lines):
    max_height = 0.0
  
    for line in lines:
        if 'Z' in line:
            height_match = re.search(r'Z(\d+\.\d+)', line)
            if height_match:
                height = float(height_match.group(1))
                #print(height)
                if height > max_height:
                    max_height = height
    return max_height

def const(valeur, borne_inf, borne_sup):
    """
    Contraint un float à être entre les bornes inférieure et supérieure spécifiées.
    """
    if valeur < borne_inf:
        valeur = borne_inf
    elif valeur > borne_sup:
        valeur = borne_sup
    return valeur