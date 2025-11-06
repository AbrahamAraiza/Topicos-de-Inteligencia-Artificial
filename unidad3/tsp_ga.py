import random
import math
import matplotlib.pyplot as plt # Necesario para la visualización

# ----------------------------------------------------
# 1. CLASE CIUDAD (Entidad)
# ----------------------------------------------------
class Ciudad:
    """Representa una ciudad con coordenadas (x, y)."""
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def distancia_a(self, otra_ciudad):
        """Calcula la distancia Euclidiana entre dos ciudades."""
        dx = self.x - otra_ciudad.x
        dy = self.y - otra_ciudad.y
        return math.sqrt(dx**2 + dy**2)

    def __repr__(self):
        return f"C{self.id}"

# ----------------------------------------------------
# 2. CLASE RUTA (Cromosoma)
# ----------------------------------------------------
class Ruta:
    """Representa un cromosoma (una posible solución o ruta)."""
    def __init__(self, ruta):
        self.ruta = ruta # Lista de objetos Ciudad
        self.distancia = 0
        self.aptitud = 0

    def calcular_distancia(self):
        """Calcula la distancia total de la ruta (ciclo cerrado)."""
        if self.distancia == 0:
            distancia_total = 0
            for i in range(len(self.ruta)):
                ciudad_origen = self.ruta[i]
                # Vuelve a la primera ciudad para cerrar el ciclo
                ciudad_destino = self.ruta[(i + 1) % len(self.ruta)] 
                distancia_total += ciudad_origen.distancia_a(ciudad_destino)
            self.distancia = distancia_total
        return self.distancia

    def calcular_aptitud(self):
        """Calcula la aptitud (inverso de la distancia)."""
        if self.aptitud == 0:
            self.aptitud = 1 / self.calcular_distancia()
        return self.aptitud

# ----------------------------------------------------
# 3. CLASE ALGORITMOGENETICO (Motor del AG)
# ----------------------------------------------------
class AlgoritmoGenetico:
    def __init__(self, ciudades_maestras, tamano_poblacion, tasa_mutacion):
        self.ciudades = ciudades_maestras
        self.tamano_poblacion = tamano_poblacion
        self.tasa_mutacion = tasa_mutacion

    def crear_poblacion_inicial(self):
        """Genera la población inicial con rutas aleatorias."""
        poblacion = []
        for _ in range(self.tamano_poblacion):
            ruta_aleatoria = self.ciudades[:] 
            random.shuffle(ruta_aleatoria)
            nueva_ruta = Ruta(ruta_aleatoria)
            nueva_ruta.calcular_aptitud()
            poblacion.append(nueva_ruta)
        return poblacion

    def seleccion_torneo(self, poblacion, tamano_torneo=3):
        """Selecciona al individuo más apto de un subgrupo aleatorio."""
        # Usa random.sample para elegir rutas únicas para el torneo
        torneo = random.sample(poblacion, tamano_torneo)
        # Retorna la ruta con la aptitud más alta
        ganador = max(torneo, key=lambda ruta: ruta.aptitud) 
        return ganador

    def cruce_ox(self, padre1: Ruta, padre2: Ruta):
        """Cruce de Orden (OX) para mantener la validez de la ruta."""
        ruta_hijo = [None] * len(self.ciudades)

        corte1 = random.randint(0, len(self.ciudades) - 1)
        corte2 = random.randint(0, len(self.ciudades) - 1)
        if corte1 > corte2: corte1, corte2 = corte2, corte1

        # 1. Herencia directa del Padre 1
        ruta_hijo[corte1:corte2 + 1] = padre1.ruta[corte1:corte2 + 1]

        # 2. Herencia de orden del Padre 2
        ciudades_heredadas = {ciudad.id for ciudad in ruta_hijo if ciudad is not None}
        p2_indice = 0
        for i in range(len(self.ciudades)):
            if ruta_hijo[i] is None:
                while padre2.ruta[p2_indice].id in ciudades_heredadas:
                    p2_indice += 1

                ruta_hijo[i] = padre2.ruta[p2_indice]
                p2_indice += 1

        return Ruta(ruta_hijo)

    def mutacion_swap(self, ruta: Ruta):
        """Mutación de Intercambio (Swap Mutation)."""
        if random.random() < self.tasa_mutacion:
            idx1, idx2 = random.sample(range(len(self.ciudades)), 2)

            # Intercambio
            ruta.ruta[idx1], ruta.ruta[idx2] = ruta.ruta[idx2], ruta.ruta[idx1]

            # Resetear aptitud y distancia para forzar el recálculo
            ruta.distancia = 0
            ruta.aptitud = 0

