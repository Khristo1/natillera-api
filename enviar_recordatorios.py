# enviar_recordatorios.py
import sqlite3
import webbrowser
import urllib.parse
from datetime import datetime, timedelta

def enviar_recordatorios_automaticos():
    conn = sqlite3.connect('natillera.db')
    cursor = conn.cursor()
    
    hoy = datetime.now().date()
    fecha_limite = hoy + timedelta(days=3)
    
    # Buscar préstamos próximos a vencer (3 días)
    cursor.execute("""
        SELECT p.id_prestamo, p.codigo_prestamo, p.saldo_pendiente, 
               p.cuota_mensual, p.fecha_proximo_pago,
               s.celular, s.nombre || ' ' || s.apellido,
               p.nombre_externo, p.celular_externo
        FROM prestamos p
        LEFT JOIN socios s ON p.id_socio = s.id_socio
        WHERE p.estado = 'activo' 
          AND p.fecha_proximo_pago BETWEEN ? AND ?
    """, (hoy.strftime("%Y-%m-%d"), fecha_limite.strftime("%Y-%m-%d")))
    
    prestamos = cursor.fetchall()
    
    for p in prestamos:
        telefono = p[5] if p[5] else p[8]
        nombre = p[6] if p[6] else p[7]
        
        if telefono:
            telefono = ''.join(filter(str.isdigit, telefono))
            if not telefono.startswith('57'):
                telefono = '57' + telefono
            
            mensaje = f"🔔 Natillera Familiar - RECORDATORIO\n\n"
            mensaje += f"Estimado/a {nombre},\n\n"
            mensaje += f"Su préstamo #{p[1]} vence el {p[4]}.\n"
            mensaje += f"Cuota: ${float(p[3]):,.2f}\n\n"
            mensaje += "¡Realice su pago a tiempo!"
            
            url = f"https://web.whatsapp.com/send?phone={telefono}&text={urllib.parse.quote(mensaje)}"
            webbrowser.open(url)
            print(f"Enviado recordatorio a {nombre} - {telefono}")
    
    conn.close()

if __name__ == "__main__":
    enviar_recordatorios_automaticos()