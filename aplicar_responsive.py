# aplicar_responsive.py
import os
import re

def aplicar_responsive_a_archivo(ruta_archivo):
    """Agrega importaciones responsive a un archivo"""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si ya tiene la importación
    if 'from modulos.responsive import' not in contenido:
        # Agregar importación después de los imports existentes
        patron = r'(import tkinter as tk.*?)\n'
        reemplazo = r'\1\nfrom modulos.responsive import configurar_ventana_responsive, configurar_treeview_responsive\n'
        contenido = re.sub(patron, reemplazo, contenido, flags=re.DOTALL)
    
    # Reemplazar Toplevel() con configuración responsive
    patron_ventana = r'(ventana = tk\.Toplevel\(\))\s*\n\s*ventana\.title\([^)]+\)'
    
    def reemplazar_ventana(match):
        return f'''{match.group(0)}
    
    # Configurar ventana responsive
    configurar_ventana_responsive(ventana, ancho_inicial=1000, alto_inicial=700, minimo_ancho=800, minimo_alto=500)'''
    
    contenido = re.sub(patron_ventana, reemplazar_ventana, contenido)
    
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✓ Procesado: {ruta_archivo}")

# Procesar archivos
archivos = ['modulos/socios.py', 'modulos/aportes.py', 'modulos/prestamos.py', 
            'modulos/actividades.py', 'modulos/reportes.py']

for archivo in archivos:
    if os.path.exists(archivo):
        aplicar_responsive_a_archivo(archivo)
    else:
        print(f"✗ No encontrado: {archivo}")

print("\n✅ Todos los archivos han sido actualizados para ser responsive")