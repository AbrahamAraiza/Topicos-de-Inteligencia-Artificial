import random
import numpy as np
import pandas as pd
import operator
from typing import List, Tuple, Dict, Any

# clase para representar un municipio (o ciudad) con coordenadas (x, y)
# (representa una ciudad o punto en la ruta)
class municipio:
    def __init__(self, x: float, y: float):
        self.x = x  # coordenada X
        self.y = y  # coordenada Y
    
    def distancia(self, otro_municipio: 'municipio') -> float:
        """calcula la distancia euclidiana (teorema de pitágoras) entre dos municipios"""
        xDis = abs(self.x - otro_municipio.x)
        yDis = abs(self.y - otro_municipio.y)
        distancia = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distancia

    def __repr__(self):
        """devuelve una representación en cadena de las coordenadas"""
        return f"({self.x},{self.y})"


# clase: aptitud (evalúa la calidad de una ruta)
class Aptitud:
    """clase para calcular la distancia total de una ruta y su aptitud (fitness)"""
    def __init__(self, ruta: List[municipio]):
        self.ruta = ruta
        self.distancia = 0
        self.f_aptitud = 0.0
    
    def distanciaRuta(self) -> float:
        """calcula la distancia total de la ruta, cerrando el ciclo (TSP)"""
        if self.distancia == 0:
            distanciaRelativa = 0
            for i in range(len(self.ruta)):
                puntoInicial = self.ruta[i]
                
                # Cierra el ciclo: si es el último punto, el destino es el primero.
                puntoFinal = self.ruta[i + 1] if i + 1 < len(self.ruta) else self.ruta[0]
                
                distanciaRelativa += puntoInicial.distancia(puntoFinal)
            
            self.distancia = distanciaRelativa
        return self.distancia
    
    def rutaApta(self) -> float:
        """Calcula el valor de aptitud (fitness), que es el inverso de la distancia"""
        if self.f_aptitud == 0:
            # aptitud = 1 / distancia (maximizar aptitud equivale a minimizar distancia)
            self.f_aptitud = 1 / float(self.distanciaRuta())
        return self.f_aptitud

# funciones auxiliares (independientes de los parámetros del algoritmo)

def crear_individuo(listaMunicipios: List[municipio]) -> List[municipio]:
    """crea una ruta aleatoria (un individuo) mediante una permutación"""
    # asegura que cada municipio se use exactamente una vez (codificación de orden)
    return random.sample(listaMunicipios, len(listaMunicipios))

def clasificacion_rutas(poblacion: List[List[municipio]]) -> List[Tuple[int, float]]:
    """evalúa la aptitud de cada individuo y los clasifica de mejor a peor"""
    fitnessResults: Dict[int, float] = {}
    for i in range(len(poblacion)):
        # calcula la aptitud para cada ruta y la almacena con su índice
        fitnessResults[i] = Aptitud(poblacion[i]).rutaApta()
    
    # rrdena la población de mayor a menor aptitud (reverse=true)
    return sorted(fitnessResults.items(), key=operator.itemgetter(1), reverse=True)


