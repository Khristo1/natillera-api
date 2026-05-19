# verificar_fechas.py
import sqlite3
import os

# Ruta de tu base de datos
db_path = r"C:\Users\Khrist01\Documents\practicas sena\natillera_1.0\natillera.db"

# Verificar si el archivo existe
if not os.path.exists(db_path):
    print(f"❌ Base de datos no encontrada en: {db_path}")
else:
    print(f"✅ Base de datos encontrada: {db_path}")
    print(f"   Tamaño: {os.path.getsize(db_path)} bytes")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("PRÉSTAMOS REGISTRADOS")
    print("=" * 60)
    
    # Obtener todos los préstamos
    cursor.execute("""
        SELECT id_prestamo, codigo_prestamo, fecha_prestamo, 
               fecha_proximo_pago, estado, saldo_pendiente
        FROM prestamos
        ORDER BY id_prestamo
    """)
    
    prestamos = cursor.fetchall()
    
    if not prestamos:
        print("No hay préstamos registrados en la base de datos.")
    else:
        for p in prestamos:
            print(f"\n📋 ID: {p[0]}")
            print(f"   Código: {p[1] if p[1] else 'Sin código'}")
            print(f"   Fecha préstamo: {p[2]}")
            print(f"   Fecha próximo pago: {p[3] if p[3] else 'No definida'}")
            print(f"   Estado: {p[4]}")
            print(f"   Saldo pendiente: ${p[5]:,.2f}" if p[5] else "   Saldo pendiente: $0")
            print("   " + "-" * 40)
    
    # Contar préstamos por estado
    cursor.execute("""
        SELECT estado, COUNT(*) FROM prestamos GROUP BY estado
    """)
    print("\n" + "=" * 60)
    print("RESUMEN POR ESTADO")
    print("=" * 60)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} préstamo(s)")
    
    conn.close()