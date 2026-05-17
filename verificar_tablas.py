import sqlite3

conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

# Ver columnas de pagos_prestamo
print("=" * 50)
print("Columnas en la tabla 'pagos_prestamo':")
print("=" * 50)
cursor.execute("PRAGMA table_info(pagos_prestamo)")
columnas_pagos = cursor.fetchall()
if columnas_pagos:
    for col in columnas_pagos:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("  La tabla 'pagos_prestamo' no existe o no tiene columnas")

print("\n" + "=" * 50)
print("Todas las tablas en la base de datos:")
print("=" * 50)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()
for tabla in tablas:
    print(f"  - {tabla[0]}")

conn.close()