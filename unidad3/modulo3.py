import numpy as np
import matplotlib.pyplot as plt
import time

# =============================================================================
# 1. FUNCIÓN OBJETIVO: RASTRIGIN (Problema de Minimización)
# =============================================================================
def funcion_rastrigin(x):
    """
    Función de Rastrigin en N dimensiones (usaremos N=2).
    Mínimo global f(0, 0) = 0.
    """
    A = 10
    n = len(x)
    # Fórmula: A*n + Sumatoria(x^2 - A * cos(2*pi*x))
    return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))

# =============================================================================
# 2. ALGORITMO: OPTIMIZACIÓN DE ENJAMBRE DE PARTÍCULAS (PSO) - Parte 1
# =============================================================================
def pso_optimizacion(
    funcion_objetivo,
    NP=50,                  # Tamaño del Enjambre
    n_dimensiones=2,
    limites_inf_sup=[-5.12, 5.12],
    max_iteraciones=200,
    w=0.5,                  # Inercia
    c1=1.5,                 # Peso Cognitivo (personal)
    c2=1.5                  # Peso Social (global)
):
    min_limite, max_limite = limites_inf_sup
    
    # Inicialización
    posiciones = np.random.uniform(min_limite, max_limite, (NP, n_dimensiones))
    velocidades = np.random.uniform(-1, 1, (NP, n_dimensiones))
    
    p_best_posiciones = posiciones.copy()
    p_best_aptitudes = np.array([funcion_objetivo(p) for p in p_best_posiciones])
    
    mejor_indice = np.argmin(p_best_aptitudes)
    g_best_posicion = p_best_posiciones[mejor_indice].copy()
    g_best_aptitud = p_best_aptitudes[mejor_indice]
    
    historial_g_best_aptitud = [g_best_aptitud]
    
    # Bucle de Iteraciones
    for t in range(max_iteraciones):
        for i in range(NP):
            # 2a. Evaluación y actualización de p_best
            aptitud_actual = funcion_objetivo(posiciones[i])
            
            if aptitud_actual < p_best_aptitudes[i]:
                p_best_aptitudes[i] = aptitud_actual
                p_best_posiciones[i] = posiciones[i].copy()
                
                # Actualización de g_best
                if aptitud_actual < g_best_aptitud:
                    g_best_aptitud = aptitud_actual
                    g_best_posicion = posiciones[i].copy()

            # 2b. Actualización de Velocidad
            r1 = np.random.rand(n_dimensiones)
            r2 = np.random.rand(n_dimensiones)
            
            inercia = w * velocidades[i]
            cognitivo = c1 * r1 * (p_best_posiciones[i] - posiciones[i])
            social = c2 * r2 * (g_best_posicion - posiciones[i])
            
            velocidades[i] = inercia + cognitivo + social

            # 2c. Actualización de Posición y límites
            posiciones[i] = posiciones[i] + velocidades[i]
            posiciones[i] = np.clip(posiciones[i], min_limite, max_limite)
            
        historial_g_best_aptitud.append(g_best_aptitud)
    
    return g_best_posicion, g_best_aptitud, historial_g_best_aptitud

