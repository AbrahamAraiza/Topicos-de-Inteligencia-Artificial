import sqlite3
import easyocr
import cv2
import numpy as np
import os

# configuración global
DB_NAME = 'placas_culiacan.db'
# se inicializa el lector de EasyOCR una sola vez para eficiencia
# usaremos 'en' (inglés) para los caracteres alfanuméricos de la placa
READER = easyocr.Reader(['en'], gpu=False) 
# EasyOCR se inicializa con gpu=True si está disponible 

# fase 1: base de datos y vinculación

def crear_conexion():
    """conexión a la base de datos"""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"ERROR BD: no se pudo conectar a la base de datos {DB_NAME} {e}")
        return None

def buscar_propietario_por_placa(conn, placa):
    """
    busca los datos del propietario y vehículo a partir de una placa normalizada
    
        conn (sqlite3.Connection): conexión activa a la BD
        placa (str): el número de placa detectado (ejemplo: 'VNH535D')
        
    returns:
        tuple or None: datos del propietario y vehículo si se encuentra
    """
    cursor = conn.cursor()
    
    # normalización del texto de la placa removiendo cualquier caracter
    placa_normalizada = placa.upper().strip()
    
    # consulta usando JOIN para obtener datos del vehículo y propietario
    consulta = f"""
        SELECT 
            P.nombre, P.telefono, P.direccion,
            V.num_placa, V.marca, V.modelo, V.anio
        FROM 
            Vehiculos V
        JOIN 
            Propietarios P ON V.id_propietario = P.id_propietario
        WHERE 
            REPLACE(REPLACE(V.num_placa, '-', ''), ' ', '') = ?
    """
    
    cursor.execute(consulta, (placa_normalizada,))
    resultado = cursor.fetchone() 

    return resultado

# fase 2: detección de la placa

def limpiar_placa(texto):
    """limpia el texto detectado, dejando solo alfanuméricos"""
    # filtra y convierte a mayúsculas
    return ''.join(filter(str.isalnum, texto)).upper()

def detectar_placa_en_imagen(ruta_imagen):
    """
    procesa la imagen, detecta la placa usando EasyOCR y devuelve el texto limpio
    
        ruta_imagen (str): ruta al archivo de imagen
        
    returns:
        str or None: placa detectada limpia (ejemplo: 'VNH535D') o None si falla
    """
    if not os.path.exists(ruta_imagen):
        print(f"ERROR: archivo no encontrado en la ruta: {ruta_imagen}")
        return None
        
    try:
        # cargar imagen
        img = cv2.imread(ruta_imagen)
        # convertir a RGB (ya que EasyOCR funciona mejor con RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"ERROR CV: no se pudo cargar o procesar la imagen{e}")
        return None

    # realizar el reconocimiento
    resultados = READER.readtext(img_rgb)
    
    # heurística para seleccionar el mejor resultado (el más grande y confiable)
    placa_detectada_final = None
    mayor_area = 0
    
    for (bbox, texto, confianza) in resultados:
        texto_limpio = limpiar_placa(texto)
        
        # filtro: las placas de sinaloa comúnmente tienen 7 o 8 caracteres (ej. VNH-535-D)
        if 6 <= len(texto_limpio) <= 9: 
            # calcular el área aproximada del cuadro delimitador (bounding box)
            ancho = abs(bbox[1][0] - bbox[0][0])
            alto = abs(bbox[2][1] - bbox[0][1])
            area = ancho * alto
            
            if area > mayor_area:
                mayor_area = area
                placa_detectada_final = texto_limpio

    return placa_detectada_final

# funcion principal del sistema

def ejecutar_sistema():
    """ejecuta el flujo completo: detección -> vinculación -> salida"""
    
    print("\n[--- SISTEMA DE DETECCIÓN DE PLACAS VEHICULARES---]")
    
    # 1. solicitar la entrada al usuario
    ruta_imagen = input("ingrese la ruta completa del archivo de imagen de la placa (ejemplo: carro 1.jpg): ")
    
    # 2. detección de la placa
    print("\n[1] analizando imagen y detectando placa...")
    placa_limpia = detectar_placa_en_imagen(ruta_imagen)
    
    if not placa_limpia:
        print("DETECCIÓN FALLIDA: no se pudo identificar una placa válida en la imagen")
        return
        
    print(f"ÉXITO DE DETECCIÓN: placa identificada como -> {placa_limpia}")
    
    # 3. vinculación con la base de datos
    print("\n[2] consultando base de datos (placas_culiacan.db)...")
    conn = crear_conexion()
    
    if conn:
        datos_propietario = buscar_propietario_por_placa(conn, placa_limpia)
        conn.close()
        
        # generación de salida
        print("\n[--- RESULTADO DE LA VINCULACIÓN ---]")
        
        if datos_propietario:
            # desempaquetar los datos para una salida limpia
            nombre, telefono, direccion, num_placa, marca, modelo, anio = datos_propietario
            
            print(f"COINCIDENCIA ENCONTRADA: Placa {num_placa}")
            print("--- DATOS DEL PROPIETARIO ---")
            print(f"Nombre: {nombre}")
            print(f"Teléfono: {telefono}")
            print(f"Dirección: {direccion}")
            print("--- DATOS DEL VEHÍCULO ---")
            print(f"Vehículo: {marca} {modelo} ({anio})")
            
        else:
            print(f"PLACA NO REGISTRADA: la placa {placa_limpia} fue detectada pero no se encontró en la base de datos")
            print("  acción requerida: registrar el vehículo y propietario")
            
    else:
        print("ERROR CRÍTICO: no se pudo establecer conexión con la base de datos")


if __name__ == "__main__":
    ejecutar_sistema()