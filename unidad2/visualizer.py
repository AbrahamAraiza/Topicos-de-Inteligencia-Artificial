import matplotlib.pyplot as plt
import numpy as np
from model import Solucion 

# define una paleta de colores para las 10 rutas
COLORES_RUTA = plt.cm.get_cmap('hsv', 10) 

def dibujar_mapa_rutas(solucion_final, datos, titulo="Rutas Optimizadas - Culiacán"):
    """
    Dibuja el mapa de Culiacán con los nodos y las rutas finales de la mejor solución.
    """
    df = datos['df_nodos']
    
    # extraer coordenadas
    latitudes = df['Latitud'].values
    longitudes = df['Longitud'].values
    
    # iniciar la figura del mapa
    plt.figure(figsize=(10, 10))
    
    # Dibujar todos los Nodos
    
    # tiendas: círculos pequeños y grises
    indices_tiendas = datos['indices_tiendas']
    plt.scatter(longitudes[indices_tiendas], latitudes[indices_tiendas], 
                c='lightgray', s=50, edgecolors='gray', zorder=1, label='Tiendas (90)')
    
    # centros de distribución (CDs): cuadrados grandes y negros/rojos
    indices_cds = datos['indices_cds']
    plt.scatter(longitudes[indices_cds], latitudes[indices_cds], 
                c='red', marker='s', s=150, zorder=3, label='Centros de Distribución (10)')
    
    # anotar los nombres de los CDs
    for i in indices_cds:
        plt.annotate(df.loc[df['ID_NUMERICO'] == i, 'Nombre'].iloc[0], 
                     (longitudes[i] + 0.001, latitudes[i] + 0.001), fontsize=8)

    # dibujar las rutas (líneas)
    for i, ruta in enumerate(solucion_final.rutas):
        if len(ruta) < 3:
            continue
            
        color = COLORES_RUTA(i) 
        
        # obtener coordenadas de la secuencia de la ruta
        ruta_lat = [latitudes[id] for id in ruta]
        ruta_lon = [longitudes[id] for id in ruta]
        
        # dibujar la línea de la ruta
        plt.plot(ruta_lon, ruta_lat, color=color, linewidth=2.0, alpha=0.8, 
                 zorder=2)
        
        # marcar el nodo CD en el centro de la ruta con un punto más grande
        plt.scatter(longitudes[ruta[0]], latitudes[ruta[0]], color=color, marker='o', s=100, zorder=3)
        
    # configuración final del gráfico
    plt.title(titulo, fontsize=14)
    plt.xlabel("Longitud", fontsize=10)
    plt.ylabel("Latitud", fontsize=10)
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.show()