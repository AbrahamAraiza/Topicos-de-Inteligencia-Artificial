import pandas as pd
import numpy as np
import random
from utils import haversine

# archivo de coordenadas
RUTA_EXCEL = 'datos_distribucion_tiendas.xlsx' 

# Factor de Combustible: Costo asumido por kilómetro
FACTOR_COMBUSTIBLE_POR_KM = 5.0 
NUM_NODOS = 100
NUM_CDS = 10
NUM_TIENDAS = 90

def _generar_datos_ficticios():
    "genera datos solo si el archivo no se encuentra"
    print("--- GENERANDO DATOS FICTICIOS (FALLÓ LECTURA DE EXCEL) ---")
    
    # Coordenada base de Culiacán (aprox)
    lat_base, lon_base = 24.80, -107.40
    
    data = []
    
    # Generar 10 Centros de Distribución (CD)
    for i in range(NUM_CDS):
        lat = lat_base + random.uniform(-0.01, 0.01)
        lon = lon_base + random.uniform(-0.01, 0.01)
        data.append({'Nombre': f'CD {i}', 'Tipo': 'CD', 'Latitud': lat, 'Longitud': lon})

    # Generar 90 Tiendas
    for i in range(NUM_TIENDAS):
        lat = lat_base + random.uniform(-0.08, 0.08)
        lon = lon_base + random.uniform(-0.08, 0.08)
        data.append({'Nombre': f'Tienda {i}', 'Tipo': 'Tienda', 'Latitud': lat, 'Longitud': lon})
        
    df = pd.DataFrame(data)
    
    return df

def cargar_y_procesar_datos():
    """
    Carga el archivo de coordenadas, asigna IDs, y calcula las matrices.
    """
    df_nodos = None
    try:
        df_nodos = pd.read_excel(RUTA_EXCEL)
        if len(df_nodos) != NUM_NODOS:
            raise ValueError(f"El archivo debe tener {NUM_NODOS} filas. Se encontraron {len(df_nodos)}.")
            
    except FileNotFoundError:
        df_nodos = _generar_datos_ficticios()
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        df_nodos = _generar_datos_ficticios()
        
    # preparación de datos: asignamos IDs
    df_nodos = df_nodos.sort_values(by='Tipo', ascending=False).reset_index(drop=True)
    df_nodos['ID_NUMERICO'] = df_nodos.index # ID de 0 a 99
    
    coordenadas = df_nodos[['Latitud', 'Longitud']].values

    # identificación de IDs
    indices_cds = df_nodos[df_nodos['Tipo'] == 'CD']['ID_NUMERICO'].tolist()
    indices_tiendas = df_nodos[df_nodos['Tipo'] == 'Tienda']['ID_NUMERICO'].tolist()
    
    if len(indices_cds) != NUM_CDS:
        print("Error: No se detectaron 10 Centros de Distribución correctamente.")
        return None

    # creación de la matriz de distancias (Haversine)
    matriz_distancia = np.zeros((NUM_NODOS, NUM_NODOS))
    print("Calculando Matriz de Distancia (Haversine)...")
    for i in range(NUM_NODOS):
        for j in range(NUM_NODOS):
            if i != j:
                matriz_distancia[i, j] = haversine(
                    coordenadas[i, 0], coordenadas[i, 1],
                    coordenadas[j, 0], coordenadas[j, 1]
                )

    # creación de la Matriz de Costos de Combustible
    matriz_costo = matriz_distancia * FACTOR_COMBUSTIBLE_POR_KM

    print("Matrices de Distancia y Costo creadas exitosamente.")

    datos = {
        'df_nodos': df_nodos,
        'num_nodos': NUM_NODOS,
        'indices_cds': indices_cds,      
        'indices_tiendas': indices_tiendas, 
        'matriz_distancia': matriz_distancia,
        'matriz_costo': matriz_costo,
        'factor_combustible': FACTOR_COMBUSTIBLE_POR_KM
    }
    return datos