# ==============================================================================
# clase: AlgoritmoGenetico (encapsula el proceso principal)
# ==============================================================================
class AlgoritmoGenetico:
    """clase principal que gestiona el ciclo de vida del algoritmo"""
    
    def __init__(self, listaMunicipios: List[municipio], tamanoPoblacion: int, indivSelecionados: int, razonMutacion: float):
        self.listaMunicipios = listaMunicipios
        self.tamanoPoblacion = tamanoPoblacion
        self.indivSelecionados = indivSelecionados # N mejores pasan
        self.razonMutacion = razonMutacion       # tasa de mutación
        
    def poblacion_inicial(self) -> List[List[municipio]]:
        """genera la población inicial de rutas aleatorias"""
        poblacion: List[List[municipio]] = []
        for _ in range(self.tamanoPoblacion):
            poblacion.append(crear_individuo(self.listaMunicipios))
        return poblacion

    def seleccion_rutas(self, popRanked: List[Tuple[int, float]]) -> List[int]:
        """
        selecciona los individuos (índices) que serán padres usando elitismo y ruleta
        """
        resultadosSeleccion: List[int] = []
        
        df = pd.DataFrame(np.array(popRanked), columns=["Indice", "Aptitud"])
        df['cum_sum'] = df['Aptitud'].cumsum()
        df['cum_perc'] = 100 * df['cum_sum'] / df['Aptitud'].sum()
        
        # elitismo: los 'indivSelecionados' mejores pasan directamente
        for i in range(self.indivSelecionados):
            resultadosSeleccion.append(popRanked[i][0])
            
        # selección por ruleta: el resto se elige por probabilidad
        num_ruleta = len(popRanked) - self.indivSelecionados
        for _ in range(num_ruleta):
            seleccion = 100 * random.random()
            for i in range(len(popRanked)):
                if seleccion <= df.iat[i, 3]: # columna 'cum_perc'
                    resultadosSeleccion.append(popRanked[i][0])
                    break
        return resultadosSeleccion

    def grupo_apareamiento(self, poblacion: List[List[municipio]], resultadosSeleccion: List[int]) -> List[List[municipio]]:
        """recupera los objetos ruta de la población original para el cruce"""
        grupoApareamiento: List[List[municipio]] = [poblacion[index] for index in resultadosSeleccion]
        return grupoApareamiento

    def reproduccion(self, progenitor1: List[municipio], progenitor2: List[municipio]) -> List[municipio]:
        """
        realiza el cruce (reproducción) PMX (o similar) para el TSP
        hereda un segmento de P1 y rellena el resto con P2 para evitar duplicados
        """
        hijoP1: List[municipio] = []
        
        # 1- definir los puntos de corte aleatorios
        longitud = len(progenitor1)
        generacionX = int(random.random() * longitud)
        generacionY = int(random.random() * longitud)
        
        generacionInicial = min(generacionX, generacionY)
        generacionFinal = max(generacionX, generacionY)

        # 2- copiar el segmento del progenitor 1
        hijoP1.extend(progenitor1[generacionInicial:generacionFinal])
         
        # 3- rellenar el resto con los elementos de P2 que NO están en hijoP1
        hijoP2 = [item for item in progenitor2 if item not in hijoP1]

        # 4- combinar (segmento P1 + resto de P2)
        # la lógica original del código base combina de forma que el segmento de P1 
        # va primero, lo cual no respeta las posiciones originales de P2. 
        # se mantendra esta lógica simple para respetar el código base:
        hijo: List[municipio] = hijoP1 + hijoP2
        return hijo

    def reproduccion_poblacion(self, grupoApareamiento: List[List[municipio]]) -> List[List[municipio]]:
        """crea la nueva generación de hijos a partir del grupo de apareamiento"""
        hijos: List[List[municipio]] = []
        tamano_total = len(grupoApareamiento)
        num_a_cruzar = tamano_total - self.indivSelecionados
        
        # 1- los individuos elitistas pasan directamente (ya están al inicio del grupoApareamiento)
        for i in range(self.indivSelecionados):
            hijos.append(grupoApareamiento[i])
        
        # 2- cruce: el resto de la población se genera
        espacio = random.sample(grupoApareamiento, tamano_total) # baraja los padres disponibles
        
        for i in range(num_a_cruzar):
            # cruce de dos padres aleatorios
            hijo = self.reproduccion(espacio[i], espacio[tamano_total - i - 1])
            hijos.append(hijo)
        return hijos

    def mutacion(self, individuo: List[municipio]) -> List[municipio]:
        """aplica mutación por intercambio (swap) a un individuo"""
        longitud = len(individuo)
        for swapped in range(longitud):
            # la mutación ocurre con una probabilidad 'razonMutacion'
            if random.random() < self.razonMutacion:
                swapWith = int(random.random() * longitud) # elige una posición aleatoria
                
                # realiza el intercambio (swap)
                individuo[swapped], individuo[swapWith] = individuo[swapWith], individuo[swapped]
        return individuo

    def mutacion_poblacion(self, poblacion: List[List[municipio]]) -> List[List[municipio]]:
        """aplica la mutación a toda la población de hijos"""
        pobMutada: List[List[municipio]] = []
        for ind in poblacion:
            # pasa cada individuo a la función de mutación
            pobMutada.append(self.mutacion(ind))
        return pobMutada

    def nueva_generacion(self, generacionActual: List[List[municipio]]) -> List[List[municipio]]:
        """crea la siguiente generación aplicando todos los pasos del algoritmo"""
        # 1- clasificar rutas por aptitud (fitness)
        popRanked = clasificacion_rutas(generacionActual)

        # 2- selección de los candidatos (elitismo + ruleta)
        selectionResults = self.seleccion_rutas(popRanked)

        # 3- generar grupo de apareamiento (recuperar los objetos ruta)
        grupoApa = self.grupo_apareamiento(generacionActual, selectionResults)

        # 4- generación de la población cruzada (crossover)
        hijos = self.reproduccion_poblacion(grupoApa)

        # 5. incluir las mutaciones en la nueva generación 
        nuevaGeneracion = self.mutacion_poblacion(hijos)

        return nuevaGeneracion

    def ejecutar_algoritmo(self, generaciones: int) -> List[municipio]:
        """bucle principal del algoritmo genético"""
        
        # 1- inicializar población
        pop = self.poblacion_inicial()
        
        # muestra la mejor distancia de la población inicial
        mejor_aptitud_inicial = clasificacion_rutas(pop)[0][1]
        print(f"distancia inicial: {1 / mejor_aptitud_inicial:.2f}")
        
        # 2- iterar a través de las generaciones
        for i in range(generaciones):
            pop = self.nueva_generacion(pop)
            
            # opcional: imprimir el progreso cada N generaciones
            if (i + 1) % 100 == 0:
                mejor_aptitud_actual = clasificacion_rutas(pop)[0][1]
                print(f"generación {i + 1}: mejor distancia = {1 / mejor_aptitud_actual:.2f}")

        # 3- resultados finales
        mejor_aptitud_final = clasificacion_rutas(pop)[0][1]
        print(f"distancia final: {1 / mejor_aptitud_final:.2f}")
        
        # obtener la ruta final
        bestRouteIndex = clasificacion_rutas(pop)[0][0]
        mejorRuta = pop[bestRouteIndex]
        
        return mejorRuta

