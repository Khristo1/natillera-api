# modulos/moneda.py
"""
Módulo para manejo de formato de moneda en todo el proyecto
"""

def a_numero(valor):
    """Convierte un string formateado a número float"""
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        # Eliminar $, comas y espacios
        limpio = str(valor).replace('$', '').replace(',', '').replace(' ', '').strip()
        return float(limpio) if limpio else 0.0
    except:
        return 0.0

def a_moneda(valor, decimales=2):
    """Convierte un número a string con formato de moneda"""
    try:
        num = a_numero(valor)
        if decimales == 0:
            return f"${num:,.0f}"
        return f"${num:,.{decimales}f}"
    except:
        return "$0.00"

def formatear_entry(entry, decimales=0):
    """Convierte un Entry para que formatee números automáticamente"""
    def _formatear(event=None):
        try:
            texto = entry.get()
            if texto:
                num = a_numero(texto)
                if decimales == 0:
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{num:,.0f}")
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{num:,.{decimales}f}")
        except:
            pass
    
    def _quitar_formato(event=None):
        try:
            texto = entry.get()
            if texto:
                num = a_numero(texto)
                entry.delete(0, tk.END)
                entry.insert(0, str(int(num)) if decimales == 0 else str(num))
        except:
            pass
    
    entry.bind('<FocusOut>', _formatear)
    entry.bind('<FocusIn>', _quitar_formato)
    
    # Formatear inicialmente
    _formatear()
    
    return entry

def formatear_label_moneda(label, valor):
    """Actualiza un Label con valor formateado"""
    label.config(text=a_moneda(valor))

def limpiar_numero(texto):
    """Limpia un string para obtener solo números"""
    if not texto:
        return "0"
    return texto.replace('$', '').replace(',', '').strip()