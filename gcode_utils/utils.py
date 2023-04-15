def const(valeur, borne_inf, borne_sup):
    """
    Contraint un float à être entre les bornes inférieure et supérieure spécifiées.
    """
    if valeur < borne_inf:
        valeur = borne_inf
    elif valeur > borne_sup:
        valeur = borne_sup
    return valeur