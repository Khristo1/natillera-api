# verificar_socios.py
import sqlite3

db_path = r"C:\Users\Khrist01\Documents\practicas sena\natillera_1.0\natillera.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ver todos los socios
cursor.execute("SELECT id_socio, codigo_socio, nombre, apellido, cedula, celular FROM socios")
socios = cursor.fetchall()

print("="*50)
print("SOCIOS REGISTRADOS EN EL SISTEMA")
print("="*50)

for socio in socios:
    print(f"ID: {socio[0]}")
    print(f"Código: {socio[1]}")
    print(f"Nombre: {socio[2]} {socio[3]}")
    print(f"Cédula: {socio[4]}")
    print(f"Celular: {socio[5]}")
    print("-"*30)

conn.close()