# verificar_todo.py
import sqlite3
from datetime import date

print("=" * 60)
print("VERIFICANDO PRÉSTAMOS VENCIDOS")
print("=" * 60)

conn = sqlite3.connect('natillera.db')
cursor = conn.cursor()

hoy = date.today()
print(f"📅 Fecha actual: {hoy}")
print("-" * 60)

# Obtener todos los préstamos activos
cursor.execute("""
    SELECT id_prestamo, codigo_prestamo, fecha_prestamo, fecha_proximo_pago, 
           estado, saldo_pendiente, monto_prestado
    FROM prestamos 
    WHERE estado = 'activo'
    ORDER BY id_prestamo
""")

prestamos = cursor.fetchall()

if not prestamos:
    print("❌ No hay préstamos activos")
else:
    print(f"📋 Préstamos activos encontrados: {len(prestamos)}\n")
    
    for p in prestamos:
        id_prestamo = p[0]
        codigo = p[1] if p[1] else "SIN CÓDIGO"
        fecha_prestamo = p[2]
        fecha_prox = p[3]
        estado = p[4]
        saldo = p[5] if p[5] else 0
        monto = p[6] if p[6] else 0
        
        print(f"🔹 Préstamo ID: {id_prestamo}")
        print(f"   Código: {codigo}")
        print(f"   Fecha préstamo: {fecha_prestamo}")
        print(f"   Fecha próximo pago: {fecha_prox}")
        print(f"   Estado: {estado}")
        print(f"   Monto: ${monto:,.2f}")
        print(f"   Saldo: ${saldo:,.2f}")
        
        # Calcular vencimiento
        if fecha_prox:
            try:
                # Convertir fecha si es string o date
                if isinstance(fecha_prox, str):
                    fecha_venc = date.fromisoformat(fecha_prox)
                else:
                    fecha_venc = fecha_prox
                
                dias = (hoy - fecha_venc).days
                
                if dias > 0:
                    print(f"   ⚠️ ESTADO: VENCIDO hace {dias} días")
                elif dias == 0:
                    print(f"   ⚠️ ESTADO: VENCE HOY")
                else:
                    print(f"   ✅ ESTADO: Al día (vence en {abs(dias)} días)")
            except Exception as e:
                print(f"   ❌ Error al procesar fecha: {e}")
        else:
            print(f"   ❓ ESTADO: Sin fecha de vencimiento definida")
        
        print("-" * 50)

# Resumen por estado
print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)

cursor.execute("""
    SELECT estado, COUNT(*) FROM prestamos GROUP BY estado
""")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]} préstamo(s)")

conn.close()
print("\n" + "=" * 60)
input("Presiona Enter para salir...")