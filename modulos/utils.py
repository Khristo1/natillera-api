# modulos/utils.py
import tkinter as tk
from tkinter import ttk

def formato_moneda(valor):
    """Formatea un número como moneda con separador de miles"""
    try:
        if isinstance(valor, str):
            valor = float(valor.replace(',', '').strip())
        return f"${valor:,.2f}"
    except:
        return "$0.00"

def formato_numero(valor, decimales=0):
    """Formatea un número con separador de miles"""
    try:
        if isinstance(valor, str):
            valor = float(valor.replace(',', '').strip())
        if decimales == 0:
            return f"{valor:,.0f}"
        else:
            return f"{valor:,.{decimales}f}"
    except:
        return "0"

def quitar_formato(texto):
    """Elimina comas y símbolos de moneda para obtener un número limpio"""
    if not texto:
        return "0"
    return texto.replace('$', '').replace(',', '').strip()

def validar_numero(texto):
    """Valida que el texto sea un número válido (permite comas y puntos)"""
    if not texto:
        return True
    # Permitir números, comas y un solo punto
    texto_limpio = texto.replace(',', '')
    try:
        float(texto_limpio)
        return True
    except:
        return False

class EntryConFormato(ttk.Entry):
    """Entry que formatea números automáticamente mientras se escribe"""
    def __init__(self, parent, decimales=0, **kwargs):
        self.decimales = decimales
        super().__init__(parent, **kwargs)
        self.bind('<KeyRelease>', self._formatear)
        self.bind('<FocusOut>', self._formatear)
        self.bind('<FocusIn>', self._quitar_formato)
    
    def _formatear(self, event=None):
        """Formatea el número al perder foco o mientras escribe"""
        try:
            texto = self.get()
            if texto:
                # Quitar formato existente
                limpio = texto.replace('$', '').replace(',', '').strip()
                if limpio:
                    numero = float(limpio)
                    if self.decimales == 0:
                        self.delete(0, tk.END)
                        self.insert(0, f"{numero:,.0f}")
                    else:
                        self.delete(0, tk.END)
                        self.insert(0, f"{numero:,.{self.decimales}f}")
        except:
            pass
    
    def _quitar_formato(self, event=None):
        """Quita el formato para editar"""
        try:
            texto = self.get()
            if texto:
                limpio = texto.replace('$', '').replace(',', '').strip()
                self.delete(0, tk.END)
                self.insert(0, limpio)
        except:
            pass
    
    def get_valor(self):
        """Retorna el valor numérico (float) del campo"""
        try:
            texto = self.get()
            if texto:
                return float(texto.replace('$', '').replace(',', '').strip())
            return 0.0
        except:
            return 0.0

class LabelMoneda(tk.Label):
    """Label que muestra valores en formato moneda"""
    def __init__(self, parent, valor=0, **kwargs):
        super().__init__(parent, **kwargs)
        self.valor_actual = valor
        self.actualizar(valor)
    
    def actualizar(self, valor):
        """Actualiza el label con el valor formateado"""
        self.valor_actual = valor
        self.config(text=formato_moneda(valor))

def configurar_entries_con_formato(parent):
    """Configura todos los Entry de un frame para usar formato de números"""
    for widget in parent.winfo_children():
        if isinstance(widget, ttk.Entry):
            # Verificar si el entry es para números
            if widget.get().replace('.', '').isdigit() or widget.get() == "":
                EntryConFormato(parent, decimales=0)
        elif isinstance(widget, tk.Frame) or isinstance(widget, ttk.Frame) or isinstance(widget, ttk.LabelFrame):
            configurar_entries_con_formato(widget)

def formatear_treeview_montos(tree, columnas_montos):
    """
    Formatea las columnas de montos en un Treeview
    columnas_montos: lista de índices de columnas que contienen montos
    """
    for item in tree.get_children():
        valores = list(tree.item(item, 'values'))
        for col_idx in columnas_montos:
            if col_idx < len(valores):
                try:
                    # Limpiar y formatear
                    valor = str(valores[col_idx]).replace('$', '').replace(',', '').strip()
                    if valor and valor.replace('.', '').isdigit():
                        num = float(valor)
                        valores[col_idx] = f"${num:,.2f}"
                except:
                    pass
        tree.item(item, values=valores)