# =============================================================================
# 3. ALGORITMO: EVOLUCIÓN DIFERENCIAL (DE/rand/1/bin) - Parte 2
# =============================================================================
def de_optimizacion(
    funcion_objetivo,
    NP=50, 
    n_dimensiones=2,
    limites_inf_sup=[-5.12, 5.12],
    max_iteraciones=200,
    F=0.8,  # Factor de Escala (Mutación)
    CR=0.9  # Probabilidad de Cruce
):
    min_limite, max_limite = limites_inf_sup
    
    # Inicialización de la Población
    poblacion = np.random.uniform(min_limite, max_limite, (NP, n_dimensiones))
    aptitudes = np.array([funcion_objetivo(p) for p in poblacion])
    
    mejor_indice = np.argmin(aptitudes)
    mejor_solucion = poblacion[mejor_indice].copy()
    mejor_aptitud = aptitudes[mejor_indice]
    
    historial_mejor_aptitud = [mejor_aptitud]
    
    # Bucle de Generaciones
    for t in range(max_iteraciones):
        nueva_poblacion = np.empty_like(poblacion)
        nuevas_aptitudes = np.empty_like(aptitudes)
        
        for i in range(NP):
            # 3a. Mutación (DE/rand/1)
            indices_posibles = [idx for idx in range(NP) if idx != i]
            # Seleccionar 3 índices distintos
            indices_rand = np.random.choice(indices_posibles, 3, replace=False)
            r1, r2, r3 = indices_rand
            
            # Vector Mutante: V = r1 + F * (r2 - r3)
            vector_mutante = poblacion[r1] + F * (poblacion[r2] - poblacion[r3])
            
            # 3b. Cruce (Binomial)
            vector_prueba = np.copy(poblacion[i])
            j_rand = np.random.randint(n_dimensiones)
            
            for j in range(n_dimensiones):
                # Cruce: si rand < CR O es la posición obligatoria (j_rand)
                if np.random.rand() < CR or j == j_rand:
                    vector_prueba[j] = vector_mutante[j]
            
            # Manejo de límites
            vector_prueba = np.clip(vector_prueba, min_limite, max_limite)
            
            # 3c. Selección
            aptitud_prueba = funcion_objetivo(vector_prueba)
            
            if aptitud_prueba <= aptitudes[i]:
                # El vector de prueba es mejor o igual: se acepta
                nueva_poblacion[i] = vector_prueba
                nuevas_aptitudes[i] = aptitud_prueba
                
                if aptitud_prueba < mejor_aptitud:
                    mejor_aptitud = aptitud_prueba
                    mejor_solucion = vector_prueba.copy()
            else:
                # El vector objetivo es mejor: se mantiene
                nueva_poblacion[i] = poblacion[i]
                nuevas_aptitudes[i] = aptitudes[i]

        poblacion = nueva_poblacion
        aptitudes = nuevas_aptitudes
        historial_mejor_aptitud.append(mejor_aptitud)

    return mejor_solucion, mejor_aptitud, historial_mejor_aptitud

# =============================================================================
# 4. EJECUCIÓN COMPARATIVA Y VISUALIZACIÓN
# =============================================================================
if __name__ == "__main__":
    
    # --- Parámetros Generales de Comparación ---
    NP_SIZE = 50
    MAX_GEN = 200
    
    print("\n=======================================================")
    print(f"   INICIANDO COMPARACIÓN DE ALGORITMOS (N={MAX_GEN} iteraciones)")
    print("=======================================================")
    
    # --- EJECUCIÓN PSO ---
    start_time_pso = time.time()
    best_pos_pso, best_apt_pso, hist_pso = pso_optimizacion(
        funcion_rastrigin, NP=NP_SIZE, max_iteraciones=MAX_GEN
    )
    end_time_pso = time.time()
    
    # --- EJECUCIÓN DE ---
    start_time_de = time.time()
    best_pos_de, best_apt_de, hist_de = de_optimizacion(
        funcion_rastrigin, NP=NP_SIZE, max_iteraciones=MAX_GEN
    )
    end_time_de = time.time()

    # --- RESULTADOS FINALES EN CONSOLA ---
    print("\n--- RESULTADOS FINALES DE OPTIMIZACIÓN ---")
    print(f"\n[PSO (Enjambre de Partículas)]")
    print(f"Mejor Mínimo F(X): {best_apt_pso:.8f}")
    print(f"Solución X: {best_pos_pso}")
    print(f"Tiempo de Cómputo: {end_time_pso - start_time_pso:.4f}s")
    
    print(f"\n[DE (Evolución Diferencial)]")
    print(f"Mejor Mínimo F(X): {best_apt_de:.8f}")
    print(f"Solución X: {best_pos_de}")
    print(f"Tiempo de Cómputo: {end_time_de - start_time_de:.4f}s")
    
    # --- GRÁFICO COMPARATIVO ---
    try:
        plt.figure(figsize=(10, 6))
        
        # PSO
        plt.plot(hist_pso, label=f'PSO (F(X) final: {best_apt_pso:.4f})', color='blue', linewidth=2)
        
        # DE
        plt.plot(hist_de, label=f'DE (F(X) final: {best_apt_de:.4f})', color='red', linestyle='--', linewidth=2)
        
        plt.title("Comparativa de Convergencia: PSO vs. Evolución Diferencial en Rastrigin")
        plt.xlabel("Generación/Iteración")
        plt.ylabel("Mejor Aptitud (Minimización)")
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.yscale('log') # Escala logarítmica para ver mejor la convergencia cerca de cero
        plt.show()
        
    except Exception as e:
        print(f"\n[ADVERTENCIA]: El cálculo fue exitoso, pero falló la visualización del gráfico. Error: {e}")
        print("Asegúrese de tener instaladas y configuradas las librerías gráficas de Matplotlib.")