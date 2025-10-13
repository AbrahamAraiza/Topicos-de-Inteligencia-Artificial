from utils import calcular_distancia_ruta
from data_loader import FACTOR_COMBUSTIBLE_POR_KM

class Solucion:
    """Representa un conjunto completo de rutas para el MDVRP."""
    def __init__(self, rutas, matriz_distancia, matriz_costo):
        # rutas es una lista donde cada elemento es una lista de IDs de nodos:
        # [[CD_ID, T1_ID, T2_ID, ..., CD_ID], [CD_ID, T3_ID, ..., CD_ID], ...]
        self.rutas = rutas 
        self.matriz_distancia = matriz_distancia
        self.matriz_costo = matriz_costo
        self.costo_global = self.evaluar_costo_global()

    def evaluar_costo_global(self):
        """
        Calcula el costo global de la solución (minimiza la Distancia Total en km).
        """
        costo_total = 0
        for ruta in self.rutas:
            # el costo que minimizamos es la distancia total en km.
            costo_total += calcular_distancia_ruta(ruta, self.matriz_distancia)
            
        return costo_total

    def obtener_detalles_ruta(self, df_nodos):
        """Devuelve una lista de diccionarios con los detalles de cada ruta."""
        detalles = []
        for i, ruta_ids in enumerate(self.rutas):
            if len(ruta_ids) < 2: # ruta vacía o solo un nodo
                continue
                
            distancia = calcular_distancia_ruta(ruta_ids, self.matriz_distancia)
            costo_combustible = distancia * FACTOR_COMBUSTIBLE_POR_KM
            
            # obtener los nombres descriptivos
            nombres = df_nodos.set_index('ID_NUMERICO').loc[ruta_ids]['Nombre'].tolist()
            ruta_descriptiva = " -> ".join(nombres)
            
            detalles.append({
                'id_cd': ruta_ids[0],
                'ruta_descriptiva': ruta_descriptiva,
                'distancia': distancia,
                'costo_combustible': costo_combustible
            })
        return detalles