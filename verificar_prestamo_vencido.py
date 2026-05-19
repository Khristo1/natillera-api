# verificar_prestamo_vencido.py
import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

print("=" * 60)
print("VERIFICANDO PRÉSTAMOS VENCIDOS")
print("=" * 60)

# Ver todos los préstamos activos con sus fechas
cursor.execute("""
    SELECT id_prestamo, codigo_prestamo, estado, fecha_proximo_pago, 
           saldo_pendiente, fecha_prestamo
    FROM prestamos 
    WHERE estado = 'activo'
    ORDER BY id_prestamo DESC
""")

prestamos = cursor.fetchall()

print(f"\nPréstamos ACTIVOS encontrados: {len(prestamos)}")
print("-" * 60)

for p in prestamos:
    print(f"ID: {p[0]}")
    print(f"  Código: {p[1]}")
    print(f"  Estado: {p[2]}")
    print(f"  Fecha próximo pago: {p[3]}")
    print(f"  Fecha préstamo: {p[5]}")
    print(f"  Saldo pendiente: ${p[4]:,.2f}")
    print("-" * 40)

# Verificar específicamente el préstamo con vencimiento 2026-04-03
print("\n" + "=" * 60)
print("BUSCANDO PRÉSTAMO CON VENCIMIENTO 2026-04-03")
print("=" * 60)

cursor.execute("""
    SELECT id_prestamo, codigo_prestamo, estado, fecha_proximo_pago, 
           saldo_pendiente, fecha_prestamo
    FROM prestamos 
    WHERE fecha_proximo_pago = '2026-04-03'
""")

prestamo_especifico = cursor.fetchall()

if prestamo_especifico:
    for p in prestamo_especifico:
        print(f"✅ ENCONTRADO: ID {p[0]}, Código {p[1]}, Estado {p[2]}")
else:
    print("❌ No se encontró ningún préstamo con fecha_proximo_pago = 2026-04-03")
    print("   Posibles causas:")
    print("   1. El préstamo ya fue pagado (estado = 'pagado')")
    print("   2. La fecha está en otro formato (ej: 2026-4-3 en lugar de 2026-04-03)")
    print("   3. El préstamo no existe o fue eliminado")

# Verificar si hay préstamos con estado 'pagado' que deberían estar activos
print("\n" + "=" * 60)
print("VERIFICANDO PRÉSTAMOS PAGADOS RECIENTEMENTE")
print("=" * 60)

cursor.execute("""
    SELECT id_prestamo, codigo_prestamo, estado, fecha_proximo_pago, saldo_pendiente
    FROM prestamos 
    WHERE estado = 'pagado' AND saldo_pendiente > 0
""")

pagados_con_saldo = cursor.fetchall()

if pagados_con_saldo:
    print("⚠️ Préstamos con estado 'pagado' pero con saldo pendiente > 0:")
    for p in pagados_con_saldo:
        print(f"   ID {p[0]}, Código {p[1]}, Saldo: ${p[4]:,.2f}")
else:
    print("✅ No hay préstamos pagados con saldo pendiente")

conn.close()

print("\n" + "=" * 60)
input("Presiona Enter para salir...")