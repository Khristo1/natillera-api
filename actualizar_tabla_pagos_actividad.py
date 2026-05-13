# actualizar_tabla_pagos_actividad.py
import sqlite3

db_path = r"C:\Users\Khrist01\Documents\practicas sena\natillera_1.0\natillera.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar columnas existentes
cursor.execute("PRAGMA table_info(pagos_actividad)")
columnas = [col[1] for col in cursor.fetchall()]

# Agregar columnas si no existen
if 'mes' not in columnas:
    cursor.execute("ALTER TABLE pagos_actividad ADD COLUMN mes TEXT")
    print("✓ Columna 'mes' agregada")

if 'año' not in columnas:
    cursor.execute("ALTER TABLE pagos_actividad ADD COLUMN año INTEGER")
    print("✓ Columna 'año' agregada")

if 'forma_pago' not in columnas:
    cursor.execute("ALTER TABLE pagos_actividad ADD COLUMN forma_pago TEXT DEFAULT 'Efectivo'")
    print("✓ Columna 'forma_pago' agregada")

if 'observaciones' not in columnas:
    cursor.execute("ALTER TABLE pagos_actividad ADD COLUMN observaciones TEXT")
    print("✓ Columna 'observaciones' agregada")

conn.commit()
conn.close()

print("\n✅ Tabla actualizada correctamente")