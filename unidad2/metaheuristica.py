import random
import numpy as np
import copy
from model import Solucion
from data_loader import FACTOR_COMBUSTIBLE_POR_KM


def generar_solucion_inicial(datos):
    """
    Genera una solución inicial utilizando la Heurística del Vecino Más Cercano (Nearest Neighbor)
    para asignar cada tienda a su Centro de Distribución (CD) más cercano, y luego ordena la secuencia.
    """
    indices_cds = datos['indices_cds']
    indices_tiendas = datos['indices_tiendas']
    matriz_distancia = datos['matriz_distancia']
    num_cds = len(indices_cds)
    
    tiendas_por_cd = {cd_id: [] for cd_id in indices_cds}
    
    # asignación de tiendas al CD más cercano (Proximidad)
    for tienda_id in indices_tiendas:
        mejor_cd = -1
        distancia_minima = float('inf')
        
        for cd_id in indices_cds:
            distancia_actual = matriz_distancia[cd_id, tienda_id]
            if distancia_actual < distancia_minima:
                distancia_minima = distancia_actual
                mejor_cd = cd_id
        
        tiendas_por_cd[mejor_cd].append(tienda_id)

    # optimizacion interna (secuencia de visitas usando Nearest Neighbor)
    rutas_iniciales = []
    for cd_id in indices_cds:
        tiendas_asignadas = tiendas_por_cd[cd_id]
        ruta_optimizada = [cd_id]
        
        if tiendas_asignadas:
            ruta_actual = [cd_id] 
            nodos_pendientes = set(tiendas_asignadas)
            
            while nodos_pendientes:
                ultimo_nodo = ruta_actual[-1]
                siguiente_nodo = -1
                distancia_minima_local = float('inf')
                
                for nodo_pendiente in nodos_pendientes:
                    distancia = matriz_distancia[ultimo_nodo, nodo_pendiente]
                    if distancia < distancia_minima_local:
                        distancia_minima_local = distancia
                        siguiente_nodo = nodo_pendiente
                
                ruta_actual.append(siguiente_nodo)
                nodos_pendientes.remove(siguiente_nodo)

            # formato de la ruta: [CD -> T1 -> T2 -> ... -> CD]
            ruta_optimizada = ruta_actual + [cd_id]

        rutas_iniciales.append(ruta_optimizada)
        
    return Solucion(rutas_iniciales, datos['matriz_distancia'], datos['matriz_costo'])


def generar_vecino(solucion_actual, datos):
    """
    Genera una solución vecina mediante un movimiento aleatorio (Intercambio o Reubicación).
    """
    nueva_solucion_rutas = copy.deepcopy(solucion_actual.rutas)
    
    movimiento = random.choice(['reubicacion', 'intercambio'])

    if movimiento == 'reubicacion':
        # movimiento de reubicación (entre rutas)
        rutas_no_vacias = [i for i, r in enumerate(nueva_solucion_rutas) if len(r) > 2]
        if not rutas_no_vacias: return generar_solucion_inicial(datos)
        
        idx_ruta_origen = random.choice(rutas_no_vacias)
        ruta_origen = nueva_solucion_rutas[idx_ruta_origen]
        
        # seleccionar la tienda a mover (índices 1 al penúltimo)
        idx_tienda_a_mover = random.randint(1, len(ruta_origen) - 2)
        tienda_a_mover = ruta_origen.pop(idx_tienda_a_mover)
        
        idx_ruta_destino = random.choice(range(len(nueva_solucion_rutas)))
        ruta_destino = nueva_solucion_rutas[idx_ruta_destino]

        # insertar la tienda en una posición aleatoria en la ruta de destino 
        pos_destino = random.randint(1, len(ruta_destino) - 1)
        ruta_destino.insert(pos_destino, tienda_a_mover)

    elif movimiento == 'intercambio':
        # movimiento de intercambio (intra-ruta / TSP)
        idx_ruta = random.choice(range(len(nueva_solucion_rutas)))
        ruta = nueva_solucion_rutas[idx_ruta]
        
        if len(ruta) >= 4: # minimo 2 tiendas + 2 CDs
            i, j = random.sample(range(1, len(ruta) - 1), 2)
            ruta[i], ruta[j] = ruta[j], ruta[i]

    # crear y devolver la nueva solución
    return Solucion(nueva_solucion_rutas, datos['matriz_distancia'], datos['matriz_costo'])

def recocido_simulado(datos, params):
    """
    Implementación del algoritmo de Recocido Simulado
    """
    # inicialización
    solucion_actual = generar_solucion_inicial(datos)
    mejor_solucion = copy.deepcopy(solucion_actual)
    
    T = params['temperatura_inicial']
    
    print("\n--- INICIO DEL ALGORITMO DE RECOCIDO SIMULADO ---")
    
    iteracion = 0
    while T > params['temperatura_final']:
        
        for _ in range(params['iteraciones_por_temp']):
            iteracion += 1
            
            # generar una solución vecina
            solucion_vecina = generar_vecino(solucion_actual, datos)
            
            # calcular la diferencia de costo (delta E)
            delta_E = solucion_vecina.costo_global - solucion_actual.costo_global
            
            # decisión de aceptación
            if delta_E < 0:
                solucion_actual = solucion_vecina
            else:
                probabilidad_aceptacion = np.exp(-delta_E / T)
                if random.random() < probabilidad_aceptacion:
                    solucion_actual = solucion_vecina

            # actualizar mejor solución global y mostrar Resultado
            if solucion_actual.costo_global < mejor_solucion.costo_global:
                mejor_solucion = copy.deepcopy(solucion_actual)
                
                detalles = mejor_solucion.obtener_detalles_ruta(datos['df_nodos'])
                
                print(f"--- ITERACIÓN {iteracion} - NUEVO MEJOR GLOBAL ENCONTRADO ---")
                print(f"Costo Global (Distancia Total): {mejor_solucion.costo_global:.2f} km\n")
                
                for detalle in detalles:
                    print(f"| Ruta Combustible: {detalle['costo_combustible']:.2f} | Ruta Distancia: {detalle['distancia']:.2f} km | Ruta: {detalle['ruta_descriptiva']}")
                print("-" * 50)
            
            if iteracion % 500 == 0:
                 print(f"Progreso: Iteración {iteracion}, Temperatura: {T:.4f}, Mejor Costo: {mejor_solucion.costo_global:.2f}")

        # enfriamiento
        T *= params['tasa_enfriamiento']
        
    return mejor_solucion