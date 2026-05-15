import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from modulos.database import Database
from datetime import datetime

app = Flask(__name__, static_folder='../app_web', static_url_path='')
CORS(app)

db = Database()

# ==================== ARCHIVOS ESTÁTICOS ====================

@app.route('/')
def index():
    return send_from_directory('../app_web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    allowed_extensions = ('.html', '.css', '.js', '.json', '.png', '.jpg', '.ico')
    if any(filename.endswith(ext) for ext in allowed_extensions):
        return send_from_directory('../app_web', filename)
    return jsonify({'error': 'Not found'}), 404

# ==================== ENDPOINT TEMPORAL ====================

@app.route('/api/crear_socio_prueba', methods=['GET'])
def crear_socio_prueba():
    try:
        db.execute("""
            INSERT INTO socios 
            (codigo_socio, nombre, apellido, cedula, celular, estado) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (codigo_socio) DO NOTHING
        """, ("SOC0001", "Juan", "Perez", "91018352", "3001234567", "activo"))
        return jsonify({"success": True, "message": "Socio de prueba creado"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# ==================== AUTENTICACION ====================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    codigo = data.get('codigo')
    cedula = data.get('cedula')
    
    print(f"Login intento - Código: {codigo}, Cédula: {cedula}")
    
    query = """
    SELECT id_socio, codigo_socio, nombre, apellido, cedula, celular, correo
    FROM socios 
    WHERE codigo_socio = %s AND cedula = %s AND estado = 'activo'
    """
    socio = db.fetch_one(query, (codigo, cedula))
    
    if socio:
        return jsonify({
            'success': True,
            'socio': {
                'id': socio[0],
                'codigo': socio[1],
                'nombre': socio[2],
                'apellido': socio[3],
                'cedula': socio[4],
                'celular': socio[5],
                'correo': socio[6] if len(socio) > 6 else ''
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'})

# ==================== APORTES ====================

@app.route('/api/aportes/<int:socio_id>', methods=['GET'])
def get_aportes(socio_id):
    query = "SELECT id_aporte, monto, mes, año, fecha_aporte, forma_pago, estado FROM aportes WHERE id_socio = %s ORDER BY año DESC, fecha_aporte DESC"
    aportes = db.fetch_all(query, (socio_id,))
    return jsonify({'success': True, 'aportes': [{
        'id': a[0], 'monto': a[1], 'mes': a[2], 'año': a[3],
        'fecha': a[4], 'forma_pago': a[5], 'estado': a[6]
    } for a in aportes]})

@app.route('/api/aportes/total/<int:socio_id>', methods=['GET'])
def get_total_aportes(socio_id):
    total = db.fetch_one("SELECT SUM(monto) FROM aportes WHERE id_socio = %s AND estado = 'pagado'", (socio_id,))
    return jsonify({'success': True, 'total': total[0] if total[0] else 0})

# ==================== PRESTAMOS ====================

@app.route('/api/prestamos/<int:socio_id>', methods=['GET'])
def get_prestamos(socio_id):
    query = "SELECT id_prestamo, monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, fecha_prestamo, saldo_pendiente, estado FROM prestamos WHERE id_socio = %s ORDER BY fecha_prestamo DESC"
    prestamos = db.fetch_all(query, (socio_id,))
    return jsonify({'success': True, 'prestamos': [{
        'id': p[0], 'monto': p[1], 'interes': p[2], 'cuota_mensual': p[3],
        'cuotas_totales': p[4], 'cuotas_restantes': p[5], 'fecha': p[6],
        'saldo_pendiente': p[7] if p[7] else p[1], 'estado': p[8]
    } for p in prestamos]})

# ==================== ACTIVIDADES ====================

@app.route('/api/actividades', methods=['GET'])
def get_actividades():
    actividades = db.fetch_all("SELECT id_actividad, nombre_actividad, descripcion, fecha_actividad, estado FROM actividades ORDER BY fecha_actividad DESC")
    return jsonify({'success': True, 'actividades': [{'id': a[0], 'nombre': a[1], 'descripcion': a[2], 'fecha': a[3], 'estado': a[4]} for a in actividades]})

@app.route('/api/actividades/pagos/<int:socio_id>', methods=['GET'])
def get_pagos_actividades(socio_id):
    pagos = db.fetch_all("""
        SELECT pa.id_pago, a.nombre_actividad, pa.monto_pagado, pa.fecha_pago
        FROM pagos_actividad pa
        JOIN actividades a ON pa.id_actividad = a.id_actividad
        WHERE pa.id_socio = %s ORDER BY pa.fecha_pago DESC
    """, (socio_id,))
    return jsonify({'success': True, 'pagos': [{'id': p[0], 'actividad': p[1], 'monto': p[2], 'fecha': p[3]} for p in pagos]})

# ==================== PROXIMOS PAGOS ====================

@app.route('/api/proximos_pagos/<int:socio_id>', methods=['GET'])
def get_proximos_pagos(socio_id):
    recordatorios = []
    prestamos = db.fetch_all("SELECT id_prestamo, cuota_mensual, saldo_pendiente, fecha_proximo_pago FROM prestamos WHERE id_socio = %s AND estado = 'activo' AND saldo_pendiente > 0", (socio_id,))
    for p in prestamos:
        recordatorios.append({'tipo': 'Préstamo', 'prestamo_id': p[0], 'monto': p[1] if p[1] else 0, 'saldo_pendiente': p[2] if p[2] else 0, 'fechaLimite': p[3] if p[3] else ''})
    return jsonify({'success': True, 'recordatorios': recordatorios})

# ==================== DASHBOARD ====================

@app.route('/api/dashboard/<int:socio_id>', methods=['GET'])
def get_dashboard(socio_id):
    total_aportes = db.fetch_one("SELECT SUM(monto) FROM aportes WHERE id_socio = %s AND estado = 'pagado'", (socio_id,))
    total_prestamos = db.fetch_one("SELECT SUM(saldo_pendiente) FROM prestamos WHERE id_socio = %s AND estado = 'activo'", (socio_id,))
    cuotas_pendientes = db.fetch_one("SELECT SUM(cuotas_restantes) FROM prestamos WHERE id_socio = %s AND estado = 'activo'", (socio_id,))
    aportes_total = total_aportes[0] if total_aportes and total_aportes[0] else 0
    prestamos_total = total_prestamos[0] if total_prestamos and total_prestamos[0] else 0
    cuotas_total = cuotas_pendientes[0] if cuotas_pendientes and cuotas_pendientes[0] else 0
    return jsonify({'success': True, 'dashboard': {
        'total_aportes': aportes_total,
        'total_prestamos': prestamos_total,
        'balance': aportes_total - prestamos_total,
        'cuotas_pendientes': cuotas_total
    }})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)