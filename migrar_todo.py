import sqlite3
import psycopg2

# --- Conexión a SQLite local ---
conn_sqlite = sqlite3.connect('natillera.db')
cursor_sqlite = conn_sqlite.cursor()

# --- Conexión a PostgreSQL en la nube ---
conn_pg = psycopg2.connect(
    database="natillera_db_7glm",
    user="natillera_db_7glm_user",
    password="SL76F9DjetHRYMCQtNvqW4hBLnn2Gfu5",
    host="dpg-d83gt05ckfvc73bl4umg-a.oregon-postgres.render.com",
    port=5432,
    sslmode='require'
)
cursor_pg = conn_pg.cursor()

# 1. Migrar socios
print("Migrando socios...")
cursor_sqlite.execute("SELECT codigo_socio, nombre, apellido, cedula, celular, correo, estado FROM socios")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO socios (codigo_socio, nombre, apellido, cedula, celular, correo, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (codigo_socio) DO NOTHING
    """, row)

# 2. Migrar aportes
print("Migrando aportes...")
cursor_sqlite.execute("SELECT id_socio, monto, mes, año, fecha_aporte, forma_pago, observaciones, estado FROM aportes")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO aportes (id_socio, monto, mes, año, fecha_aporte, forma_pago, observaciones, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, row)

# 3. Migrar préstamos
print("Migrando préstamos...")
cursor_sqlite.execute("SELECT id_socio, monto_prestado, interes_mensual, cuota_mensual, tipo_cuota, cuotas_totales, cuotas_restantes, saldo_pendiente, fecha_prestamo, fecha_proximo_pago, estado, observaciones FROM prestamos")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO prestamos (id_socio, monto_prestado, interes_mensual, cuota_mensual, tipo_cuota, cuotas_totales, cuotas_restantes, saldo_pendiente, fecha_prestamo, fecha_proximo_pago, estado, observaciones) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, row)

# 4. Migrar pagos de préstamos (con las columnas reales)
print("Migrando pagos de préstamos...")
cursor_sqlite.execute("SELECT id_prestamo, monto_pagado, fecha_pago, mes_correspondiente, forma_pago, comprobante FROM pagos_prestamo")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO pagos_prestamo (id_prestamo, monto_pagado, fecha_pago, mes_correspondiente, forma_pago, comprobante) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, row)

# 5. Migrar actividades
print("Migrando actividades...")
cursor_sqlite.execute("SELECT nombre_actividad, descripcion, fecha_actividad, inversion_total, ganancias, estado FROM actividades")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO actividades (nombre_actividad, descripcion, fecha_actividad, inversion_total, ganancias, estado) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, row)

# 6. Migrar pagos de actividades
print("Migrando pagos de actividades...")
cursor_sqlite.execute("SELECT id_actividad, id_socio, monto_pagado, fecha_pago, mes, año, forma_pago, observaciones, estado FROM pagos_actividad")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO pagos_actividad (id_actividad, id_socio, monto_pagado, fecha_pago, mes, año, forma_pago, observaciones, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, row)

conn_pg.commit()
print("✅ Migración completada exitosamente")

conn_sqlite.close()
conn_pg.close()