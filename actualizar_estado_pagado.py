# actualizar_estado_pagado.py
import sqlite3

conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

# Cambiar estado a 'pagado' para los préstamos ID 1 y 2
cursor.execute("UPDATE prestamos SET estado = 'pagado' WHERE id_prestamo IN (1, 2)")
conn.commit()
print(f"Préstamos actualizados: {cursor.rowcount}")

# Verificar
cursor.execute("SELECT id_prestamo, estado, saldo_pendiente FROM prestamos")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Estado: {row[1]}, Saldo: {row[2]}")

conn.close()