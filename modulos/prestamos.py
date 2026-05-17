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
        ventana.geometry("800x750")
        ventana.minsize(750, 650)
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
        
        # ========== TIPO DE PRÉSTAMO ==========
        tipo_frame = ttk.LabelFrame(main_frame, text="TIPO DE PRÉSTAMO", padding="10")
        tipo_frame.pack(fill=tk.X, pady=5)
        
        tipo_var = tk.StringVar(value="socio")
        ttk.Radiobutton(tipo_frame, text="Préstamo a Socio (registrado)", variable=tipo_var, value="socio", command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(tipo_frame, text="Préstamo a Particular (no socio)", variable=tipo_var, value="particular", command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
        
        # ========== FRAME PARA SOCIO (registrado) ==========
        socio_frame = ttk.LabelFrame(main_frame, text="SELECCIONAR SOCIO", padding="10")
        
        # Frame de búsqueda
        search_frame = ttk.Frame(socio_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        entry_buscar = ttk.Entry(search_frame, width=30)
        entry_buscar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="🔍 Buscar", command=lambda: buscar_socios()).pack(side=tk.LEFT, padx=5)
        
        # Treeview de socios
        tree_frame = ttk.Frame(socio_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("ID", "Código", "Nombre", "Cédula", "Celular")
        tree_socios = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
        for col in columns:
            tree_socios.heading(col, text=col)
            tree_socios.column(col, width=120)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree_socios.yview)
        tree_socios.configure(yscroll=scroll_y.set)
        tree_socios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        lbl_socio_seleccionado = tk.Label(socio_frame, text="⚡ Socio seleccionado: Ninguno", font=("Arial", 10, "bold"), fg="green")
        lbl_socio_seleccionado.pack(anchor=tk.W, pady=5)
        
        # ========== FRAME PARA PARTICULAR ==========
        particular_frame = ttk.LabelFrame(main_frame, text="DATOS DEL PARTICULAR", padding="10")
        
        # Datos del particular
        ttk.Label(particular_frame, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_nombre_particular = ttk.Entry(particular_frame, width=35)
        entry_nombre_particular.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(particular_frame, text="Cédula:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_cedula_particular = ttk.Entry(particular_frame, width=35)
        entry_cedula_particular.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(particular_frame, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_celular_particular = ttk.Entry(particular_frame, width=35)
        entry_celular_particular.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Socio recomendador
        ttk.Label(particular_frame, text="Recomendado por (socio):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        frame_rec = ttk.Frame(particular_frame)
        frame_rec.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        entry_buscar_rec = ttk.Entry(frame_rec, width=25)
        entry_buscar_rec.pack(side=tk.LEFT)
        ttk.Button(frame_rec, text="Buscar", command=lambda: buscar_recomendador()).pack(side=tk.LEFT, padx=5)
        
        tree_rec_frame = ttk.Frame(particular_frame)
        tree_rec_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        columns_rec = ("ID", "Código", "Nombre", "Cédula")
        tree_recomendador = ttk.Treeview(tree_rec_frame, columns=columns_rec, show="headings", height=3)
        for col in columns_rec:
            tree_recomendador.heading(col, text=col)
            tree_recomendador.column(col, width=110)
        
        scroll_rec = ttk.Scrollbar(tree_rec_frame, orient=tk.VERTICAL, command=tree_recomendador.yview)
        tree_recomendador.configure(yscroll=scroll_rec.set)
        tree_recomendador.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_rec.pack(side=tk.RIGHT, fill=tk.Y)
        
        lbl_recomendador = tk.Label(particular_frame, text="⚡ Recomendador: Ninguno", font=("Arial", 10, "bold"), fg="blue")
        lbl_recomendador.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # ========== DATOS DEL PRÉSTAMO ==========
        datos_frame = ttk.LabelFrame(main_frame, text="DATOS DEL PRÉSTAMO", padding="10")
        datos_frame.pack(fill=tk.X, pady=10)
        
        # Monto
        ttk.Label(datos_frame, text="Monto del préstamo ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_monto = ttk.Entry(datos_frame)
        entry_monto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_monto.insert(0, "0")
        
        # Interés mensual
        ttk.Label(datos_frame, text="Interés mensual (%):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_interes = ttk.Entry(datos_frame)
        entry_interes.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_interes.insert(0, "10")
        
        # Cuotas
        ttk.Label(datos_frame, text="Número de cuotas:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_cuotas = ttk.Entry(datos_frame)
        entry_cuotas.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_cuotas.insert(0, "12")
        
        # Abono a capital (opcional)
        ttk.Label(datos_frame, text="Abono inicial a capital ($):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry_abono_inicial = ttk.Entry(datos_frame)
        entry_abono_inicial.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_abono_inicial.insert(0, "0")
        
        # Cuota mensual sugerida
        ttk.Label(datos_frame, text="Cuota mensual sugerida ($):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        entry_cuota_sugerida = ttk.Entry(datos_frame)
        entry_cuota_sugerida.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_cuota_sugerida.insert(0, "0")
        
        # Fecha inicial
        ttk.Label(datos_frame, text="Fecha inicial del préstamo:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha_inicial = ttk.Entry(datos_frame)
        entry_fecha_inicial.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_fecha_inicial.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Fecha de primera cuota
        ttk.Label(datos_frame, text="Fecha de primera cuota:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha_primera = ttk.Entry(datos_frame)
        entry_fecha_primera.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        fecha_defecto = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        entry_fecha_primera.insert(0, fecha_defecto)
        
        # Observaciones
        ttk.Label(datos_frame, text="Observaciones:").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        text_obs = tk.Text(datos_frame, height=3, width=35)
        text_obs.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # ========== FUNCIONES ==========
        socio_seleccionado_id = None
        socio_seleccionado_nombre = None
        recomendador_id = None
        recomendador_nombre = None
        
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
                query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula FROM socios WHERE estado = 'activo' ORDER BY nombre LIMIT 30"
                socios = self.db.fetch_all(query)
            else:
                query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula FROM socios WHERE estado = 'activo' AND (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?) ORDER BY nombre LIMIT 30"
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
        
        entry_abono_inicial.bind('<FocusOut>', formatear_monto(entry_abono_inicial))
        entry_abono_inicial.bind('<FocusIn>', lambda e: entry_abono_inicial.delete(0, tk.END))
        
        def registrar_prestamo():
            try:
                monto_texto = entry_monto.get().replace(',', '')
                monto = float(monto_texto) if monto_texto else 0
                interes = float(entry_interes.get())
                cuotas = int(entry_cuotas.get())
                abono_inicial = float(entry_abono_inicial.get().replace(',', '')) if entry_abono_inicial.get() else 0
                cuota_sugerida = float(entry_cuota_sugerida.get().replace(',', '')) if entry_cuota_sugerida.get() else 0
                fecha_inicial = entry_fecha_inicial.get()
                fecha_primera = entry_fecha_primera.get()
                obs = text_obs.get("1.0", tk.END).strip()
                
                if monto <= 0:
                    messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                    return
                
                # Calcular saldo después de abono inicial
                saldo_inicial = monto - abono_inicial
                if saldo_inicial < 0:
                    saldo_inicial = 0
                
                # Calcular cuota mensual
                interes_mensual_calc = saldo_inicial * (interes / 100)
                if cuota_sugerida > 0:
                    cuota = cuota_sugerida
                else:
                    cuota = (saldo_inicial / cuotas) + interes_mensual_calc
                
                fecha_inicial_dt = datetime.strptime(fecha_inicial, "%Y-%m-%d")
                fecha_primera_dt = datetime.strptime(fecha_primera, "%Y-%m-%d")
                
                if tipo_var.get() == "socio":
                    if not socio_seleccionado_id:
                        messagebox.showwarning("Error", "Seleccione un socio")
                        return
                    
                    query = """INSERT INTO prestamos 
                        (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                        cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                        saldo_pendiente, observaciones, estado, es_externo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 0)"""
                    
                    self.db.execute(query, (socio_seleccionado_id, monto, interes, cuota, cuotas, cuotas,
                                            fecha_inicial, fecha_primera, saldo_inicial, obs))
                    messagebox.showinfo("Éxito", f"Préstamo aprobado para socio: {socio_seleccionado_nombre}")
                    
                else:
                    nombre = entry_nombre_particular.get().strip()
                    cedula = entry_cedula_particular.get().strip()
                    celular = entry_celular_particular.get().strip()
                    
                    if not nombre or not cedula or not celular:
                        messagebox.showwarning("Error", "Complete todos los datos del particular")
                        return
                    
                    query = """INSERT INTO prestamos 
                        (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                        cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                        saldo_pendiente, observaciones, estado, es_externo, nombre_externo,
                        cedula_externa, celular_externo, id_recomendador)
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 1, ?, ?, ?, ?)"""
                    
                    self.db.execute(query, (monto, interes, cuota, cuotas, cuotas, fecha_inicial,
                                            fecha_primera, saldo_inicial, obs,
                                            nombre, cedula, celular, recomendador_id))
                    messagebox.showinfo("Éxito", f"Préstamo aprobado para particular: {nombre}")
                
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
    
    def gestionar_prestamos(self):
        """Gestionar préstamos existentes - Con opciones de modificar y eliminar"""
        ventana = tk.Toplevel()
        ventana.title("Gestión de Préstamos")
        ventana.geometry("1300x700")
        ventana.minsize(900, 500)
        
        # ========== LISTA DE PRÉSTAMOS ==========
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Socio", "Monto", "Interés", "Cuota", "Tipo", "Cuotas", "Restantes", "Saldo", "Estado", "Fecha")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 50, "Socio": 200, "Monto": 120, "Interés": 70, "Cuota": 120, 
                    "Tipo": 80, "Cuotas": 70, "Restantes": 70, "Saldo": 120, "Estado": 90, "Fecha": 100}
        
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
        
        lbl_socio = tk.Label(detalles_frame, text="Socio: ", font=("Arial", 11, "bold"))
        lbl_socio.pack(anchor=tk.W, pady=2)
        
        lbl_monto = tk.Label(detalles_frame, text="Monto: $0", font=("Arial", 10))
        lbl_monto.pack(anchor=tk.W, pady=2)
        
        lbl_interes = tk.Label(detalles_frame, text="Interés mensual: 0%", font=("Arial", 10))
        lbl_interes.pack(anchor=tk.W, pady=2)
        
        lbl_saldo = tk.Label(detalles_frame, text="Saldo pendiente: $0", font=("Arial", 11, "bold"), fg="red")
        lbl_saldo.pack(anchor=tk.W, pady=2)
        
        lbl_proximo = tk.Label(detalles_frame, text="Próxima cuota: $0", font=("Arial", 10))
        lbl_proximo.pack(anchor=tk.W, pady=2)
        
        lbl_fecha = tk.Label(detalles_frame, text="Fecha próximo pago: ", font=("Arial", 10))
        lbl_fecha.pack(anchor=tk.W, pady=2)
        
        # ========== BOTONES ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        def cargar_prestamos():
            for item in tree.get_children():
                tree.delete(item)
            
            query = """
            SELECT p.id_prestamo, s.nombre || ' ' || s.apellido,
                p.monto_prestado, p.interes_mensual, p.cuota_mensual, p.tipo_cuota,
                p.cuotas_totales, p.cuotas_restantes, p.saldo_pendiente, p.estado,
                p.fecha_prestamo
            FROM prestamos p
            JOIN socios s ON p.id_socio = s.id_socio
            ORDER BY p.fecha_prestamo DESC
            """
            prestamos = self.db.fetch_all(query)
            
            if not prestamos:
                tree.insert("", tk.END, values=("No hay préstamos", "", "", "", "", "", "", "", "", "", ""))
                return
            
            for p in prestamos:
                monto = float(p[2]) if p[2] is not None else 0
                interes = float(p[3]) if p[3] is not None else 0
                cuota = float(p[4]) if p[4] is not None else 0
                saldo = float(p[8]) if p[8] is not None else 0
                valores = (p[0], p[1], f"${monto:,.2f}", f"{interes}%", f"${cuota:,.2f}",
                        p[5] if p[5] else "Mensual", p[6], p[7], f"${saldo:,.2f}", p[9], p[10])
                
                if p[9] == "activo":
                    tree.insert("", tk.END, values=valores, tags=("activo",))
                elif p[9] == "pagado":
                    tree.insert("", tk.END, values=valores, tags=("pagado",))
                else:
                    tree.insert("", tk.END, values=valores, tags=("vencido",))
            
            tree.tag_configure('activo', foreground='green')
            tree.tag_configure('pagado', foreground='blue')
            tree.tag_configure('vencido', foreground='red')
        
        def mostrar_detalles(event=None):
            seleccion = tree.selection()
            if not seleccion:
                return
            item = tree.item(seleccion[0])
            valores = item['values']
            if valores[0] == "No hay préstamos":
                return
            prestamo_id = valores[0]
            query = "SELECT saldo_pendiente, cuota_mensual, fecha_proximo_pago, interes_mensual, monto_prestado FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(query, (prestamo_id,))
            if prestamo:
                saldo = float(prestamo[0]) if prestamo[0] is not None else 0
                cuota = float(prestamo[1]) if prestamo[1] is not None else 0
                fecha = str(prestamo[2]) if prestamo[2] else "No definida"
                interes = float(prestamo[3]) if prestamo[3] is not None else 0
                monto = float(prestamo[4]) if prestamo[4] is not None else 0
                lbl_socio.config(text=f"Socio: {valores[1]}")
                lbl_monto.config(text=f"Monto: ${monto:,.2f}")
                lbl_interes.config(text=f"Interés mensual: {interes}%")
                lbl_saldo.config(text=f"Saldo pendiente: ${saldo:,.2f}")
                lbl_proximo.config(text=f"Próxima cuota: ${cuota:,.2f}")
                lbl_fecha.config(text=f"Fecha próximo pago: {fecha}")
        
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
            query = "SELECT monto_prestado, interes_mensual, cuota_mensual, tipo_cuota, cuotas_totales, cuotas_restantes, estado FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(query, (prestamo_id,))
            if not prestamo:
                return
            
            # Ventana de modificación
            mod_win = tk.Toplevel(ventana)
            mod_win.title("Modificar Préstamo")
            mod_win.geometry("400x450")
            mod_win.transient()
            mod_win.grab_set()
            
            ttk.Label(mod_win, text="MODIFICAR PRÉSTAMO", font=("Arial", 14, "bold")).pack(pady=10)
            
            frame = ttk.Frame(mod_win, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Monto ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
            entry_monto = ttk.Entry(frame)
            entry_monto.grid(row=0, column=1, pady=5)
            entry_monto.insert(0, str(prestamo[0]))
            
            ttk.Label(frame, text="Interés mensual (%):").grid(row=1, column=0, sticky=tk.W, pady=5)
            entry_interes = ttk.Entry(frame)
            entry_interes.grid(row=1, column=1, pady=5)
            entry_interes.insert(0, str(prestamo[1]))
            
            ttk.Label(frame, text="Cuota mensual ($):").grid(row=2, column=0, sticky=tk.W, pady=5)
            entry_cuota = ttk.Entry(frame)
            entry_cuota.grid(row=2, column=1, pady=5)
            entry_cuota.insert(0, str(prestamo[2]))
            
            ttk.Label(frame, text="Tipo de cuota:").grid(row=3, column=0, sticky=tk.W, pady=5)
            combo_tipo = ttk.Combobox(frame, values=["Mensual", "Quincenal"], state="readonly")
            combo_tipo.grid(row=3, column=1, pady=5)
            combo_tipo.set(prestamo[3] if prestamo[3] else "Mensual")
            
            ttk.Label(frame, text="Cuotas totales:").grid(row=4, column=0, sticky=tk.W, pady=5)
            entry_cuotas_totales = ttk.Entry(frame)
            entry_cuotas_totales.grid(row=4, column=1, pady=5)
            entry_cuotas_totales.insert(0, str(prestamo[4]))
            
            ttk.Label(frame, text="Cuotas restantes:").grid(row=5, column=0, sticky=tk.W, pady=5)
            entry_cuotas_restantes = ttk.Entry(frame)
            entry_cuotas_restantes.grid(row=5, column=1, pady=5)
            entry_cuotas_restantes.insert(0, str(prestamo[5]))
            
            ttk.Label(frame, text="Estado:").grid(row=6, column=0, sticky=tk.W, pady=5)
            combo_estado = ttk.Combobox(frame, values=["activo", "pagado", "vencido"], state="readonly")
            combo_estado.grid(row=6, column=1, pady=5)
            combo_estado.set(prestamo[6])
            
            def guardar_modificacion():
                try:
                    monto = float(entry_monto.get())
                    interes = float(entry_interes.get())
                    cuota = float(entry_cuota.get())
                    tipo = combo_tipo.get()
                    cuotas_totales = int(entry_cuotas_totales.get())
                    cuotas_restantes = int(entry_cuotas_restantes.get())
                    estado = combo_estado.get()
                    
                    query = """
                    UPDATE prestamos SET 
                        monto_prestado = ?, interes_mensual = ?, cuota_mensual = ?,
                        tipo_cuota = ?, cuotas_totales = ?, cuotas_restantes = ?, estado = ?
                    WHERE id_prestamo = ?
                    """
                    if self.db.execute(query, (monto, interes, cuota, tipo, cuotas_totales, cuotas_restantes, estado, prestamo_id)):
                        messagebox.showinfo("Éxito", "Préstamo modificado correctamente")
                        mod_win.destroy()
                        cargar_prestamos()
                        mostrar_detalles()
                    else:
                        messagebox.showerror("Error", "No se pudo modificar el préstamo")
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {str(e)}")
            
            ttk.Button(frame, text="Guardar Cambios", command=guardar_modificacion).grid(row=7, column=0, columnspan=2, pady=20)
        
        def eliminar_prestamo():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Error", "Seleccione un préstamo para eliminar")
                return
            item = tree.item(seleccion[0])
            valores = item['values']
            if valores[0] == "No hay préstamos":
                return
            prestamo_id = valores[0]
            socio = valores[1]
            
            respuesta = messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar préstamo #{prestamo_id} de {socio}?\nEsta acción NO se puede deshacer.")
            if respuesta:
                try:
                    # Primero eliminar pagos asociados
                    self.db.execute("DELETE FROM pagos_prestamo WHERE id_prestamo = ?", (prestamo_id,))
                    # Luego eliminar el préstamo
                    self.db.execute("DELETE FROM prestamos WHERE id_prestamo = ?", (prestamo_id,))
                    messagebox.showinfo("Éxito", "Préstamo eliminado correctamente")
                    cargar_prestamos()
                    mostrar_detalles()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
        
        def registrar_pago():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            item = tree.item(seleccion[0])
            valores = item['values']
            if valores[0] == "No hay préstamos":
                return
            prestamo_id = valores[0]
            socio = valores[1]
            query = "SELECT saldo_pendiente, cuota_mensual FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(query, (prestamo_id,))
            if prestamo:
                saldo = float(prestamo[0]) if prestamo[0] is not None else 0
                cuota = float(prestamo[1]) if prestamo[1] is not None else 0
                monto = simpledialog.askfloat("Registrar Pago", 
                                            f"Socio: {socio}\nSaldo: ${saldo:,.2f}\nCuota sugerida: ${cuota:,.2f}\n\nMonto a pagar: $",
                                            minvalue=0.01, maxvalue=saldo)
                if monto:
                    nuevo_saldo = saldo - monto
                    nuevo_estado = "pagado" if nuevo_saldo <= 0 else "activo"
                    self.db.execute("INSERT INTO pagos_prestamo (id_prestamo, monto_pagado, fecha_pago, forma_pago, saldo_restante) VALUES (?, ?, date('now'), 'Efectivo', ?)",
                                (prestamo_id, monto, nuevo_saldo))
                    self.db.execute("UPDATE prestamos SET saldo_pendiente = ?, estado = ? WHERE id_prestamo = ?",
                                (nuevo_saldo, nuevo_estado, prestamo_id))
                    messagebox.showinfo("Éxito", f"Pago registrado\nNuevo saldo: ${nuevo_saldo:,.2f}")
                    cargar_prestamos()
                    mostrar_detalles()
        
        # Botones
        ttk.Button(btn_frame, text="Registrar Pago", command=registrar_pago, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Modificar", command=modificar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=eliminar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=lambda: [cargar_prestamos(), mostrar_detalles()], width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=ventana.destroy, width=14).pack(side=tk.RIGHT, padx=5)
        
        tree.bind("<<TreeviewSelect>>", mostrar_detalles)
        cargar_prestamos()
    
    def prestamos_vencidos(self):
        """Mostrar préstamos vencidos - Compatible con PostgreSQL y SQLite"""
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
        
        # Consulta compatible con PostgreSQL y SQLite
        # Para PostgreSQL usamos EXTRACT, para SQLite usamos julianday
        # Como database.py ya maneja la conversión, usamos una consulta estándar
        
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
        AND p.fecha_proximo_pago < CURRENT_DATE
        ORDER BY p.fecha_proximo_pago ASC
        """
        
        prestamos = self.db.fetch_all(query)
        
        from datetime import date
        
        for p in prestamos:
            monto = float(p[3]) if p[3] is not None else 0
            saldo = float(p[4]) if p[4] is not None else 0
            cuota = float(p[5]) if p[5] is not None else 0
            fecha_prox = p[6]
            
            # Calcular días vencidos manualmente
            dias_vencido = 0
            if fecha_prox:
                try:
                    fecha_prox_date = datetime.strptime(fecha_prox, "%Y-%m-%d").date()
                    dias_vencido = (date.today() - fecha_prox_date).days
                    if dias_vencido < 0:
                        dias_vencido = 0
                except:
                    pass
            
            tree.insert("", tk.END, values=(
                p[0], p[1], p[2], 
                f"${monto:,.2f}", 
                f"${saldo:,.2f}", 
                f"${cuota:,.2f}", 
                f"{dias_vencido} días"
            ))
        
        ttk.Button(main_frame, text="Actualizar", command=lambda: [tree.delete(*tree.get_children()), self.prestamos_vencidos()]).pack(pady=10)
        
    def registrar_pago(self):
        """Registrar pago de préstamo (acceso directo)"""
        self.gestionar_prestamos()