# ==============================================================================
# SECCIÓN DE PRUEBAS
# ==============================================================================

def ejecutar_casos_prueba():
    """ejecuta y valida las funciones críticas del algoritmo genético."""

    print("\n" + "="*50)
    print("      CASOS DE PRUEBA FORMALES")
    print("="*50)

    # preparaciónd e datos simples (para cálculo manual)
    # distancias: d(A,B)=3, d(B,C)=5, d(C,A)=4. distancia total del ciclo: 12.0
    mun_A = municipio(0, 0)
    mun_B = municipio(3, 0)
    mun_C = municipio(0, 4)
    ruta_prueba = [mun_A, mun_B, mun_C]
    
    print("\n1- caso de prueba: clase aptitud (fitness)")

    # ----------------------------------------------------------------------
    # prueba C1.1 y C1.2: validación de la distancia y aptitud
    # ----------------------------------------------------------------------
    aptitud_test = Aptitud(ruta_prueba)
    distancia_calculada = aptitud_test.distanciaRuta()
    aptitud_calculada = aptitud_test.rutaApta()
    
    distancia_esperada = 12.0
    aptitud_esperada = 1.0 / 12.0
    
    print(f"ruta de prueba: {ruta_prueba}")
    print(f"distancia calculada (C1.1): {distancia_calculada:.2f}")
    print(f"aptitud calculada (C1.2): {aptitud_calculada:.4f}")
    
    # comprobación de la prueba (usando numpy.isclose por seguridad con floats)
    if np.isclose(distancia_calculada, distancia_esperada):
        print("-> C1.1 pasó: La distancia es correcta (esperado 12.00)")
    else:
        print(f"-> C1.1 falló: esperado {distancia_esperada}, obtenido {distancia_calculada}")

    if np.isclose(aptitud_calculada, aptitud_esperada):
        print("-> C1.2 pasó: la aptitud es correcta (esperado 0.0833)")
    else:
        print(f"-> C1.2 falló: esperado {aptitud_esperada:.4f}, obtenido {aptitud_calculada:.4f}")

    print("-" * 50)

    print("\n2- caso de prueba: cruce (reproduccion)")

    # ----------------------------------------------------------------------
    # prueba C2.1: validación del cruce - validez de la permutación
    # ----------------------------------------------------------------------
    P1 = [mun_A, mun_B, mun_C] # [A, B, C]
    P2 = [mun_C, mun_A, mun_B] # [C, A, B]
    
    # creamos un objeto AG solo para usar el método de reproducción
    ag_tester = AlgoritmoGenetico(P1, tamanoPoblacion=1, indivSelecionados=0, razonMutacion=0)
    hijo = ag_tester.reproduccion(P1, P2)
    
    print(f"progenitor 1: {P1}")
    print(f"progenitor 2: {P2}")
    print(f"hijo generado:  {hijo}")
    
    # validación: el hijo debe tener la misma longitud y mismos elementos que los padres
    municipios_unicos_hijo = set(hijo)
    municipios_originales = set(P1)
    
    if municipios_unicos_hijo == municipios_originales and len(hijo) == len(P1):
        print("-> C2.1 pasó: el cruce generó un hijo válido (sin duplicados/pérdidas)")
    else:
        print("-> C2.1 falló: el hijo no es una permutación válida")
    
    print("-" * 50)
    
    print("\n3- caso de prueba: mutación")

    # ----------------------------------------------------------------------
    # prueba C3.1: validación de mutación al 100% (swap mutation)
    # ----------------------------------------------------------------------
    individuo_prueba = [mun_A, mun_B, mun_C]
    individuo_original = list(individuo_prueba) # copia de la lista
    
    # aplicar mutación al 100% (debería haber al menos un intercambio)
    individuo_mutado = ag_tester.mutacion(individuo_prueba)
    
    print(f"individuo Original: {individuo_original}")
    print(f"individuo Mutado:   {individuo_mutado}")
    
    # la prueba pasa si el individuo cambia Y sigue siendo una permutación válida
    es_diferente = individuo_original != individuo_mutado
    es_valido = set(individuo_mutado) == set(individuo_original)
    
    if es_diferente and es_valido:
        print("-> C3.1 pasó: el individuo cambió y sigue siendo una ruta válida")
    else:
        print("-> C3.1 falló: no hubo mutación o la ruta dejó de ser válida")
    
    print("-" * 50)

    print("\n" + "="*50)
    print("      FIN DE CASOS DE PRUEBA FORMALES")
    print("="*50)


