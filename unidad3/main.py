import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# importar las funciones de los módulos
from optimizador_pso import ejecutar_optimizacion_pso
from modelo_campo import cargar_y_preprocesar_datos, NUM_SENSORES, TAMANO_CAMPO

def transformar_a_geografico(df_datos, posicion_optima):
    """
    transforma las coordenadas normalizadas (0-100) de vuelta a Latitud y Longitud (WGS 84).
    """
    if df_datos is None:
        return None
        
    # obtener los límites originales del campo
    lat_min, lat_max = df_datos['Latitud'].min(), df_datos['Latitud'].max()
    lon_min, lon_max = df_datos['Longitud'].min(), df_datos['Longitud'].max()
    
    # el resultado 'posicion_optima' es un vector plano [x1, y1, x2, y2, ...]
    coordenadas_norm = posicion_optima.reshape(NUM_SENSORES, 2)
    
    # 1- revertir la normalización de X (Longitud)
    longitudes_optimas = (coordenadas_norm[:, 0] / TAMANO_CAMPO) * \
                         (lon_max - lon_min) + lon_min
                         
    # 2- revertir la normalización de Y (Latitud)
    latitudes_optimas = (coordenadas_norm[:, 1] / TAMANO_CAMPO) * \
                        (lat_max - lat_min) + lat_min
                        
    return pd.DataFrame({
        'Latitud_Optima': latitudes_optimas, 
        'Longitud_Optima': longitudes_optimas
    })

def visualizar_resultados(df_datos, coordenadas_optimas_geo, historial_costo):
    """genera los dos gráficos de resultados (colocación Geoespacial y convergencia)"""
    
    # gráfico de colocación geoespacial (prueba funcional)
    plt.figure(figsize=(10, 8))
    
    # definir los colores para los cultivos
    cultivo_colores = {'Maiz': 'gold', 'Tomate': 'red', 'Chile': 'green'}
    
    # plotear los datos del campo por cultivo (fondo)
    for cultivo, color in cultivo_colores.items():
        subconjunto = df_datos[df_datos['Cultivo'] == cultivo]
        plt.scatter(subconjunto['Longitud'], subconjunto['Latitud'], 
                    s=50, alpha=0.5, color=color, label=cultivo)
    
    # superponer el índice de riesgo como mapa de calor
    mapa_riesgo = plt.scatter(df_datos['Longitud'], df_datos['Latitud'], 
                c=df_datos['Indice_Riesgo'], cmap='Reds', s=30, alpha=0.8)
    plt.colorbar(mapa_riesgo, label='Índice de Riesgo Combinado (Alto = Más Rojo)')

    # dibujar las ubicaciones óptimas de los sensores (resultado del PSO)
    plt.scatter(coordenadas_optimas_geo['Longitud_Optima'], coordenadas_optimas_geo['Latitud_Optima'], 
                marker='X', color='black', edgecolors='white', s=200, linewidth=2, 
                label='Sensores Óptimos (PSO)')
    
    plt.title('Solución Óptima PSO: Colocación de Sensores en Guasave (WGS 84)')
    plt.xlabel('Longitud (°)')
    plt.ylabel('Latitud (°)')
    plt.legend(loc='lower left')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

    # gráfico de convergencia (análisis de eficiencia)
    plt.figure(figsize=(8, 5))
    plt.plot(historial_costo)
    plt.title('Convergencia del Algoritmo PSO')
    plt.xlabel('Iteración')
    plt.ylabel('Función de Aptitud (Costo Mínimo)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

def main():
    """Función principal de ejecución del proyecto."""
    print("Proyecto: Optimización de Riego con PSO (Guasave)")
    
    # 1- cargar y normalizar datos reales
    df_datos, arbol_kdtree, mapa_cultivos = cargar_y_preprocesar_datos()
    if df_datos is None:
        return 
        
    # 2- ejecutar la optimización 
    costo_optimo, posicion_optima, historial_costo = ejecutar_optimizacion_pso(num_particulas=80, iteraciones=200)
    
    print(f"\nresultados finales de la optimización")
    print(f"mejor costo (fitness): {costo_optimo:.4f}")
    
    # 3- transformación inversa para visualización
    coordenadas_optimas_geo = transformar_a_geografico(df_datos, posicion_optima)
    
    # 4- visualizar
    if coordenadas_optimas_geo is not None:
        visualizar_resultados(df_datos, coordenadas_optimas_geo, historial_costo)

if __name__ == '__main__':
    main()