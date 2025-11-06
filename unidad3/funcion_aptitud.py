import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist # necesario para calcular distancias entre sensores

# importamos el modelo de campo
from modelo_campo import cargar_y_preprocesar_datos, TAMANO_CAMPO, NUM_SENSORES

# cargar datos una sola vez
DATOS_CAMPO, ARBOL_KDTREE, MAPA_CULTIVOS = cargar_y_preprocesar_datos()
if DATOS_CAMPO is None:
    # aseguramos que las constantes existan para evitar errores de importación en otros módulos
    DATOS_CAMPO = pd.DataFrame()
    
MIN_SENSORES_CULTIVO = 2 # mínimo de sensores requerido por cultivo (ajustable)

# pesos (W) para la función objetivo
PESO_CULTIVO = 1000  # máxima prioridad
PESO_RIESGO = 100    # alta prioridad
PESO_COBERTURA = 10  # baja prioridad

def calcular_aptitud(posiciones_enjambre):
    """
    función de aptitud (fitness) que PSO intentará minimizar.
    evalúa las coordenadas normalizadas (X, Y) de los sensores.
    """
    if DATOS_CAMPO.empty:
        return np.inf * np.ones(posiciones_enjambre.shape[0])

    num_particulas = posiciones_enjambre.shape[0]
    aptitud = np.zeros(num_particulas)
    
    # IDs de cultivo a buscar (1, 2, 3)
    IDS_CULTIVOS = list(MAPA_CULTIVOS.values())
    
    for i in range(num_particulas):
        particula_actual = posiciones_enjambre[i, :]
        # redimensionar el vector plano a pares de coordenadas (x_norm, y_norm)
        coordenadas_sensores = particula_actual.reshape(NUM_SENSORES, 2)
        
        # 1- asegurar coordenadas válidas (dentro del rango 0-100)
        coordenadas_sensores = np.clip(coordenadas_sensores, 0, TAMANO_CAMPO).astype(float)
        
        # búsqueda georreferenciada inversa (usando KDtree)
        # encontramos el punto de dato real más cercano para cada ubicación de sensor
        # k=1 para buscar el vecino más cercano.
        distancias, indices = ARBOL_KDTREE.query(coordenadas_sensores, k=1)
        
        # obtenemos los atributos de los puntos de datos más cercanos
        ids_cultivos_cercanos = DATOS_CAMPO['ID_Cultivo'].iloc[indices].values
        riesgo_cercano = DATOS_CAMPO['Indice_Riesgo'].iloc[indices].values
        
        # P1: penalización por cobertura (amontonamiento)
        # minimizar: 1 / (distancia mínima entre sensores)
        if coordenadas_sensores.shape[0] > 1:
            distancias_pares = pdist(coordenadas_sensores)
            dist_minima = np.min(distancias_pares) if distancias_pares.size > 0 else 0.001
        else:
            dist_minima = 0.001
            
        P_cobertura = 1 / (dist_minima + 1e-6)

        # P2: penalización por zonas de riesgo
        # minimizar: 1 - promedio de riesgo cubierto (alto promedio de riesgo cubierto = bajo costo)
        P_riesgo = 1 - np.mean(riesgo_cercano)

        # P3: penalización por cultivo (requisito mínimo)
        P_cultivo = 0
        for id_c in IDS_CULTIVOS:
            conteo = np.sum(ids_cultivos_cercanos == id_c)
            # penaliza con un valor alto si no se cumple el mínimo
            P_cultivo += max(0, MIN_SENSORES_CULTIVO - conteo) * 100 

        # función objetivo final
        aptitud[i] = (PESO_CULTIVO * P_cultivo) + (PESO_RIESGO * P_riesgo) + (PESO_COBERTURA * P_cobertura)
        
    return aptitud