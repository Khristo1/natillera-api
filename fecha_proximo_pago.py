import sqlite3
from datetime import datetime

conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id_prestamo, fecha_prestamo, fecha_proximo_pago, estado 
    FROM prestamos 
    WHERE id_prestamo = 1 OR fecha_prestamo LIKE '2026-03%'
""")

print("Préstamos de marzo 2026:")
for p in cursor.fetchall():
    print(f"ID: {p[0]}, Fecha préstamo: {p[1]}, Fecha próximo pago: {p[2]}, Estado: {p[3]}")

conn.close()