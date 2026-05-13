# modulos/database.py
import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path=None):
        """
        Inicializa la conexion a la base de datos
        """
        if db_path is None:
            self.db_path = self.get_default_db_path()
        else:
            self.db_path = db_path
        
        self.connection = None
        self.cursor = None
        
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.connect()
        self.create_tables()
        print(f"[OK] Base de datos conectada: {self.db_path}")

    def formatear_monto(self, monto):
        """Formatea un monto con separador de miles"""
        try:
            return f"${float(monto):,.2f}"
        except:
            return "$0.00"
    
    def get_default_db_path(self):
        """Obtiene la ruta por defecto de la base de datos (raiz del proyecto)"""
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, 'natillera.db')
    
    def connect(self):
        """Conectar a la base de datos - Configuración para múltiples hilos"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
            print(f"[OK] Conexion establecida a {self.db_path}")
        except Exception as e:
            print(f"[ERROR] Conectando a la base de datos: {e}")
            raise
    
    def create_tables(self):
        """Crear tablas si no existen"""
        try:
            # Tabla de socios
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS socios (
                    id_socio INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_socio TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    cedula TEXT UNIQUE NOT NULL,
                    celular TEXT NOT NULL,
                    correo TEXT,
                    fecha_ingreso DATE DEFAULT CURRENT_DATE,
                    estado TEXT DEFAULT 'activo',
                    direccion TEXT,
                    ciudad TEXT,
                    observaciones TEXT
                )
            """)
            
            # Tabla de aportes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS aportes (
                    id_aporte INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_socio INTEGER NOT NULL,
                    monto REAL NOT NULL,
                    mes TEXT NOT NULL,
                    año INTEGER NOT NULL,
                    fecha_aporte DATE DEFAULT CURRENT_DATE,
                    estado TEXT DEFAULT 'pagado',
                    forma_pago TEXT DEFAULT 'efectivo',
                    comprobante TEXT,
                    observaciones TEXT,
                    FOREIGN KEY (id_socio) REFERENCES socios(id_socio) ON DELETE CASCADE
                )
            """)
            
            # Tabla de prestamos (actualizada)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id_prestamo INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_socio INTEGER,
                    id_recomendador INTEGER,
                    monto_prestado REAL NOT NULL,
                    interes_mensual REAL NOT NULL,
                    cuota_mensual REAL NOT NULL,
                    tipo_cuota TEXT DEFAULT 'Mensual',
                    cuotas_totales INTEGER NOT NULL,
                    cuotas_restantes INTEGER NOT NULL,
                    saldo_pendiente REAL DEFAULT 0,
                    abonos_extraordinarios REAL DEFAULT 0,
                    fecha_prestamo DATE DEFAULT CURRENT_DATE,
                    fecha_proximo_pago DATE,
                    estado TEXT DEFAULT 'activo',
                    es_externo BOOLEAN DEFAULT FALSE,
                    nombre_externo TEXT,
                    garantia TEXT,
                    observaciones TEXT,
                    FOREIGN KEY (id_socio) REFERENCES socios(id_socio) ON DELETE SET NULL,
                    FOREIGN KEY (id_recomendador) REFERENCES socios(id_socio) ON DELETE SET NULL
                )
            """)
            
            # Tabla de pagos de prestamos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos_prestamo (
                    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_prestamo INTEGER NOT NULL,
                    monto_pagado REAL NOT NULL,
                    fecha_pago DATE DEFAULT CURRENT_DATE,
                    forma_pago TEXT,
                    abono_capital REAL DEFAULT 0,
                    interes_cancelado REAL DEFAULT 0,
                    saldo_restante REAL DEFAULT 0,
                    es_extraordinario INTEGER DEFAULT 0,
                    FOREIGN KEY (id_prestamo) REFERENCES prestamos(id_prestamo) ON DELETE CASCADE
                )
            """)
            
            # Tabla de actividades
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS actividades (
                    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_actividad TEXT NOT NULL,
                    descripcion TEXT,
                    fecha_actividad DATE NOT NULL,
                    fecha_limite DATE,
                    inversion_total REAL NOT NULL DEFAULT 0,
                    ganancias REAL DEFAULT 0,
                    estado TEXT DEFAULT 'planificada',
                    ubicacion TEXT,
                    responsable TEXT
                )
            """)
            
            # Tabla de pagos de actividades
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos_actividad (
                    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_actividad INTEGER NOT NULL,
                    id_socio INTEGER NOT NULL,
                    monto_pagado REAL NOT NULL,
                    fecha_pago DATE DEFAULT CURRENT_DATE,
                    estado TEXT DEFAULT 'pagado',
                    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad) ON DELETE CASCADE,
                    FOREIGN KEY (id_socio) REFERENCES socios(id_socio) ON DELETE CASCADE
                )
            """)
            
            # Tabla de configuracion
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT,
                    descripcion TEXT,
                    fecha_actualizacion DATE DEFAULT CURRENT_DATE
                )
            """)
            
            self.connection.commit()
            print("[OK] Tablas creadas/verificadas correctamente")
            
        except Exception as e:
            print(f"[ERROR] Creando tablas: {e}")
            raise
    
    def execute(self, query, params=None):
        """Ejecutar consulta (INSERT, UPDATE, DELETE)"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Ejecutando consulta: {e}")
            return False
    
    def fetch_all(self, query, params=None):
        """Obtener todos los resultados - DEVUELVE LISTA DE TUPLAS"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] Obteniendo datos: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """Obtener un solo resultado - DEVUELVE TUPLA"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] Obteniendo dato: {e}")
            return None
    
    def obtener_estadisticas(self):
        """Obtener estadisticas del sistema"""
        stats = {}
        
        try:
            # Total socios
            self.cursor.execute("SELECT COUNT(*) FROM socios")
            stats['socios'] = str(self.cursor.fetchone()[0])
            
            # Socios activos
            self.cursor.execute("SELECT COUNT(*) FROM socios WHERE estado = 'activo'")
            stats['socios_activos'] = str(self.cursor.fetchone()[0])
            
            # Aportes del mes
            meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                     5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                     9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
            mes_actual = meses[datetime.now().month]
            año_actual = datetime.now().year
            
            self.cursor.execute(
                "SELECT SUM(monto) FROM aportes WHERE mes = ? AND año = ? AND estado = 'pagado'",
                (mes_actual, año_actual)
            )
            resultado = self.cursor.fetchone()[0]
            stats['aportes_mes'] = f"${resultado:,.2f}" if resultado else "$0"
            
            # Fondo total
            self.cursor.execute("SELECT SUM(monto) FROM aportes WHERE estado = 'pagado'")
            resultado = self.cursor.fetchone()[0]
            stats['fondo_total'] = f"${resultado:,.2f}" if resultado else "$0"
            
            # Prestamos activos
            self.cursor.execute("SELECT COUNT(*) FROM prestamos WHERE estado = 'activo'")
            stats['prestamos_activos'] = str(self.cursor.fetchone()[0])
            
            # Prestamos vencidos
            self.cursor.execute("SELECT COUNT(*) FROM prestamos WHERE estado = 'vencido'")
            stats['prestamos_vencidos'] = str(self.cursor.fetchone()[0])
            
            # Actividades
            self.cursor.execute("SELECT COUNT(*) FROM actividades")
            stats['actividades'] = str(self.cursor.fetchone()[0])
            
            # Ganancias totales
            self.cursor.execute("SELECT SUM(ganancias) FROM actividades")
            resultado = self.cursor.fetchone()[0]
            stats['ganancias'] = f"${resultado:,.2f}" if resultado else "$0"
            
        except Exception as e:
            print(f"[ERROR] Obteniendo estadisticas: {e}")
            stats = {
                'socios': '0', 'socios_activos': '0', 'aportes_mes': '$0',
                'fondo_total': '$0', 'prestamos_activos': '0', 'prestamos_vencidos': '0',
                'actividades': '0', 'ganancias': '$0'
            }
        
        return stats
    
    def get_db_size(self):
        """Obtener tamaño de la base de datos en KB"""
        try:
            size_bytes = os.path.getsize(self.db_path)
            return round(size_bytes / 1024, 2)
        except:
            return 0
    
    def close(self):
        """Cerrar conexion"""
        if self.connection:
            self.connection.close()
            print("[INFO] Conexion cerrada")
            