# modulos/actividades.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class ModuloActividades:
    def __init__(self, database):
        self.db = database
    
    def nueva_actividad(self):
        """Ventana para nueva actividad"""
        ventana = tk.Toplevel()
        ventana.title("Nueva Actividad")
        ventana.geometry("600x500")
        
        main_frame = ttk.Frame(ventana, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="NUEVA ACTIVIDAD", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Campos de la actividad
        campos_frame = ttk.LabelFrame(main_frame, text="Datos de la Actividad", padding="10")
        campos_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(campos_frame, text="Nombre Actividad:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_nombre = ttk.Entry(campos_frame)
        entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(campos_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        text_desc = scrolledtext.ScrolledText(campos_frame, height=4, width=40)
        text_desc.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(campos_frame, text="Fecha Actividad:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha = ttk.Entry(campos_frame)
        entry_fecha.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(campos_frame, text="Inversión Total ($):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry_inversion = ttk.Entry(campos_frame)
        entry_inversion.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_inversion.insert(0, "0")
        
        ttk.Label(campos_frame, text="Ganancias ($):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        entry_ganancias = ttk.Entry(campos_frame)
        entry_ganancias.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_ganancias.insert(0, "0")
        
        def guardar_actividad():
            """Guardar actividad"""
            try:
                nombre = entry_nombre.get().strip()
                descripcion = text_desc.get("1.0", tk.END).strip()
                fecha = entry_fecha.get().strip()
                inversion_texto = entry_inversion.get().strip()
                ganancias_texto = entry_ganancias.get().strip()
                
                if not nombre or not fecha:
                    messagebox.showwarning("Error", "Complete los campos requeridos")
                    return
                
                # Validar montos
                inversion = float(inversion_texto) if inversion_texto.replace('.', '', 1).isdigit() else 0
                ganancias = float(ganancias_texto) if ganancias_texto.replace('.', '', 1).isdigit() else 0
                
                # Insertar actividad
                query = """
                INSERT INTO actividades (nombre_actividad, descripcion, fecha_actividad, 
                                        inversion_total, ganancias)
                VALUES (?, ?, ?, ?, ?)
                """
                
                if self.db.execute(query, (nombre, descripcion, fecha, inversion, ganancias)):
                    messagebox.showinfo("Éxito", "Actividad registrada correctamente")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo registrar la actividad")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Guardar Actividad", 
                  command=guardar_actividad, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=ventana.destroy, width=20).pack(side=tk.LEFT, padx=5)
        
        # Campo Inversión Total
        ttk.Label(campos_frame, text="Inversión Total ($):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry_inversion = ttk.Entry(campos_frame)
        entry_inversion.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_inversion.insert(0, "0")
        
        def formatear_inversion(event):
            try:
                valor = entry_inversion.get().replace(',', '')
                if valor and float(valor) > 0:
                    entry_inversion.delete(0, tk.END)
                    entry_inversion.insert(0, f"{float(valor):,.0f}")
            except:
                pass
        
        entry_inversion.bind('<FocusOut>', formatear_inversion)
        
        # Campo Ganancias
        ttk.Label(campos_frame, text="Ganancias ($):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        entry_ganancias = ttk.Entry(campos_frame)
        entry_ganancias.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_ganancias.insert(0, "0")
        
        entry_ganancias.bind('<FocusOut>', formatear_inversion)
    
    def gestionar_actividades(self):
        """Gestionar actividades existentes"""
        ventana = tk.Toplevel()
        ventana.title("Gestionar Actividades")
        ventana.geometry("800x500")
        
        main_frame = ttk.Frame(ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ("ID", "Nombre", "Fecha", "Inversión", "Ganancias", "Estado")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar actividades
        try:
            query = """
            SELECT id_actividad, nombre_actividad, fecha_actividad, 
                   inversion_total, ganancias, estado
            FROM actividades 
            ORDER BY fecha_actividad DESC
            """
            
            actividades = self.db.fetch_all(query)
            
            for actividad in actividades:
                tree.insert("", tk.END, values=actividad)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando actividades: {str(e)}")
    
    def registrar_pago_actividad(self):
            """Registrar pago de actividad - Versión con scroll responsive"""
            ventana = tk.Toplevel()
            ventana.title("Registrar Pago de Actividad")
            ventana.geometry("850x750")
            ventana.minsize(750, 600)
            ventana.transient()
            ventana.grab_set()
            
            # ========== CONTENEDOR PRINCIPAL CON SCROLL ==========
            main_container = ttk.Frame(ventana)
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Canvas y scrollbar para toda la ventana
            canvas = tk.Canvas(main_container, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Evento para redimensionar el ancho del canvas
            def on_canvas_configure(event):
                canvas.itemconfig("all", width=event.width)
            
            canvas.bind("<Configure>", on_canvas_configure)
            
            # ========== FRAME PRINCIPAL DENTRO DEL SCROLL ==========
            main_frame = ttk.Frame(scrollable_frame, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            tk.Label(main_frame, text="REGISTRAR PAGO DE ACTIVIDAD", 
                    font=("Arial", 16, "bold"), fg="navy").pack(pady=(0, 20))
            
            # ========== Frame para seleccionar socio (con scroll interno) ==========
            socio_container = ttk.LabelFrame(main_frame, text="1. SELECCIONAR SOCIO", padding="10")
            socio_container.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Frame de búsqueda
            search_frame = ttk.Frame(socio_container)
            search_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(search_frame, text="Buscar por nombre, cédula o código:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
            entry_buscar_socio = ttk.Entry(search_frame, width=35, font=("Arial", 10))
            entry_buscar_socio.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Frame para el Treeview de socios con scroll
            tree_socio_frame = ttk.Frame(socio_container)
            tree_socio_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            columns_socios = ("ID", "Código", "Nombre", "Cédula", "Celular")
            tree_socios = ttk.Treeview(tree_socio_frame, columns=columns_socios, show="headings", height=6)
            
            for col in columns_socios:
                tree_socios.heading(col, text=col)
                tree_socios.column(col, width=120)
            
            # Scrollbars para el treeview de socios
            tree_socio_scroll_y = ttk.Scrollbar(tree_socio_frame, orient=tk.VERTICAL, command=tree_socios.yview)
            tree_socio_scroll_x = ttk.Scrollbar(tree_socio_frame, orient=tk.HORIZONTAL, command=tree_socios.xview)
            tree_socios.configure(yscrollcommand=tree_socio_scroll_y.set, xscrollcommand=tree_socio_scroll_x.set)
            
            tree_socios.grid(row=0, column=0, sticky="nsew")
            tree_socio_scroll_y.grid(row=0, column=1, sticky="ns")
            tree_socio_scroll_x.grid(row=1, column=0, sticky="ew")
            
            tree_socio_frame.grid_rowconfigure(0, weight=1)
            tree_socio_frame.grid_columnconfigure(0, weight=1)
            
            # Botones de socio
            socio_btn_frame = ttk.Frame(socio_container)
            socio_btn_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(socio_btn_frame, text="🔍 Buscar Socio", command=lambda: buscar_socios(), width=18).pack(side=tk.LEFT, padx=5)
            ttk.Button(socio_btn_frame, text="Limpiar Selección", command=lambda: limpiar_seleccion_socio(), width=18).pack(side=tk.LEFT, padx=5)
            
            # Label para mostrar socio seleccionado
            lbl_socio_seleccionado = tk.Label(socio_container, text="⚡ Socio seleccionado: Ninguno", 
                                            font=("Arial", 10, "bold"), fg="green", bg="#f0f0f0")
            lbl_socio_seleccionado.pack(anchor=tk.W, pady=5, fill=tk.X)
            
            # ========== Frame para seleccionar actividad (con scroll interno) ==========
            actividad_container = ttk.LabelFrame(main_frame, text="2. SELECCIONAR ACTIVIDAD", padding="10")
            actividad_container.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Frame de búsqueda
            search_act_frame = ttk.Frame(actividad_container)
            search_act_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(search_act_frame, text="Buscar por nombre de actividad:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
            entry_buscar_actividad = ttk.Entry(search_act_frame, width=35, font=("Arial", 10))
            entry_buscar_actividad.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Frame para el Treeview de actividades con scroll
            tree_act_frame = ttk.Frame(actividad_container)
            tree_act_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            columns_actividades = ("ID", "Nombre", "Fecha", "Inversión", "Ganancias", "Estado")
            tree_actividades = ttk.Treeview(tree_act_frame, columns=columns_actividades, show="headings", height=5)
            
            for col in columns_actividades:
                tree_actividades.heading(col, text=col)
                tree_actividades.column(col, width=120)
            
            # Scrollbars para el treeview de actividades
            tree_act_scroll_y = ttk.Scrollbar(tree_act_frame, orient=tk.VERTICAL, command=tree_actividades.yview)
            tree_act_scroll_x = ttk.Scrollbar(tree_act_frame, orient=tk.HORIZONTAL, command=tree_actividades.xview)
            tree_actividades.configure(yscrollcommand=tree_act_scroll_y.set, xscrollcommand=tree_act_scroll_x.set)
            
            tree_actividades.grid(row=0, column=0, sticky="nsew")
            tree_act_scroll_y.grid(row=0, column=1, sticky="ns")
            tree_act_scroll_x.grid(row=1, column=0, sticky="ew")
            
            tree_act_frame.grid_rowconfigure(0, weight=1)
            tree_act_frame.grid_columnconfigure(0, weight=1)
            
            # Botones de actividad
            act_btn_frame = ttk.Frame(actividad_container)
            act_btn_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(act_btn_frame, text="🔍 Buscar Actividad", command=lambda: buscar_actividades(), width=18).pack(side=tk.LEFT, padx=5)
            ttk.Button(act_btn_frame, text="Limpiar Selección", command=lambda: limpiar_seleccion_actividad(), width=18).pack(side=tk.LEFT, padx=5)
            
            # Label para mostrar actividad seleccionada
            lbl_actividad_seleccionada = tk.Label(actividad_container, text="⚡ Actividad seleccionada: Ninguna", 
                                                font=("Arial", 10, "bold"), fg="blue", bg="#f0f0f0")
            lbl_actividad_seleccionada.pack(anchor=tk.W, pady=5, fill=tk.X)
            
            # ========== Frame para datos del pago ==========
            pago_container = ttk.LabelFrame(main_frame, text="3. DATOS DEL PAGO", padding="10")
            pago_container.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Grid para organizar los campos
            fields_frame = ttk.Frame(pago_container)
            fields_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Configurar grid responsive
            for i in range(2):
                fields_frame.columnconfigure(i, weight=1)
            
            # Monto
            ttk.Label(fields_frame, text="Monto a Pagar ($):", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
            entry_monto = ttk.Entry(fields_frame, font=("Arial", 12), width=20)
            entry_monto.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
            
            # Mes
            ttk.Label(fields_frame, text="Mes:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
            combo_mes = ttk.Combobox(fields_frame, values=[
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ], state="readonly", width=20, font=("Arial", 10))
            combo_mes.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
            combo_mes.current(datetime.now().month - 1)
            
            # Año
            ttk.Label(fields_frame, text="Año:", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
            entry_año = ttk.Entry(fields_frame, font=("Arial", 10), width=20)
            entry_año.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
            entry_año.insert(0, str(datetime.now().year))
            
            # Forma de pago
            ttk.Label(fields_frame, text="Forma de Pago:", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
            combo_forma_pago = ttk.Combobox(fields_frame, 
                                        values=["Efectivo", "Transferencia", "Débito", "Cheque"], 
                                        state="readonly", width=20, font=("Arial", 10))
            combo_forma_pago.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
            combo_forma_pago.set("Efectivo")
            
            # Observaciones
            ttk.Label(fields_frame, text="Observaciones:", font=("Arial", 10)).grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
            text_obs = tk.Text(fields_frame, height=4, width=40, font=("Arial", 10))
            text_obs.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
            
            # Label informativo
            lbl_info = tk.Label(pago_container, text="", font=("Arial", 9), fg="gray")
            lbl_info.pack(anchor=tk.W, pady=5)
            
            # ========== Funciones ==========
            socio_seleccionado_id = None
            socio_seleccionado_nombre = None
            actividad_seleccionada_id = None
            actividad_seleccionada_nombre = None
            
            def formatear_monto(event=None):
                try:
                    texto = entry_monto.get()
                    if texto:
                        limpio = texto.replace('$', '').replace(',', '').strip()
                        if limpio and limpio.replace('.', '', 1).isdigit():
                            numero = float(limpio)
                            if numero > 0:
                                entry_monto.delete(0, tk.END)
                                entry_monto.insert(0, f"{numero:,.0f}")
                except:
                    pass
            
            def quitar_formato_monto(event=None):
                try:
                    texto = entry_monto.get()
                    if texto:
                        limpio = texto.replace('$', '').replace(',', '').strip()
                        entry_monto.delete(0, tk.END)
                        entry_monto.insert(0, limpio)
                except:
                    pass
            
            entry_monto.bind('<FocusOut>', formatear_monto)
            entry_monto.bind('<FocusIn>', quitar_formato_monto)
            
            def buscar_socios():
                nonlocal socio_seleccionado_id, socio_seleccionado_nombre
                texto = entry_buscar_socio.get().strip()
                for item in tree_socios.get_children():
                    tree_socios.delete(item)
                
                if not texto:
                    query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular FROM socios WHERE estado = 'activo' ORDER BY nombre LIMIT 50"
                    socios = self.db.fetch_all(query)
                else:
                    query = """
                    SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular
                    FROM socios WHERE estado = 'activo' AND 
                    (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?)
                    ORDER BY nombre LIMIT 50
                    """
                    patron = f"%{texto}%"
                    socios = self.db.fetch_all(query, (patron, patron, patron, patron))
                
                for socio in socios:
                    tree_socios.insert("", tk.END, values=socio)
            
            def on_socio_seleccionado(event):
                nonlocal socio_seleccionado_id, socio_seleccionado_nombre
                seleccion = tree_socios.selection()
                if seleccion:
                    item = tree_socios.item(seleccion[0])
                    valores = item['values']
                    if valores and len(valores) > 2:
                        socio_seleccionado_id = valores[0]
                        socio_seleccionado_nombre = valores[2]
                        lbl_socio_seleccionado.config(text=f"✅ Socio seleccionado: {valores[2]} - Cédula: {valores[3]}", fg="green")
                        lbl_info.config(text=f"Socio ID: {socio_seleccionado_id}")
                    else:
                        limpiar_seleccion_socio()
            
            def limpiar_seleccion_socio():
                nonlocal socio_seleccionado_id, socio_seleccionado_nombre
                socio_seleccionado_id = None
                socio_seleccionado_nombre = None
                lbl_socio_seleccionado.config(text="⚡ Socio seleccionado: Ninguno", fg="red")
                tree_socios.selection_remove(tree_socios.selection())
                lbl_info.config(text="")
            
            def buscar_actividades():
                nonlocal actividad_seleccionada_id, actividad_seleccionada_nombre
                texto = entry_buscar_actividad.get().strip()
                for item in tree_actividades.get_children():
                    tree_actividades.delete(item)
                
                if not texto:
                    query = "SELECT id_actividad, nombre_actividad, fecha_actividad, inversion_total, ganancias, estado FROM actividades ORDER BY fecha_actividad DESC LIMIT 50"
                    actividades = self.db.fetch_all(query)
                else:
                    query = """
                    SELECT id_actividad, nombre_actividad, fecha_actividad, inversion_total, ganancias, estado
                    FROM actividades WHERE nombre_actividad LIKE ? OR descripcion LIKE ?
                    ORDER BY fecha_actividad DESC LIMIT 50
                    """
                    patron = f"%{texto}%"
                    actividades = self.db.fetch_all(query, (patron, patron))
                
                for actividad in actividades:
                    inversion = float(actividad[3]) if actividad[3] else 0
                    ganancias = float(actividad[4]) if actividad[4] else 0
                    tree_actividades.insert("", tk.END, values=(
                        actividad[0], actividad[1], actividad[2], 
                        f"${inversion:,.2f}", f"${ganancias:,.2f}", actividad[5]
                    ))
            
            def on_actividad_seleccionada(event):
                nonlocal actividad_seleccionada_id, actividad_seleccionada_nombre
                seleccion = tree_actividades.selection()
                if seleccion:
                    item = tree_actividades.item(seleccion[0])
                    valores = item['values']
                    if valores and len(valores) > 1:
                        actividad_seleccionada_id = valores[0]
                        actividad_seleccionada_nombre = valores[1]
                        lbl_actividad_seleccionada.config(text=f"✅ Actividad seleccionada: {valores[1]}", fg="blue")
                    else:
                        limpiar_seleccion_actividad()
            
            def limpiar_seleccion_actividad():
                nonlocal actividad_seleccionada_id, actividad_seleccionada_nombre
                actividad_seleccionada_id = None
                actividad_seleccionada_nombre = None
                lbl_actividad_seleccionada.config(text="⚡ Actividad seleccionada: Ninguna", fg="red")
                tree_actividades.selection_remove(tree_actividades.selection())
            
            tree_socios.bind("<<TreeviewSelect>>", on_socio_seleccionado)
            tree_actividades.bind("<<TreeviewSelect>>", on_actividad_seleccionada)
            
            def guardar_pago():
                try:
                    # Verificar socio seleccionado
                    if not socio_seleccionado_id:
                        messagebox.showwarning("Error", "Seleccione un socio de la lista")
                        return
                    
                    # Verificar actividad seleccionada
                    if not actividad_seleccionada_id:
                        messagebox.showwarning("Error", "Seleccione una actividad de la lista")
                        return
                    
                    # Validar monto
                    monto_texto = entry_monto.get().replace(',', '')
                    if not monto_texto or not monto_texto.replace('.', '', 1).isdigit():
                        messagebox.showwarning("Error", "Ingrese un monto válido")
                        return
                    
                    monto = float(monto_texto) if monto_texto else 0
                    if monto <= 0:
                        messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                        return
                    
                    # Validar mes
                    mes = combo_mes.get()
                    if not mes:
                        messagebox.showwarning("Error", "Seleccione un mes")
                        return
                    
                    # Validar año
                    año_texto = entry_año.get().strip()
                    if not año_texto.isdigit() or len(año_texto) != 4:
                        messagebox.showwarning("Error", "Ingrese un año válido (4 dígitos)")
                        return
                    
                    año = int(año_texto)
                    forma_pago = combo_forma_pago.get()
                    observaciones = text_obs.get("1.0", tk.END).strip()
                    
                    # Insertar pago
                    query = """
                    INSERT INTO pagos_actividad (id_actividad, id_socio, monto_pagado, fecha_pago, 
                                                mes, año, forma_pago, observaciones, estado)
                    VALUES (?, ?, ?, date('now'), ?, ?, ?, ?, 'pagado')
                    """
                    
                    if self.db.execute(query, (actividad_seleccionada_id, socio_seleccionado_id, monto, 
                                            mes, año, forma_pago, observaciones)):
                        messagebox.showinfo("✅ Éxito", 
                                        f"Pago registrado correctamente\n\n"
                                        f"Socio: {socio_seleccionado_nombre}\n"
                                        f"Actividad: {actividad_seleccionada_nombre}\n"
                                        f"Monto: ${monto:,.2f}\n"
                                        f"Mes: {mes} {año}\n"
                                        f"Forma de pago: {forma_pago}")
                        ventana.destroy()
                    else:
                        messagebox.showerror("Error", "No se pudo registrar el pago")
                
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {str(e)}")
            
            # ========== Botones principales ==========
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=20)
            
            ttk.Button(btn_frame, text="💾 REGISTRAR PAGO", 
                    command=guardar_pago, width=20).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="❌ CANCELAR", 
                    command=ventana.destroy, width=20).pack(side=tk.LEFT, padx=10)
            
            # Cargar datos iniciales
            buscar_socios()
            buscar_actividades()
            
            # Configurar scroll con mouse
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", on_mousewheel)
            scrollable_frame.bind("<MouseWheel>", on_mousewheel)
    
    def reporte_actividades(self):
            """Reporte de pagos de actividades"""
            ventana = tk.Toplevel()
            ventana.title("Reporte de Pagos de Actividades")
            ventana.geometry("1100x600")
            ventana.minsize(900, 400)
            
            main_frame = ttk.Frame(ventana, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(main_frame, text="REPORTE DE PAGOS DE ACTIVIDADES", 
                    font=("Arial", 14, "bold")).pack(pady=10)
            
            # Treeview
            columns = ("ID", "Fecha", "Socio", "Actividad", "Monto", "Mes", "Año", "Forma Pago", "Estado")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscroll=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Frame para total
            total_frame = ttk.Frame(main_frame)
            total_frame.pack(fill=tk.X, pady=10)
            
            total_label = tk.Label(total_frame, text="Total Recaudado: $0.00", 
                                font=("Arial", 12, "bold"), fg="green")
            total_label.pack(side=tk.RIGHT, padx=10)
            
            def cargar_pagos():
                for item in tree.get_children():
                    tree.delete(item)
                
                query = """
                SELECT pa.id_pago, pa.fecha_pago, s.nombre || ' ' || s.apellido,
                    a.nombre_actividad, pa.monto_pagado, pa.mes, pa.año, 
                    pa.forma_pago, pa.estado
                FROM pagos_actividad pa
                JOIN socios s ON pa.id_socio = s.id_socio
                JOIN actividades a ON pa.id_actividad = a.id_actividad
                ORDER BY pa.fecha_pago DESC
                """
                
                pagos = self.db.fetch_all(query)
                total = 0
                
                for pago in pagos:
                    monto = float(pago[4]) if pago[4] is not None else 0
                    total += monto
                    
                    tree.insert("", tk.END, values=(
                        pago[0], pago[1], pago[2], pago[3], 
                        f"${monto:,.2f}", pago[5], pago[6], pago[7], pago[8]
                    ))
                
                total_label.config(text=f"Total Recaudado: ${total:,.2f}")
            
            ttk.Button(main_frame, text="Actualizar", command=cargar_pagos).pack(pady=10)
            
            cargar_pagos()