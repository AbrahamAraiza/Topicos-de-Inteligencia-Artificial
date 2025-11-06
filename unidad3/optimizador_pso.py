import numpy as np
import pyswarms as ps

# importamos la función de aptitud y las constantes del espacio
from funcion_aptitud import calcular_aptitud
from modelo_campo import TAMANO_CAMPO, NUM_SENSORES 

def ejecutar_optimizacion_pso(num_particulas=80, iteraciones=200):
    """
    configura y ejecuta el algoritmo PSO para encontrar la mejor colocación.
    retorna el mejor costo, la mejor posición (coordenadas normalizadas) e historial.
    """
    dimensiones = 2 * NUM_SENSORES # dos dimensiones (x, y) por cada sensor
    
    # 1- definir los límites del espacio de búsqueda (0 a TAMANO_CAMPO)
    limites = (np.zeros(dimensiones), np.ones(dimensiones) * TAMANO_CAMPO)
    
    # 2- configurar los hiperparámetros del enjambre
    opciones = {
        'c1': 0.7,  # componente cognitivo
        'c2': 0.8,  # componente social
        'w': 0.9    # coeficiente de inercia
    }

    # 3- inicializar el optimizador de mejor global
    optimizador = ps.single.GlobalBestPSO(
        n_particles=num_particulas,
        dimensions=dimensiones,
        options=opciones,
        bounds=limites
    )

    # 4- ejecutar la optimización
    print(f"\niniciando optimización PSO con {num_particulas} partículas y {iteraciones} iteraciones...")
    costo, posicion_optima = optimizador.optimize(calcular_aptitud, iters=iteraciones, verbose=True)
    
    print("optimización finalizada!")
    
    return costo, posicion_optima, optimizador.cost_history