import sqlite3

conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

# Datos del nuevo préstamo
fecha_prestamo = "2026-03-03"
fecha_proximo_pago = "2026-04-03"
monto = 600000
interes = 10  # 10%
cuota = 66000  # monto + interés (para 1 mes)

# Incluir ambas columnas de interés
cursor.execute("""
    INSERT INTO prestamos 
    (codigo_prestamo, monto_prestado, interes, interes_mensual, cuota_mensual,
     cuotas_totales, cuotas_restantes, saldo_pendiente, fecha_prestamo, 
     fecha_proximo_pago, estado, id_socio)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", ("PREST-20260303-001", monto, interes, interes, cuota, 1, 1, monto, 
      fecha_prestamo, fecha_proximo_pago, "activo", 1))

conn.commit()
print(f"✅ Nuevo préstamo agregado. ID: {cursor.lastrowid}")

# Verificar
cursor.execute("""
    SELECT id_prestamo, codigo_prestamo, fecha_prestamo, fecha_proximo_pago, estado 
    FROM prestamos 
    ORDER BY id_prestamo
""")
print("\nPréstamos actuales:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Código: {row[1]}, Fecha préstamo: {row[2]}, Fecha próx: {row[3]}, Estado: {row[4]}")

conn.close()