# ----------------------------------------------------
# 4. FUNCIÓN DE EJECUCIÓN PRINCIPAL (Coordina el ciclo)
# ----------------------------------------------------
def ejecutar_ga(ciudades_data, tamano_poblacion, generaciones, tasa_mutacion):
    ciudades = [Ciudad(id + 1, x, y) for id, (x, y) in enumerate(ciudades_data)]

    solver = AlgoritmoGenetico(ciudades, tamano_poblacion, tasa_mutacion)

    poblacion = solver.crear_poblacion_inicial()
    mejor_ruta_global = max(poblacion, key=lambda ruta: ruta.aptitud)
    historial_distancia = [mejor_ruta_global.distancia]

    print("--- Iniciando Algoritmo Genético ---")

    for gen in range(generaciones):
        nueva_poblacion = []

        # Elitismo: Mantener al mejor individuo (el más apto)
        nueva_poblacion.append(mejor_ruta_global)

        while len(nueva_poblacion) < tamano_poblacion:
            # Selección, Cruce y Mutación
            padre1 = solver.seleccion_torneo(poblacion)
            padre2 = solver.seleccion_torneo(poblacion)
            hijo = solver.cruce_ox(padre1, padre2)
            solver.mutacion_swap(hijo)

            # Evaluación
            hijo.calcular_aptitud()
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

        # Actualizar mejor ruta global
        mejor_ruta_actual = max(poblacion, key=lambda ruta: ruta.aptitud)
        if mejor_ruta_actual.distancia < mejor_ruta_global.distancia:
            mejor_ruta_global = mejor_ruta_actual

        historial_distancia.append(mejor_ruta_global.distancia)

        if gen % 100 == 0:
            print(f"Generación {gen}: Distancia Óptima = {mejor_ruta_global.distancia:.2f}")

    return mejor_ruta_global, historial_distancia

# ----------------------------------------------------
# 5. CONFIGURACIÓN, EJECUCIÓN Y REPORTE FINAL
# ----------------------------------------------------
if __name__ == '__main__':
    # Definir las coordenadas de las ciudades (ejemplo de 10 ciudades)
    ciudades_coords = [
        (60, 200), (180, 200), (80, 180), (140, 180), (20, 160),
        (100, 160), (200, 160), (140, 140), (40, 120), (100, 120)
    ]

    # Parámetros del AG
    TAMANO_POBLACION = 100
    GENERACIONES = 2000
    TASA_MUTACION = 0.05

    # Ejecutar el algoritmo
    ruta_optima, historial = ejecutar_ga(
        ciudades_coords, TAMANO_POBLACION, GENERACIONES, TASA_MUTACION
    )

    # ----------------------------------------------------
    # REPORTE Y VISUALIZACIÓN
    # ----------------------------------------------------
    print("\n==============================================")
    print("✅ Algoritmo Terminado. Resultados Finales")
    print("==============================================")
    print(f"Distancia Final: {ruta_optima.distancia:.2f}")

    ruta_final = ruta_optima.ruta
    secuencia_ids = [c.id for c in ruta_final]
    print(f"Ruta: {secuencia_ids} -> {ruta_final[0].id}")

    # Preparar datos para el gráfico de Matplotlib
    x_coords = [c.x for c in ruta_final] + [ruta_final[0].x]
    y_coords = [c.y for c in ruta_final] + [ruta_final[0].y]

    plt.figure(figsize=(12, 5))

    # Gráfico 1: Ruta Óptima
    plt.subplot(1, 2, 1)
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='blue')
    plt.scatter(x_coords[:-1], y_coords[:-1], color='red', s=50)
    for i, ciudad in enumerate(ruta_final):
        plt.annotate(ciudad.id, (ciudad.x, ciudad.y), textcoords="offset points", xytext=(0,10), ha='center')
    plt.title("Ruta Óptima del Vendedor Viajero")

    # Gráfico 2: Progreso de Convergencia
    plt.subplot(1, 2, 2)
    plt.plot(historial, color='orange')
    plt.title("Progreso de la Distancia")
    plt.xlabel("Generación")
    plt.ylabel("Mejor Distancia")

    plt.tight_layout()
    plt.show()