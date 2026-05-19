# verificar_vencido_simple.py
import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

hoy = date.today()
print(f"Fecha actual: {hoy}")
print("=" * 50)

cursor.execute("""
    SELECT id_prestamo, codigo_prestamo, fecha_proximo_pago, estado, saldo_pendiente
    FROM prestamos 
    WHERE estado = 'activo'
""")

for row in cursor.fetchall():
    id_prestamo = row[0]
    codigo = row[1] if row[1] else "S/C"
    fecha_prox = row[2]
    estado = row[3]
    saldo = row[4] if row[4] else 0
    
    # Convertir fecha si es necesario
    if isinstance(fecha_prox, str):
        fecha_prox_date = date.fromisoformat(fecha_prox)
    elif isinstance(fecha_prox, date):
        fecha_prox_date = fecha_prox
    else:
        print(f"⚠️ Préstamo {id_prestamo} ({codigo}) - Fecha inválida: {fecha_prox}")
        continue
    
    dias = (hoy - fecha_prox_date).days
    
    if dias > 0:
        print(f"⚠️ Préstamo {id_prestamo} ({codigo}) - VENCIDO hace {dias} días (desde {fecha_prox_date})")
        print(f"   Saldo: ${saldo:,.2f}")
    else:
        print(f"✅ Préstamo {id_prestamo} ({codigo}) - Al día, vence en {abs(dias)} días")
    print("-" * 40)

conn.close()