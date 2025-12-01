import sqlite3

# definir la base de datos

DB_NAME = 'placas_culiacan.db'

def crear_conexion():
    """conexión a la base de datos SQLite"""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"error al conectar a la BD: {e}")
        return None

def crear_tablas(conn):
    """tablas de propietarios y vehiculos"""
    cursor = conn.cursor()
    
    # tabla 1: propietarios (datos personales)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Propietarios (
            id_propietario INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT,
            direccion TEXT
        );
    """)
    
    # tabla 2: vehiculos (datos del auto y la placa)
    # num_placa es UNIQUE para asegurar que no haya duplicados
    # id_propietario es la CLAVE FORÁNEA
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vehiculos (
            id_vehiculo INTEGER PRIMARY KEY,
            num_placa TEXT NOT NULL UNIQUE, 
            marca TEXT,
            modelo TEXT,
            anio INTEGER,
            id_propietario INTEGER,
            FOREIGN KEY (id_propietario) REFERENCES Propietarios (id_propietario)
        );
    """)
    
    conn.commit()
    print("tablas 'propietarios' y 'vehiculos' creadas o ya existentes")


# datos de prueba (simulación)

def insertar_datos_prueba(conn):
    """datos de prueba"""
    cursor = conn.cursor()

    # datos de propietarios
    propietarios_data = [
        ("Mario Pérez Hernandez", "6671234567", "Col. Centro, Culiacán, Sinaloa"),
        ("Sofia González Soto", "6675376543", "Col. Tierra Blanca, Culiacán, Sinaloa"),
        ("Juan Ramírez Díaz", "6672351212", "Col. Guadalupe, Culiacán, Sinaloa"),
        ("Fernando Santillan León", "6677926341", "Col. Morelos, Culiacán, Sinaloa"),
        ("Abraham Araiza Verdugo", "6672916274", "Col. Nuevo Culiacán, Culiacán, Sinaloa"),
    ]
    cursor.executemany("INSERT INTO Propietarios (nombre, telefono, direccion) VALUES (?, ?, ?)", propietarios_data)

    # datos de Vehículos (con placas de ejemplo de Sinaloa)
    vehiculos_data = [
        ("VNH535D", "HONDA HR-V", "SPORT", 2023, 1), # Mario Perez
        ("SIN5365A", "KIA", "OPTIMA", 2016, 2), # Sofia González
        ("SIN8051R", "HYUNDAI", "SONATA", 2014, 3), # Juan Ramírez
        ("VKD623D", "TOYOTA", "YARIS", 2021, 4), # Fernando Santillan
        ("VHM084A", "NISSAN", "KICKS", 2029, 5), # Abraham Araiza
    ]
    
    # la instrucción ON CONFLICT IGNORE evita que se detenga si ya existen las placas
    cursor.executemany(
        """INSERT OR IGNORE INTO Vehiculos (num_placa, marca, modelo, anio, id_propietario) 
           VALUES (?, ?, ?, ?, ?)""", 
        vehiculos_data
    )

    conn.commit()
    print("datos de prueba insertados (placas de Sinaloa simuladas)")


# funcion de vinculación

def buscar_propietario_por_placa(conn, placa):
    """
    busca los datos del propietario y vehículo a partir de una placa
    esta función simula la lógica del 'sistema de vinculación'
    """
    cursor = conn.cursor()
    
    # 1. normalizar la placa (ejemplo: VNH-535-D-> VHN535D)
    #placa_normalizada = placa.upper().strip().replace('-', '').replace(' ', '')
    placa_normalizada = placa.upper().strip()
    
    # usamos LIKE con comodines por si la normalización falla
    # y quitamos guiones/espacios de la consulta
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
    resultado = cursor.fetchone() # obtiene el primer resultado

    return resultado


# ejecución del setup

if __name__ == "__main__":
    conn = crear_conexion()
    if conn:
        crear_tablas(conn)
        # intentamos insertar datos, si la placa ya existe, SQLite lo ignora
        insertar_datos_prueba(conn) 
        
        print("\n--- PRUEBA DE LA LÓGICA DE VINCULACIÓN ---")
        
        # prueba 1: placa que existe y está normalizada
        placa_a_buscar_1 = "VNH535D"
        datos_1 = buscar_propietario_por_placa(conn, placa_a_buscar_1)
        
        if datos_1:
            print(f"éxito: Placa '{placa_a_buscar_1}' encontrada")
            print(f"Propietario: {datos_1[0]}, Vehículo: {datos_1[4]} {datos_1[5]}")
        else:
            print(f"fallo: Placa '{placa_a_buscar_1}' no encontrada")
            
        # prueba 2: placa con formato diferente (simula un resultado de OCR)
        placa_a_buscar_2 = "kua5678"
        datos_2 = buscar_propietario_por_placa(conn, placa_a_buscar_2)
        
        if datos_2:
            print(f"éxito: Placa '{placa_a_buscar_2}' (normalizada) encontrada")
            print(f"Propietario: {datos_2[0]}, Teléfono: {datos_2[1]}")
        else:
            print(f"fallo: Placa '{placa_a_buscar_2}' no encontrada")
            
        conn.close()
        print("\nbase de datos creada y lógica de búsqueda probada")