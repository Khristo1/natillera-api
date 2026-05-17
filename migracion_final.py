import sqlite3
import psycopg2
import os

# --- Conexión a SQLite (datos correctos) ---
print("1. Conectando a SQLite local...")
conn_sqlite = sqlite3.connect('natillera.db')
cursor_sqlite = conn_sqlite.cursor()

# --- Conexión a PostgreSQL (nube) ---
print("2. Conectando a PostgreSQL en la nube...")
conn_pg = psycopg2.connect(
    database="natillera_db_7glm",
    user="natillera_db_7glm_user",
    password="SL76F9DjetHRYMCQtNvqW4hBLnn2Gfu5",
    host="dpg-d83gt05ckfvc73bl4umg-a.oregon-postgres.render.com",
    port=5432,
    sslmode='require'
)
cursor_pg = conn_pg.cursor()

# --- LIMPIAR tablas en la nube (sin borrar la estructura) ---
print("3. Limpiando datos existentes en la nube...")
cursor_pg.execute("TRUNCATE TABLE pagos_actividad, pagos_prestamo, prestamos, aportes, socios, actividades RESTART IDENTITY CASCADE;")
conn_pg.commit()

# --- 1. Migrar socios ---
print("4. Migrando socios...")
cursor_sqlite.execute("SELECT codigo_socio, nombre, apellido, cedula, celular, correo, estado FROM socios")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO socios (codigo_socio, nombre, apellido, cedula, celular, correo, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, row)
conn_pg.commit()

# --- 2. Obtener diccionario de IDs nuevos (SQLite -> PostgreSQL) ---
print("5. Mapeando IDs de socios...")
cursor_sqlite.execute("SELECT id_socio, codigo_socio FROM socios")
sqlite_ids = {codigo: id_socio for id_socio, codigo in cursor_sqlite.fetchall()}

cursor_pg.execute("SELECT id_socio, codigo_socio FROM socios")
pg_ids = {codigo: id_socio for id_socio, codigo in cursor_pg.fetchall()}

# --- 3. Migrar aportes ---
print("6. Migrando aportes...")
cursor_sqlite.execute("SELECT id_socio, monto, mes, año, fecha_aporte, forma_pago, observaciones, estado FROM aportes")
for row in cursor_sqlite.fetchall():
    old_socio_id = row[0]
    codigo_socio = [k for k, v in sqlite_ids.items() if v == old_socio_id][0]
    new_socio_id = pg_ids[codigo_socio]
    cursor_pg.execute("""
        INSERT INTO aportes (id_socio, monto, mes, año, fecha_aporte, forma_pago, observaciones, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (new_socio_id, *row[1:]))
conn_pg.commit()

# --- 4. Migrar préstamos ---
print("7. Migrando préstamos...")
cursor_sqlite.execute("SELECT id_socio, monto_prestado, interes_mensual, cuota_mensual, tipo_cuota, cuotas_totales, cuotas_restantes, saldo_pendiente, fecha_prestamo, fecha_proximo_pago, estado, observaciones FROM prestamos")
for row in cursor_sqlite.fetchall():
    old_socio_id = row[0]
    codigo_socio = [k for k, v in sqlite_ids.items() if v == old_socio_id][0]
    new_socio_id = pg_ids[codigo_socio]
    cursor_pg.execute("""
        INSERT INTO prestamos (id_socio, monto_prestado, interes_mensual, cuota_mensual, tipo_cuota, cuotas_totales, cuotas_restantes, saldo_pendiente, fecha_prestamo, fecha_proximo_pago, estado, observaciones) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (new_socio_id, *row[1:]))
conn_pg.commit()

# --- 5. Migrar pagos de préstamos ---
print("8. Migrando pagos de préstamos...")
cursor_sqlite.execute("SELECT id_prestamo, monto_pagado, fecha_pago, mes_correspondiente, forma_pago, comprobante FROM pagos_prestamo")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO pagos_prestamo (id_prestamo, monto_pagado, fecha_pago, mes_correspondiente, forma_pago, comprobante) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, row)
conn_pg.commit()

# --- 6. Migrar actividades ---
print("9. Migrando actividades...")
cursor_sqlite.execute("SELECT nombre_actividad, descripcion, fecha_actividad, inversion_total, ganancias, estado FROM actividades")
for row in cursor_sqlite.fetchall():
    cursor_pg.execute("""
        INSERT INTO actividades (nombre_actividad, descripcion, fecha_actividad, inversion_total, ganancias, estado) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, row)
conn_pg.commit()

# --- 7. Migrar pagos de actividades ---
print("10. Migrando pagos de actividades...")
cursor_sqlite.execute("SELECT id_actividad, id_socio, monto_pagado, fecha_pago, mes, año, forma_pago, observaciones, estado FROM pagos_actividad")
for row in cursor_sqlite.fetchall():
    _, old_socio_id, *resto = row
    codigo_socio = [k for k, v in sqlite_ids.items() if v == old_socio_id][0]
    new_socio_id = pg_ids[codigo_socio]
    cursor_pg.execute("""
        INSERT INTO pagos_actividad (id_actividad, id_socio, monto_pagado, fecha_pago, mes, año, forma_pago, observaciones, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (row[0], new_socio_id, *resto))
conn_pg.commit()

print("Migracion completada. Los datos en la nube ahora coinciden con tu app de escritorio.")

conn_sqlite.close()
conn_pg.close()