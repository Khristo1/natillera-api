# actualizar_tabla_prestamos.py
import sqlite3

db_path = "C:\\Users\\Khrist01\\Documents\\practicas sena\\natillera_1.0\\natillera.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar si la columna interes_mensual ya existe
cursor.execute("PRAGMA table_info(prestamos)")
columnas = [col[1] for col in cursor.fetchall()]

if 'interes_mensual' not in columnas:
    print("Agregando columna interes_mensual...")
    cursor.execute("ALTER TABLE prestamos ADD COLUMN interes_mensual REAL DEFAULT 10")
    print("✓ Columna interes_mensual agregada")
    
    # Copiar valores de la columna antigua 'interes' a la nueva si existe
    if 'interes' in columnas:
        cursor.execute("UPDATE prestamos SET interes_mensual = interes WHERE interes IS NOT NULL")
        print("✓ Valores migrados de columna 'interes' a 'interes_mensual'")
else:
    print("✓ La columna interes_mensual ya existe")

conn.commit()
conn.close()
print("\n✅ Actualización completada")