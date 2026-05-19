# modulos/prestamos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

class ModuloPrestamos:
    def __init__(self, database):
        self.db = database
    
    def nuevo_prestamo(self):
            """Ventana para nuevo préstamo - Socio o Particular"""
            ventana = tk.Toplevel()
            ventana.title("Nuevo Préstamo")
            ventana.geometry("800x800")
            ventana.minsize(750, 700)
            ventana.transient()
            ventana.grab_set()
            
            # Contenedor con scroll
            main_container = ttk.Frame(ventana)
            main_container.pack(fill=tk.BOTH, expand=True)
            
            canvas = tk.Canvas(main_container, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            main_frame = ttk.Frame(scrollable_frame, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(main_frame, text="NUEVO PRÉSTAMO", 
                    font=("Arial", 16, "bold"), fg="navy").pack(pady=(0, 20))
            
            # ========== 1. TIPO DE SOLICITANTE ==========
            tipo_frame = ttk.LabelFrame(main_frame, text="TIPO DE SOLICITANTE", padding="10")
            tipo_frame.pack(fill=tk.X, pady=5)
            
            tipo_var = tk.StringVar(value="socio")
            ttk.Radiobutton(tipo_frame, text="Socio (registrado)", variable=tipo_var, value="socio", 
                        command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(tipo_frame, text="Particular (no socio)", variable=tipo_var, value="particular", 
                        command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
            
            # ========== 2. DATOS DEL SOLICITANTE ==========
            # Frame para SOCIO
            socio_frame = ttk.LabelFrame(main_frame, text="DATOS DEL SOCIO", padding="10")
            
            search_frame = ttk.Frame(socio_frame)
            search_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(search_frame, text="Buscar socio:").pack(side=tk.LEFT, padx=5)
            entry_buscar = ttk.Entry(search_frame, width=30)
            entry_buscar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            ttk.Button(search_frame, text="🔍 Buscar", command=lambda: buscar_socios()).pack(side=tk.LEFT, padx=5)
            
            tree_frame = ttk.Frame(socio_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            columns = ("ID", "Código", "Nombre", "Cédula", "Celular")
            tree_socios = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
            for col in columns:
                tree_socios.heading(col, text=col)
                tree_socios.column(col, width=110)
            
            scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree_socios.yview)
            tree_socios.configure(yscroll=scroll_y.set)
            tree_socios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            
            lbl_socio_seleccionado = tk.Label(socio_frame, text="⚡ Socio seleccionado: Ninguno", 
                                            font=("Arial", 10, "bold"), fg="green")
            lbl_socio_seleccionado.pack(anchor=tk.W, pady=5)
            
            # Frame para PARTICULAR
            particular_frame = ttk.LabelFrame(main_frame, text="DATOS DEL PARTICULAR", padding="10")
            
            ttk.Label(particular_frame, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            entry_nombre = ttk.Entry(particular_frame, width=35)
            entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(particular_frame, text="Número de celular:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            entry_celular = ttk.Entry(particular_frame, width=35)
            entry_celular.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(particular_frame, text="Recomendado por (socio):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            frame_rec = ttk.Frame(particular_frame)
            frame_rec.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            
            entry_buscar_rec = ttk.Entry(frame_rec, width=25)
            entry_buscar_rec.pack(side=tk.LEFT)
            ttk.Button(frame_rec, text="Buscar", command=lambda: buscar_recomendador()).pack(side=tk.LEFT, padx=5)
            
            tree_rec_frame = ttk.Frame(particular_frame)
            tree_rec_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            
            columns_rec = ("ID", "Código", "Nombre")
            tree_recomendador = ttk.Treeview(tree_rec_frame, columns=columns_rec, show="headings", height=3)
            for col in columns_rec:
                tree_recomendador.heading(col, text=col)
                tree_recomendador.column(col, width=100)
            
            scroll_rec = ttk.Scrollbar(tree_rec_frame, orient=tk.VERTICAL, command=tree_recomendador.yview)
            tree_recomendador.configure(yscroll=scroll_rec.set)
            tree_recomendador.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll_rec.pack(side=tk.RIGHT, fill=tk.Y)
            
            lbl_recomendador = tk.Label(particular_frame, text="⚡ Recomendador: Ninguno", 
                                        font=("Arial", 10, "bold"), fg="blue")
            lbl_recomendador.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.W)
            
            # ========== 3. DATOS DEL PRÉSTAMO ==========
            datos_frame = ttk.LabelFrame(main_frame, text="DATOS DEL PRÉSTAMO", padding="10")
            datos_frame.pack(fill=tk.X, pady=10)
            
            # Fila 0: Fecha del préstamo
            ttk.Label(datos_frame, text="Fecha del préstamo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            entry_fecha = ttk.Entry(datos_frame)
            entry_fecha.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
            entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            # Fila 1: Monto
            ttk.Label(datos_frame, text="Monto ($):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            entry_monto = ttk.Entry(datos_frame)
            entry_monto.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
            entry_monto.insert(0, "0")
            
            # Fila 2: Interés (%)
            ttk.Label(datos_frame, text="Interés (%):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            combo_interes = ttk.Combobox(datos_frame, values=["5%", "10%"], state="readonly", width=10)
            combo_interes.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            combo_interes.set("5%")
            
            # Fila 3: Tiempo del préstamo
            tiempo_frame = ttk.Frame(datos_frame)
            tiempo_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(tiempo_frame, text="Tiempo:").pack(side=tk.LEFT, padx=5)
            entry_tiempo = ttk.Entry(tiempo_frame, width=10)
            entry_tiempo.pack(side=tk.LEFT, padx=5)
            combo_unidad = ttk.Combobox(tiempo_frame, values=["meses", "días"], state="readonly", width=8)
            combo_unidad.pack(side=tk.LEFT, padx=5)
            combo_unidad.set("meses")
            
            # Fila 4: Cuota calculada
            ttk.Label(datos_frame, text="Cuota calculada:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
            lbl_cuota = tk.Label(datos_frame, text="$0.00", font=("Arial", 12, "bold"), fg="blue")
            lbl_cuota.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Fila 5: Fecha de pago (próxima cuota o fecha final)
            ttk.Label(datos_frame, text="Fecha de pago:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
            entry_fecha_pago = ttk.Entry(datos_frame)
            entry_fecha_pago.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
            
            # Fila 6: Observaciones
            ttk.Label(datos_frame, text="Observaciones:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
            text_obs = tk.Text(datos_frame, height=3, width=35)
            text_obs.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
            
            # Función para calcular cuota y fecha de pago
            def calcular_cuota_y_fecha(event=None):
                try:
                    monto_texto = entry_monto.get().replace(',', '')
                    monto = float(monto_texto) if monto_texto else 0
                    interes_porcentaje = int(combo_interes.get().replace('%', ''))
                    tiempo = int(entry_tiempo.get()) if entry_tiempo.get() else 0
                    unidad = combo_unidad.get()
                    fecha_inicial = entry_fecha.get()
                    
                    if monto > 0 and tiempo > 0:
                        interes_valor = monto * (interes_porcentaje / 100)
                        total = monto + interes_valor
                        
                        if unidad == "meses":
                            cuota = total / tiempo
                            lbl_cuota.config(text=f"${cuota:,.2f} (total ${total:,.2f})")
                            # Fecha de pago = fecha inicial + (tiempo meses) para la última cuota
                            try:
                                fecha_dt = datetime.strptime(fecha_inicial, "%Y-%m-%d")
                                from dateutil.relativedelta import relativedelta
                                fecha_final = fecha_dt + relativedelta(months=tiempo)
                                entry_fecha_pago.delete(0, tk.END)
                                entry_fecha_pago.insert(0, fecha_final.strftime("%Y-%m-%d"))
                            except:
                                pass
                        else:  # días
                            cuota = total  # pago único
                            lbl_cuota.config(text=f"${cuota:,.2f} (pago único)")
                            # Fecha de pago = fecha inicial + tiempo días
                            try:
                                fecha_dt = datetime.strptime(fecha_inicial, "%Y-%m-%d")
                                fecha_final = fecha_dt + timedelta(days=tiempo)
                                entry_fecha_pago.delete(0, tk.END)
                                entry_fecha_pago.insert(0, fecha_final.strftime("%Y-%m-%d"))
                            except:
                                pass
                    else:
                        lbl_cuota.config(text="$0.00")
                except:
                    lbl_cuota.config(text="$0.00")
            
            # Vincular eventos para calcular automáticamente
            entry_monto.bind("<KeyRelease>", calcular_cuota_y_fecha)
            combo_interes.bind("<<ComboboxSelected>>", calcular_cuota_y_fecha)
            entry_tiempo.bind("<KeyRelease>", calcular_cuota_y_fecha)
            combo_unidad.bind("<<ComboboxSelected>>", calcular_cuota_y_fecha)
            entry_fecha.bind("<KeyRelease>", calcular_cuota_y_fecha)
            
            # ========== VARIABLES ==========
            socio_seleccionado_id = None
            socio_seleccionado_nombre = None
            recomendador_id = None
            recomendador_nombre = None
            
            # ========== FUNCIONES ==========
            def toggle_tipo():
                if tipo_var.get() == "socio":
                    socio_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                    particular_frame.pack_forget()
                else:
                    socio_frame.pack_forget()
                    particular_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            def buscar_socios():
                texto = entry_buscar.get().strip()
                for item in tree_socios.get_children():
                    tree_socios.delete(item)
                
                if not texto:
                    query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular FROM socios WHERE estado = 'activo' ORDER BY nombre LIMIT 50"
                    socios = self.db.fetch_all(query)
                else:
                    query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular FROM socios WHERE estado = 'activo' AND (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?) ORDER BY nombre LIMIT 50"
                    p = f"%{texto}%"
                    socios = self.db.fetch_all(query, (p, p, p, p))
                
                for s in socios:
                    tree_socios.insert("", tk.END, values=s)
            
            def on_socio_select(event):
                nonlocal socio_seleccionado_id, socio_seleccionado_nombre
                sel = tree_socios.selection()
                if sel:
                    vals = tree_socios.item(sel[0])['values']
                    if vals:
                        socio_seleccionado_id = vals[0]
                        socio_seleccionado_nombre = vals[2]
                        lbl_socio_seleccionado.config(text=f"✅ Socio seleccionado: {socio_seleccionado_nombre}")
            
            def buscar_recomendador():
                texto = entry_buscar_rec.get().strip()
                for item in tree_recomendador.get_children():
                    tree_recomendador.delete(item)
                
                if not texto:
                    query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido FROM socios WHERE estado = 'activo' ORDER BY nombre LIMIT 30"
                    socios = self.db.fetch_all(query)
                else:
                    query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido FROM socios WHERE estado = 'activo' AND (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?) ORDER BY nombre LIMIT 30"
                    p = f"%{texto}%"
                    socios = self.db.fetch_all(query, (p, p, p, p))
                
                for s in socios:
                    tree_recomendador.insert("", tk.END, values=s)
            
            def on_recomendador_select(event):
                nonlocal recomendador_id, recomendador_nombre
                sel = tree_recomendador.selection()
                if sel:
                    vals = tree_recomendador.item(sel[0])['values']
                    if vals:
                        recomendador_id = vals[0]
                        recomendador_nombre = vals[2]
                        lbl_recomendador.config(text=f"✅ Recomendador: {recomendador_nombre}")
            
            tree_socios.bind("<<TreeviewSelect>>", on_socio_select)
            tree_recomendador.bind("<<TreeviewSelect>>", on_recomendador_select)
            
            def formatear_monto(entry):
                def _format(event=None):
                    try:
                        texto = entry.get()
                        if texto:
                            limpio = texto.replace('$', '').replace(',', '').strip()
                            if limpio and limpio.replace('.', '', 1).isdigit():
                                num = float(limpio)
                                if num > 0:
                                    entry.delete(0, tk.END)
                                    entry.insert(0, f"{num:,.0f}")
                    except:
                        pass
                return _format
            
            entry_monto.bind('<FocusOut>', formatear_monto(entry_monto))
            entry_monto.bind('<FocusIn>', lambda e: entry_monto.delete(0, tk.END))
            
            def registrar_prestamo():
                try:
                    # Obtener valores
                    fecha_prestamo = entry_fecha.get()
                    monto_texto = entry_monto.get().replace(',', '')
                    monto = float(monto_texto) if monto_texto else 0
                    interes_porcentaje = int(combo_interes.get().replace('%', ''))
                    tiempo = int(entry_tiempo.get()) if entry_tiempo.get() else 0
                    unidad = combo_unidad.get()
                    obs = text_obs.get("1.0", tk.END).strip()
                    
                    if monto <= 0:
                        messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                        return
                    
                    if tiempo <= 0:
                        messagebox.showwarning("Error", "El tiempo debe ser mayor a cero")
                        return
                    
                    # Calcular interés y cuota
                    interes_valor = monto * (interes_porcentaje / 100)
                    total = monto + interes_valor
                    
                    if unidad == "meses":
                        cuota = total / tiempo
                        cuotas_totales = tiempo
                        cuotas_restantes = tiempo
                        fecha_proximo_pago = entry_fecha_pago.get()
                    else:  # días
                        cuota = total
                        cuotas_totales = 1
                        cuotas_restantes = 1
                        fecha_proximo_pago = entry_fecha_pago.get()
                    
                    saldo_pendiente = total
                    
                    if tipo_var.get() == "socio":
                        if not socio_seleccionado_id:
                            messagebox.showwarning("Error", "Seleccione un socio")
                            return
                        
                        query = """INSERT INTO prestamos 
                            (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                            cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                            saldo_pendiente, observaciones, estado, es_externo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 0)"""
                        
                        self.db.execute(query, (socio_seleccionado_id, monto, interes_porcentaje, cuota,
                                                cuotas_totales, cuotas_restantes, fecha_prestamo,
                                                fecha_proximo_pago, saldo_pendiente, obs))
                        messagebox.showinfo("Éxito", f"Préstamo registrado para socio: {socio_seleccionado_nombre}\n"
                                                    f"Monto: ${monto:,.2f}\nInterés: {interes_porcentaje}%\n"
                                                    f"Total a pagar: ${total:,.2f}\nCuota: ${cuota:,.2f}")
                    else:
                        nombre = entry_nombre.get().strip()
                        celular = entry_celular.get().strip()
                        
                        if not nombre or not celular:
                            messagebox.showwarning("Error", "Complete nombre y celular del particular")
                            return
                        
                        query = """INSERT INTO prestamos 
                            (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                            cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                            saldo_pendiente, observaciones, estado, es_externo, 
                            nombre_externo, celular_externo, id_recomendador)
                            VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 1, ?, ?, ?)"""
                        
                        self.db.execute(query, (monto, interes_porcentaje, cuota,
                                                cuotas_totales, cuotas_restantes, fecha_prestamo,
                                                fecha_proximo_pago, saldo_pendiente, obs,
                                                nombre, celular, recomendador_id))
                        messagebox.showinfo("Éxito", f"Préstamo registrado para particular: {nombre}\n"
                                                    f"Monto: ${monto:,.2f}\nInterés: {interes_porcentaje}%\n"
                                                    f"Total a pagar: ${total:,.2f}\nCuota: ${cuota:,.2f}")
                    
                    ventana.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {str(e)}")
            
            # ========== BOTONES ==========
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(pady=20)
            
            ttk.Button(btn_frame, text="✅ APROBAR PRÉSTAMO", command=registrar_prestamo, width=20).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="❌ CANCELAR", command=ventana.destroy, width=20).pack(side=tk.LEFT, padx=10)
            
            # Inicializar
            buscar_socios()
            toggle_tipo()
            calcular_cuota_y_fecha()    
       
    def gestionar_prestamos(self):
        """Gestionar préstamos existentes - Muestra socios y particulares, pagos mejorados"""
        ventana = tk.Toplevel()
        ventana.title("Gestión de Préstamos")
        ventana.geometry("1300x700")
        ventana.minsize(900, 500)
        
        # ========== LISTA DE PRÉSTAMOS ==========
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Solicitante", "Monto", "Interés", "Cuota", "Plazo", "Restantes", "Saldo", "Estado", "Fecha")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 50, "Solicitante": 200, "Monto": 120, "Interés": 70, "Cuota": 120, 
                    "Plazo": 70, "Restantes": 70, "Saldo": 120, "Estado": 90, "Fecha": 100}
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 100))
        
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ========== DETALLES DEL PRÉSTAMO ==========
        detalles_frame = ttk.LabelFrame(main_frame, text="Detalles del Préstamo Seleccionado", padding="10")
        detalles_frame.pack(fill=tk.X, pady=10)
        
        lbl_solicitante = tk.Label(detalles_frame, text="Solicitante: ", font=("Arial", 11, "bold"))
        lbl_solicitante.pack(anchor=tk.W, pady=2)
        
        lbl_monto = tk.Label(detalles_frame, text="Monto: $0", font=("Arial", 10))
        lbl_monto.pack(anchor=tk.W, pady=2)
        
        lbl_interes = tk.Label(detalles_frame, text="Interés: 0%", font=("Arial", 10))
        lbl_interes.pack(anchor=tk.W, pady=2)
        
        lbl_saldo = tk.Label(detalles_frame, text="Saldo pendiente: $0", font=("Arial", 11, "bold"), fg="red")
        lbl_saldo.pack(anchor=tk.W, pady=2)
        
        lbl_proximo = tk.Label(detalles_frame, text="Próxima cuota: $0", font=("Arial", 10))
        lbl_proximo.pack(anchor=tk.W, pady=2)
        
        lbl_fecha = tk.Label(detalles_frame, text="Fecha próximo pago: ", font=("Arial", 10))
        lbl_fecha.pack(anchor=tk.W, pady=2)
        
        # ========== FUNCIONES ==========
        prestamo_actual_id = None
        
        def cargar_prestamos():
            for item in tree.get_children():
                tree.delete(item)
            
            # Consulta que incluye socios y particulares
            query = """
                SELECT p.id_prestamo, 
                    CASE 
                        WHEN p.es_externo = 1 THEN p.nombre_externo 
                        ELSE s.nombre || ' ' || s.apellido 
                    END as solicitante,
                    p.monto_prestado, 
                    p.interes_mensual, 
                    p.cuota_mensual,
                    p.cuotas_totales, 
                    p.cuotas_restantes, 
                    p.saldo_pendiente, 
                    p.estado,
                    p.fecha_prestamo
                FROM prestamos p
                LEFT JOIN socios s ON p.id_socio = s.id_socio
                ORDER BY p.fecha_prestamo DESC
            """
            prestamos = self.db.fetch_all(query)
            
            if not prestamos:
                tree.insert("", tk.END, values=("No hay préstamos", "", "", "", "", "", "", "", "", ""))
                return
            
            for p in prestamos:
                monto = float(p[2]) if p[2] is not None else 0
                interes = float(p[3]) if p[3] is not None else 0
                cuota = float(p[4]) if p[4] is not None else 0
                saldo = float(p[7]) if p[7] is not None else 0
                valores = (p[0], p[1], f"${monto:,.2f}", f"{interes}%", f"${cuota:,.2f}",
                        p[5], p[6], f"${saldo:,.2f}", p[8], p[9])
                
                if p[8] == "activo":
                    tree.insert("", tk.END, values=valores, tags=("activo",))
                elif p[8] == "pagado":
                    tree.insert("", tk.END, values=valores, tags=("pagado",))
                else:
                    tree.insert("", tk.END, values=valores, tags=("vencido",))
            
            tree.tag_configure('activo', foreground='green')
            tree.tag_configure('pagado', foreground='blue')
            tree.tag_configure('vencido', foreground='red')
        
        def mostrar_detalles(event=None):
            nonlocal prestamo_actual_id
            seleccion = tree.selection()
            if not seleccion:
                return
            item = tree.item(seleccion[0])
            valores = item['values']
            if valores[0] == "No hay préstamos":
                return
            prestamo_actual_id = valores[0]
            query = """
                SELECT saldo_pendiente, cuota_mensual, fecha_proximo_pago, 
                    interes_mensual, monto_prestado, cuotas_totales, cuotas_restantes
                FROM prestamos WHERE id_prestamo = ?
            """
            prestamo = self.db.fetch_one(query, (prestamo_actual_id,))
            if prestamo:
                saldo = float(prestamo[0]) if prestamo[0] is not None else 0
                cuota = float(prestamo[1]) if prestamo[1] is not None else 0
                fecha = str(prestamo[2]) if prestamo[2] else "No definida"
                interes = float(prestamo[3]) if prestamo[3] is not None else 0
                monto = float(prestamo[4]) if prestamo[4] is not None else 0
                lbl_solicitante.config(text=f"Solicitante: {valores[1]}")
                lbl_monto.config(text=f"Monto: ${monto:,.2f}")
                lbl_interes.config(text=f"Interés: {interes}%")
                lbl_saldo.config(text=f"Saldo pendiente: ${saldo:,.2f}")
                lbl_proximo.config(text=f"Próxima cuota: ${cuota:,.2f}")
                lbl_fecha.config(text=f"Fecha próximo pago: {fecha}")
        
        def registrar_pago():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Error", "Seleccione un préstamo primero")
                return
            
            # Obtener datos actuales del préstamo
            query = """
                SELECT saldo_pendiente, cuota_mensual, interes_mensual, 
                    monto_prestado, cuotas_restantes
                FROM prestamos WHERE id_prestamo = ?
            """
            prestamo = self.db.fetch_one(query, (prestamo_actual_id,))
            if not prestamo:
                messagebox.showerror("Error", "Préstamo no encontrado")
                return
            
            saldo_actual = float(prestamo[0]) if prestamo[0] is not None else 0
            cuota_actual = float(prestamo[1]) if prestamo[1] is not None else 0
            interes_porcentaje = float(prestamo[2]) if prestamo[2] is not None else 0
            monto_original = float(prestamo[3]) if prestamo[3] is not None else 0
            cuotas_restantes = int(prestamo[4]) if prestamo[4] is not None else 0
            
            if saldo_actual <= 0:
                messagebox.showinfo("Información", "Este préstamo ya está pagado")
                return
            
            # Ventana de pago mejorada
            pago_win = tk.Toplevel(ventana)
            pago_win.title("Registrar Pago")
            pago_win.geometry("500x550")
            pago_win.transient()
            pago_win.grab_set()
            
            main_frame_pago = ttk.Frame(pago_win, padding="20")
            main_frame_pago.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(main_frame_pago, text="REGISTRAR PAGO", font=("Arial", 14, "bold")).pack(pady=(0, 20))
            
            # Mostrar información del préstamo
            info_frame = ttk.LabelFrame(main_frame_pago, text="Información del Préstamo", padding="10")
            info_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(info_frame, text=f"Saldo actual: ${saldo_actual:,.2f}", font=("Arial", 11, "bold")).pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Cuota actual: ${cuota_actual:,.2f}").pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Interés: {interes_porcentaje}% sobre saldo").pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Cuotas restantes: {cuotas_restantes}").pack(anchor=tk.W)
            
            # Tipo de pago
            tipo_frame = ttk.LabelFrame(main_frame_pago, text="Tipo de Pago", padding="10")
            tipo_frame.pack(fill=tk.X, pady=10)
            
            tipo_pago_var = tk.StringVar(value="cuota")
            ttk.Radiobutton(tipo_frame, text="Pago de cuota (interés + abono a capital)", 
                        variable=tipo_pago_var, value="cuota").pack(anchor=tk.W)
            ttk.Radiobutton(tipo_frame, text="Abono extraordinario a capital (solo reduce saldo)", 
                        variable=tipo_pago_var, value="abono").pack(anchor=tk.W)
            
            # Monto a pagar
            monto_frame = ttk.LabelFrame(main_frame_pago, text="Monto a Pagar", padding="10")
            monto_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(monto_frame, text="Monto ($):").pack(anchor=tk.W)
            entry_monto = ttk.Entry(monto_frame, font=("Arial", 12))
            entry_monto.pack(fill=tk.X, pady=5)
            
            # Calcular interés del período (para pago de cuota)
            interes_periodo = saldo_actual * (interes_porcentaje / 100)
            lbl_desglose = tk.Label(monto_frame, text=f"Interés del período: ${interes_periodo:,.2f}", 
                                    font=("Arial", 10), fg="blue")
            lbl_desglose.pack(anchor=tk.W, pady=5)
            
            def actualizar_desglose(*args):
                try:
                    monto_pagado = float(entry_monto.get().replace(',', ''))
                    if tipo_pago_var.get() == "cuota":
                        if monto_pagado >= interes_periodo:
                            abono_capital = monto_pagado - interes_periodo
                            nuevo_saldo = saldo_actual - abono_capital
                            lbl_desglose.config(
                                text=f"Interés pagado: ${interes_periodo:,.2f} | Abono a capital: ${abono_capital:,.2f} | Nuevo saldo: ${nuevo_saldo:,.2f}",
                                fg="green")
                        else:
                            lbl_desglose.config(
                                text=f"⚠️ El pago no cubre el interés (${interes_periodo:,.2f}). El saldo no se reduce.",
                                fg="red")
                    else:
                        nuevo_saldo = saldo_actual - monto_pagado
                        lbl_desglose.config(text=f"Nuevo saldo después del abono: ${nuevo_saldo:,.2f}", fg="green")
                except:
                    lbl_desglose.config(text="Ingrese un monto válido", fg="red")
            
            entry_monto.bind("<KeyRelease>", lambda e: actualizar_desglose())
            
            # Forma de pago
            forma_frame = ttk.LabelFrame(main_frame_pago, text="Forma de Pago", padding="10")
            forma_frame.pack(fill=tk.X, pady=10)
            
            combo_forma = ttk.Combobox(forma_frame, values=["Efectivo", "Transferencia", "Débito", "Cheque"], 
                                    state="readonly")
            combo_forma.pack(fill=tk.X)
            combo_forma.set("Efectivo")
            
            # Fecha de pago
            fecha_frame = ttk.LabelFrame(main_frame_pago, text="Fecha de Pago", padding="10")
            fecha_frame.pack(fill=tk.X, pady=10)
            
            entry_fecha = ttk.Entry(fecha_frame)
            entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
            entry_fecha.pack(fill=tk.X)
            
            def guardar_pago():
                try:
                    monto_pagado = float(entry_monto.get().replace(',', ''))
                    forma_pago = combo_forma.get()
                    fecha_pago = entry_fecha.get()
                    tipo_pago = tipo_pago_var.get()
                    
                    if monto_pagado <= 0:
                        messagebox.showwarning("Error", "Ingrese un monto válido")
                        return
                    
                    if tipo_pago == "cuota":
                        # Pago de cuota: primero se paga interés, lo demás abona a capital
                        if monto_pagado >= interes_periodo:
                            interes_pagado = interes_periodo
                            abono_capital = monto_pagado - interes_periodo
                            nuevo_saldo = saldo_actual - abono_capital
                            nuevas_cuotas_restantes = max(0, cuotas_restantes - 1)
                        else:
                            # Pago insuficiente, solo se registra como abono a interés
                            interes_pagado = monto_pagado
                            abono_capital = 0
                            nuevo_saldo = saldo_actual
                            nuevas_cuotas_restantes = cuotas_restantes
                            messagebox.showwarning("Advertencia", 
                                f"El pago (${monto_pagado:,.2f}) no cubre el interés del período (${interes_periodo:,.2f}).\n"
                                f"Se registrará como abono a interés. El saldo no se reduce.")
                    else:
                        # Abono extraordinario a capital
                        interes_pagado = 0
                        abono_capital = monto_pagado
                        nuevo_saldo = saldo_actual - abono_capital
                        nuevas_cuotas_restantes = cuotas_restantes
                        if nuevo_saldo < 0:
                            nuevo_saldo = 0
                    
                    nuevo_estado = "pagado" if nuevo_saldo <= 0 else "activo"
                    
                    # Recalcular nueva cuota si el saldo cambió
                    if nuevo_saldo > 0 and nuevas_cuotas_restantes > 0:
                        nueva_cuota = nuevo_saldo / nuevas_cuotas_restantes
                    else:
                        nueva_cuota = cuota_actual
                    
                    # Calcular nueva fecha de próxima cuota
                    fecha_actual = datetime.strptime(fecha_pago, "%Y-%m-%d")
                    fecha_proxima = fecha_actual + timedelta(days=30)
                    
                    # Insertar pago
                    self.db.execute("""
                        INSERT INTO pagos_prestamo 
                        (id_prestamo, monto_pagado, fecha_pago, forma_pago, 
                        interes_pagado, abono_capital, saldo_restante)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (prestamo_actual_id, monto_pagado, fecha_pago, forma_pago,
                        interes_pagado, abono_capital, nuevo_saldo))
                    
                    # Actualizar préstamo
                    self.db.execute("""
                        UPDATE prestamos 
                        SET saldo_pendiente = ?, cuota_mensual = ?, 
                            cuotas_restantes = ?, estado = ?, fecha_proximo_pago = ?
                        WHERE id_prestamo = ?
                    """, (nuevo_saldo, nueva_cuota, nuevas_cuotas_restantes, 
                        nuevo_estado, fecha_proxima.strftime("%Y-%m-%d"), prestamo_actual_id))
                    
                    messagebox.showinfo("Éxito", 
                        f"Pago registrado correctamente\n\n"
                        f"Monto pagado: ${monto_pagado:,.2f}\n"
                        f"Interés pagado: ${interes_pagado:,.2f}\n"
                        f"Abono a capital: ${abono_capital:,.2f}\n"
                        f"Nuevo saldo: ${nuevo_saldo:,.2f}")
                    
                    pago_win.destroy()
                    cargar_prestamos()
                    mostrar_detalles()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar pago: {str(e)}")
            
            ttk.Button(main_frame_pago, text="REGISTRAR PAGO", command=guardar_pago, width=20).pack(pady=20)
            ttk.Button(main_frame_pago, text="CANCELAR", command=pago_win.destroy, width=20).pack(pady=5)

            def modificar_prestamo():
                seleccion = tree.selection()
                if not seleccion:
                    messagebox.showwarning("Error", "Seleccione un préstamo para modificar")
                    return
                item = tree.item(seleccion[0])
                valores = item['values']
                if valores[0] == "No hay préstamos":
                    return
                prestamo_id = valores[0]
                
                # Obtener datos actuales
                query = "SELECT monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, estado FROM prestamos WHERE id_prestamo = ?"
                prestamo = self.db.fetch_one(query, (prestamo_id,))
                if not prestamo:
                    return
                
                # Ventana de modificación
                mod_win = tk.Toplevel(ventana)
                mod_win.title("Modificar Préstamo")
                mod_win.geometry("400x400")
                mod_win.transient()
                mod_win.grab_set()
                
                ttk.Label(mod_win, text="MODIFICAR PRÉSTAMO", font=("Arial", 14, "bold")).pack(pady=10)
                
                frame = ttk.Frame(mod_win, padding="20")
                frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(frame, text="Monto ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
                entry_monto = ttk.Entry(frame)
                entry_monto.grid(row=0, column=1, pady=5)
                entry_monto.insert(0, str(prestamo[0]))
                
                ttk.Label(frame, text="Interés (%):").grid(row=1, column=0, sticky=tk.W, pady=5)
                entry_interes = ttk.Entry(frame)
                entry_interes.grid(row=1, column=1, pady=5)
                entry_interes.insert(0, str(prestamo[1]))
                
                ttk.Label(frame, text="Cuota ($):").grid(row=2, column=0, sticky=tk.W, pady=5)
                entry_cuota = ttk.Entry(frame)
                entry_cuota.grid(row=2, column=1, pady=5)
                entry_cuota.insert(0, str(prestamo[2]))
                
                ttk.Label(frame, text="Cuotas totales:").grid(row=3, column=0, sticky=tk.W, pady=5)
                entry_cuotas_totales = ttk.Entry(frame)
                entry_cuotas_totales.grid(row=3, column=1, pady=5)
                entry_cuotas_totales.insert(0, str(prestamo[3]))
                
                ttk.Label(frame, text="Cuotas restantes:").grid(row=4, column=0, sticky=tk.W, pady=5)
                entry_cuotas_restantes = ttk.Entry(frame)
                entry_cuotas_restantes.grid(row=4, column=1, pady=5)
                entry_cuotas_restantes.insert(0, str(prestamo[4]))
                
                ttk.Label(frame, text="Estado:").grid(row=5, column=0, sticky=tk.W, pady=5)
                combo_estado = ttk.Combobox(frame, values=["activo", "pagado", "vencido"], state="readonly")
                combo_estado.grid(row=5, column=1, pady=5)
                combo_estado.set(prestamo[5])
                
                def guardar_modificacion():
                    try:
                        monto = float(entry_monto.get())
                        interes = float(entry_interes.get())
                        cuota = float(entry_cuota.get())
                        cuotas_totales = int(entry_cuotas_totales.get())
                        cuotas_restantes = int(entry_cuotas_restantes.get())
                        estado = combo_estado.get()
                        
                        query = """
                            UPDATE prestamos SET 
                                monto_prestado = ?, interes_mensual = ?, cuota_mensual = ?,
                                cuotas_totales = ?, cuotas_restantes = ?, estado = ?
                            WHERE id_prestamo = ?
                        """
                        if self.db.execute(query, (monto, interes, cuota, cuotas_totales, cuotas_restantes, estado, prestamo_id)):
                            messagebox.showinfo("Éxito", "Préstamo modificado correctamente")
                            mod_win.destroy()
                            cargar_prestamos()
                            mostrar_detalles()
                        else:
                            messagebox.showerror("Error", "No se pudo modificar")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error: {str(e)}")
                
                ttk.Button(frame, text="Guardar Cambios", command=guardar_modificacion).grid(row=6, column=0, columnspan=2, pady=20)


            def eliminar_prestamo():
                seleccion = tree.selection()
                if not seleccion:
                    messagebox.showwarning("Error", "Seleccione un préstamo")
                    return
                item = tree.item(seleccion[0])
                valores = item['values']
                if valores[0] == "No hay préstamos":
                    return
                prestamo_id = valores[0]
                solicitante = valores[1]
                
                respuesta = messagebox.askyesno("Confirmar", f"¿Eliminar préstamo #{prestamo_id} de {solicitante}?")
                if respuesta:
                    try:
                        self.db.execute("DELETE FROM pagos_prestamo WHERE id_prestamo = ?", (prestamo_id,))
                        self.db.execute("DELETE FROM prestamos WHERE id_prestamo = ?", (prestamo_id,))
                        messagebox.showinfo("Éxito", "Préstamo eliminado")
                        cargar_prestamos()
                        mostrar_detalles()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error: {str(e)}")
        
        # ========== BOTONES ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Registrar Pago", command=registrar_pago, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Modificar", command=modificar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=eliminar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=lambda: [cargar_prestamos(), mostrar_detalles()], width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=ventana.destroy, width=14).pack(side=tk.RIGHT, padx=5)
        
        tree.bind("<<TreeviewSelect>>", mostrar_detalles)
        cargar_prestamos()

    def prestamos_vencidos(self):
            """Mostrar préstamos vencidos - Compatible con PostgreSQL y SQLite"""
            from datetime import date

            ventana = tk.Toplevel()
            ventana.title("Préstamos Vencidos")
            ventana.geometry("1000x500")

            main_frame = ttk.Frame(ventana, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(main_frame, text="PRÉSTAMOS VENCIDOS", font=("Arial", 14, "bold")).pack(pady=10)

            columns = ("ID", "Socio", "Teléfono", "Monto", "Saldo", "Cuota", "Días Vencido")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=130)

            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 1. Obtener préstamos activos
            query = """
                SELECT p.id_prestamo, 
                    COALESCE(s.nombre || ' ' || s.apellido, p.nombre_externo) as socio_nombre,
                    COALESCE(s.celular, p.celular_externo) as telefono,
                    p.monto_prestado, 
                    p.saldo_pendiente, 
                    p.cuota_mensual,
                    p.fecha_proximo_pago
                FROM prestamos p
                LEFT JOIN socios s ON p.id_socio = s.id_socio
                WHERE p.estado = 'activo'
            """
            prestamos = self.db.fetch_all(query)
            
            hoy = date.today()
            for p in prestamos:
                fecha_prox_str = p[6]
                if fecha_prox_str:
                    try:
                        fecha_prox = datetime.strptime(fecha_prox_str, "%Y-%m-%d").date()
                        if fecha_prox < hoy:
                            dias_vencido = (hoy - fecha_prox).days
                            
                            monto = float(p[3]) if p[3] is not None else 0
                            saldo = float(p[4]) if p[4] is not None else 0
                            cuota = float(p[5]) if p[5] is not None else 0
                            
                            tree.insert("", tk.END, values=(
                                p[0], p[1], p[2], 
                                f"${monto:,.2f}", 
                                f"${saldo:,.2f}", 
                                f"${cuota:,.2f}", 
                                f"{dias_vencido} días"
                            ))
                    except Exception as e:
                        print(f"Error procesando fecha {fecha_prox_str}: {e}")

            ttk.Button(main_frame, text="Actualizar", command=lambda: [tree.delete(*tree.get_children()), self.prestamos_vencidos()]).pack(pady=10)

    def registrar_pago(self):
        """Registrar pago de préstamo (acceso directo)"""
        self.gestionar_prestamos()