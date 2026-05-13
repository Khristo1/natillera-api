# actualizar_bd.py
import sqlite3
import os

def actualizar_base_datos():
    # Ruta de tu base de datos
    db_path = "C:\\Users\\Khrist01\\Documents\\practicas sena\\natillera_1.0\\natillera.db"
    
    # Verificar si existe
    if not os.path.exists(db_path):
        print(f"Base de datos no encontrada en: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar qué columnas existen actualmente
    cursor.execute("PRAGMA table_info(prestamos)")
    columnas = [col[1] for col in cursor.fetchall()]
    
    print("Columnas actuales en tabla prestamos:")
    for col in columnas:
        print(f"  - {col}")
    
    # Agregar columnas faltantes
    if 'tipo_cuota' not in columnas:
        print("\nAgregando columna 'tipo_cuota'...")
        cursor.execute("ALTER TABLE prestamos ADD COLUMN tipo_cuota TEXT DEFAULT 'Mensual'")
        print("✓ Columna 'tipo_cuota' agregada")
    
    if 'saldo_pendiente' not in columnas:
        print("Agregando columna 'saldo_pendiente'...")
        cursor.execute("ALTER TABLE prestamos ADD COLUMN saldo_pendiente REAL DEFAULT 0")
        print("✓ Columna 'saldo_pendiente' agregada")
        
        # Actualizar saldos existentes
        cursor.execute("UPDATE prestamos SET saldo_pendiente = monto_prestado WHERE saldo_pendiente = 0")
        print("✓ Saldos actualizados")
    
    if 'abonos_extraordinarios' not in columnas:
        print("Agregando columna 'abonos_extraordinarios'...")
        cursor.execute("ALTER TABLE prestamos ADD COLUMN abonos_extraordinarios REAL DEFAULT 0")
        print("✓ Columna 'abonos_extraordinarios' agregada")
    
    # Crear tabla pagos_prestamo si no existe
    cursor.execute("""
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
            FOREIGN KEY (id_prestamo) REFERENCES prestamos(id_prestamo)
        )
    """)
    print("\n✓ Tabla 'pagos_prestamo' verificada/creada")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("ACTUALIZACIÓN COMPLETADA")
    print("="*50)

if __name__ == "__main__":
    actualizar_base_datos()
    input("\nPresiona Enter para salir...")