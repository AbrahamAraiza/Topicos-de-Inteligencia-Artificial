from data_loader import cargar_y_procesar_datos
from metaheuristica import recocido_simulado
from visualizer import dibujar_mapa_rutas 

def prueba_1_ejecucion_sa(datos):
    """
    Ejecución del Algoritmo de Recocido Simulado.
    """
    print("===================================================")
    print("INICIANDO PRUEBA DE IMPLEMENTACION ===========")
    print("===================================================")
    
    # parámetros del recocido Simulado
    params_sa = {
        'temperatura_inicial': 1000.0,  # valor alto para aceptar peores soluciones inicialmente
        'temperatura_final': 1.0,       # valor bajo para terminar
        'tasa_enfriamiento': 0.999,     # tasa de enfriamiento lenta para una búsqueda profunda
        'iteraciones_por_temp': 100     # iteraciones en cada nivel de temperatura
    }

    mejor_solucion_final = recocido_simulado(datos, params_sa)

    # mostrar la mejor ruta global al final
    print("\n===================================================")
    print(" MEJOR RUTA GLOBAL FINAL ENCONTRADA")
    print(f"Costo Global Final (Distancia Total): {mejor_solucion_final.costo_global:.2f} km")
    print("===================================================")

    detalles_finales = mejor_solucion_final.obtener_detalles_ruta(datos['df_nodos'])
    detalles_finales.sort(key=lambda x: x['id_cd'])
    
    for i, detalle in enumerate(detalles_finales):
        # Muestra la información final con el formato solicitado
        print(f"Ruta {i+1}:")
        print(f"\t| Ruta Combustible: {detalle['costo_combustible']:.2f} | Ruta Distancia: {detalle['distancia']:.2f} km")
        print(f"\tRuta: {detalle['ruta_descriptiva']}")
        print("-" * 30)

    # visualización de la ruta final
    print("\nGenerando Mapa de Rutas...")
    dibujar_mapa_rutas(mejor_solucion_final, datos, "Mejor Solución de Enrutamiento (MDVRP) - Culiacán")


if __name__ == "__main__":
    
    # cargar datos
    datos_proyecto = cargar_y_procesar_datos()
    
    if datos_proyecto:
        # ejecutar prueba de implementación
        prueba_1_ejecucion_sa(datos_proyecto)