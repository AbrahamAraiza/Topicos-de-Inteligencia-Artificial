import pandas as pd
import numpy as np
from scipy.spatial import KDTree # usado para la búsqueda eficiente del vecino más cercano

# constantes del espacio de búsqueda normalizado para PSO
TAMANO_CAMPO = 100 
NUM_SENSORES = 10

def cargar_y_preprocesar_datos(ruta_csv="datos cultivos.csv"):
    """
    carga los datos geoespaciales, calcula el índice de riesgo combinado 
    y normaliza las coordenadas para el espacio de búsqueda del PSO (0-100).
    """
    try:
        df = pd.read_csv(ruta_csv)
    except FileNotFoundError:
        print(f"ERROR: archivo CSV no encontrado en la ruta: {ruta_csv}")
        return None, None, None

    # normalización del riesgo
    
    # normalizar salinidad (0 a 1)
    salinidad_norm = (df['Salinidad (dS/m)'] - df['Salinidad (dS/m)'].min()) / \
                     (df['Salinidad (dS/m)'].max() - df['Salinidad (dS/m)'].min())
                     
    # normalizar elevación (0 a 1) - se invierte: baja elevación es ALTO riesgo de drenaje
    elevacion_norm = 1 - (df['Elevacion (m)'] - df['Elevacion (m)'].min()) / \
                         (df['Elevacion (m)'].max() - df['Elevacion (m)'].min())

    # índice de riesgo combinado (60% salinidad + 40% baja elevación)
    df['Indice_Riesgo'] = 0.6 * salinidad_norm + 0.4 * elevacion_norm
    
    # proyección y escalamiento WGS 84
    lat_min, lat_max = df['Latitud'].min(), df['Latitud'].max()
    lon_min, lon_max = df['Longitud'].min(), df['Longitud'].max()
    
    # coordenadas normalizadas (X_norm, Y_norm) para el espacio de búsqueda PSO
    df['X_norm'] = (df['Longitud'] - lon_min) / (lon_max - lon_min) * TAMANO_CAMPO
    df['Y_norm'] = (df['Latitud'] - lat_min) / (lat_max - lat_min) * TAMANO_CAMPO
    
    # mapeo numérico para los cultivos
    mapa_cultivos = {'Maiz': 1, 'Tomate': 2, 'Chile': 3}
    df['ID_Cultivo'] = df['Cultivo'].map(mapa_cultivos)
    
    print(f"datos reales de Guasave cargados y normalizados a un espacio {TAMANO_CAMPO}x{TAMANO_CAMPO}.")
    
    # árbol de búsqueda para las coordenadas normalizadas
    coordenadas_kdtree = df[['X_norm', 'Y_norm']].values
    arbol_kdtree = KDTree(coordenadas_kdtree)
    
    return df, arbol_kdtree, mapa_cultivos