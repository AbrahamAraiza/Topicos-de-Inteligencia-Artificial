import numpy as np

# radio de la tierra en kilómetros (km)
R_TIERRA = 6371.0 

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia de la Gran Círculo (Haversine) entre dos 
    puntos geográficos (latitud y longitud) en kilómetros.
    """
    # convertir grados a radianes
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # diferencias de coordenadas
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # fórmula de Haversine
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distancia = R_TIERRA * c
    return distancia

def calcular_distancia_ruta(ruta_ids, matriz_distancia):
    """Calcula la distancia total de una ruta."""
    distancia_total = 0
    if not ruta_ids or len(ruta_ids) < 2:
        return 0
    
    for i in range(len(ruta_ids) - 1):
        origen_id = ruta_ids[i]
        destino_id = ruta_ids[i+1]
        distancia_total += matriz_distancia[origen_id, destino_id]
        
    return distancia_total