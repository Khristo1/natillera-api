# actualizar_saldos.py
import sqlite3

db_path = r"C:\Users\Khrist01\Documents\practicas sena\natillera_1.0\natillera.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Actualizando saldos pendientes...")

# Actualizar saldo pendiente donde sea null o 0
cursor.execute("UPDATE prestamos SET saldo_pendiente = monto_prestado WHERE saldo_pendiente IS NULL OR saldo_pendiente = 0")
print(f"  ✓ {cursor.rowcount} préstamos actualizados")

# Verificar que tipo_cuota tenga valor por defecto
cursor.execute("UPDATE prestamos SET tipo_cuota = 'Mensual' WHERE tipo_cuota IS NULL OR tipo_cuota = ''")
print(f"  ✓ {cursor.rowcount} préstamos con tipo_cuota actualizado")

# Verificar datos de socios
cursor.execute("SELECT id_socio, nombre, apellido FROM socios LIMIT 5")
print("\nSocios en BD:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Nombre: {row[1]} {row[2]}")

conn.commit()
conn.close()

print("\n¡Actualización completada!")