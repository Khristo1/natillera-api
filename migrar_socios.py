import sqlite3
import psycopg2

# Conectar a SQLite local
conn_sqlite = sqlite3.connect('natillera.db')
cursor_sqlite = conn_sqlite.cursor()
cursor_sqlite.execute("SELECT codigo_socio, nombre, apellido, cedula, celular, correo, estado FROM socios")
socios = cursor_sqlite.fetchall()

print(f"Socios encontrados en SQLite: {len(socios)}")

# Conectar a PostgreSQL en la nube
try:
    conn_pg = psycopg2.connect(
        database="natillera_db_7glm",
        user="natillera_db_7glm_user",
        password="SL76F9DjetHRYMCQtNvqW4hBLnn2Gfu5",
        host="dpg-d83gt05ckfvc73bl4umg-a.oregon-postgres.render.com",
        port=5432,
        sslmode='require'
    )
    cursor_pg = conn_pg.cursor()
    print("Conectado a PostgreSQL")
except Exception as e:
    print(f"Error conectando a PostgreSQL: {e}")
    exit()

# Migrar socios
migrados = 0
for socio in socios:
    try:
        cursor_pg.execute("""
            INSERT INTO socios (codigo_socio, nombre, apellido, cedula, celular, correo, estado) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (codigo_socio) DO NOTHING
        """, socio)
        migrados += 1
    except Exception as e:
        print(f"Error con socio {socio[0]}: {e}")

conn_pg.commit()
print(f"Migrados {migrados} socios a PostgreSQL")

conn_sqlite.close()
conn_pg.close()