# modulos/responsive.py
import tkinter as tk
from tkinter import ttk

def configurar_ventana_responsive(ventana, ancho_inicial=1000, alto_inicial=700, minimo_ancho=800, minimo_alto=500):
    """
    Configura una ventana para que sea responsive
    """
    # Centrar ventana en la pantalla
    ventana.update_idletasks()
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()
    
    # Calcular posición centrada
    x = (screen_width - ancho_inicial) // 2
    y = (screen_height - alto_inicial) // 2
    
    ventana.geometry(f"{ancho_inicial}x{alto_inicial}+{x}+{y}")
    
    # Permitir redimensionar
    ventana.resizable(True, True)
    
    # Establecer tamaño mínimo
    ventana.minsize(minimo_ancho, minimo_alto)
    
    return ventana

def configurar_frame_expansible(frame, padding=10):
    """
    Configura un frame para que sea expansible
    """
    frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
    return frame

def configurar_treeview_responsive(tree, parent_frame):
    """
    Configura un Treeview para que sea responsive
    """
    # Configurar scrollbars
    scrollbar_y = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar_x = ttk.Scrollbar(parent_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    
    # Posicionar usando pack (más simple y confiable)
    tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    return parent_frame