# ==============================================================================
# EJECUCIÓN PRINCIPAL DEL CÓDIGO
# ==============================================================================

if __name__ == '__main__':
    
    # 1- ejecución de las pruebas
    ejecutar_casos_prueba()
    
    # 2- definición de las ciudades reales
    ciudades_coordenadas = [
        municipio(x=40.4168, y=-3.7038),   # Madrid
        municipio(x=41.3851, y=2.1734),    # Barcelona
        municipio(x=39.4699, y=-0.3774),   # Valencia
        municipio(x=43.2630, y=-2.9350),   # Bilbao
        municipio(x=40.8286, y=-3.1601),   # Guadalajara
        municipio(x=37.3891, y=-5.9845)    # Sevilla (añadida para tener más de 5)
    ]

    print("\n" + "="*50)
    print("  INICIO DEL ALGORITMO GENÉTICO PRINCIPAL")
    print("="*50)
    
    # 3- creación e inicio del algortimo
    AG = AlgoritmoGenetico(
        listaMunicipios=ciudades_coordenadas, 
        tamanoPoblacion=100, 
        indivSelecionados=20, 
        razonMutacion=0.01
    )
    
    mejor_ruta = AG.ejecutar_algoritmo(generaciones=500)

    print("\nmejor ruta encontrada (coordenadas):")
    print(mejor_ruta)