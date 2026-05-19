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
        
        tk.Label(main_frame, text="NUEVO PRÉSTAMO", font=("Arial", 18, "bold"), fg="navy").pack(pady=(0, 20))
        
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
        
        # Fecha del préstamo
        ttk.Label(datos_frame, text="Fecha del préstamo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha = ttk.Entry(datos_frame)
        entry_fecha.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Monto
        ttk.Label(datos_frame, text="Monto ($):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_monto = ttk.Entry(datos_frame)
        entry_monto.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_monto.insert(0, "0")
        
        # Interés (%)
        ttk.Label(datos_frame, text="Interés (%):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        combo_interes = ttk.Combobox(datos_frame, values=["5%", "10%"], state="readonly", width=10)
        combo_interes.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        combo_interes.set("5%")
        
        # Plazo
        ttk.Label(datos_frame, text="Plazo (meses):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry_plazo = ttk.Entry(datos_frame)
        entry_plazo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_plazo.insert(0, "12")
        
        # Cuota calculada
        ttk.Label(datos_frame, text="Cuota mensual:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        lbl_cuota = tk.Label(datos_frame, text="$0.00", font=("Arial", 12, "bold"), fg="blue")
        lbl_cuota.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Fecha de primera cuota
        ttk.Label(datos_frame, text="Fecha de primera cuota:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha_pago = ttk.Entry(datos_frame)
        entry_fecha_pago.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        fecha_defecto = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        entry_fecha_pago.insert(0, fecha_defecto)
        
        # Observaciones
        ttk.Label(datos_frame, text="Observaciones:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        text_obs = tk.Text(datos_frame, height=3, width=35)
        text_obs.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Calcular cuota automáticamente
        def calcular_cuota(*args):
            try:
                monto_texto = entry_monto.get().replace(',', '')
                monto = float(monto_texto) if monto_texto else 0
                interes = int(combo_interes.get().replace('%', ''))
                plazo = int(entry_plazo.get()) if entry_plazo.get() else 0
                
                if monto > 0 and plazo > 0:
                    interes_valor = monto * (interes / 100)
                    total = monto + interes_valor
                    cuota = total / plazo
                    lbl_cuota.config(text=f"${cuota:,.2f}")
                else:
                    lbl_cuota.config(text="$0.00")
            except:
                lbl_cuota.config(text="$0.00")
        
        entry_monto.bind("<KeyRelease>", calcular_cuota)
        combo_interes.bind("<<ComboboxSelected>>", calcular_cuota)
        entry_plazo.bind("<KeyRelease>", calcular_cuota)
        
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
                fecha_prestamo = entry_fecha.get()
                monto_texto = entry_monto.get().replace(',', '')
                monto = float(monto_texto) if monto_texto else 0
                interes = int(combo_interes.get().replace('%', ''))
                plazo = int(entry_plazo.get())
                fecha_pago = entry_fecha_pago.get()
                obs = text_obs.get("1.0", tk.END).strip()
                
                if monto <= 0:
                    messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                    return
                
                if plazo <= 0:
                    messagebox.showwarning("Error", "El plazo debe ser mayor a cero")
                    return
                
                # Calcular cuota
                interes_valor = monto * (interes / 100)
                total = monto + interes_valor
                cuota = total / plazo
                
                if tipo_var.get() == "socio":
                    if not socio_seleccionado_id:
                        messagebox.showwarning("Error", "Seleccione un socio")
                        return
                    
                    query = """INSERT INTO prestamos 
                        (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                         cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                         saldo_pendiente, observaciones, estado, es_externo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', FALSE)"""
                    
                    self.db.execute(query, (socio_seleccionado_id, monto, interes, cuota, plazo, plazo,
                                            fecha_prestamo, fecha_pago, total, obs))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para socio: {socio_seleccionado_nombre}")
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
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', TRUE, ?, ?, ?)"""
                    
                    self.db.execute(query, (monto, interes, cuota, plazo, plazo, fecha_prestamo,
                                            fecha_pago, total, obs, nombre, celular, recomendador_id))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para particular: {nombre}")
                
                ventana.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {str(e)}")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="✅ APROBAR PRÉSTAMO", command=registrar_prestamo, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ CANCELAR", command=ventana.destroy, width=20).pack(side=tk.LEFT, padx=10)
        
        # Inicializar
        buscar_socios()
        toggle_tipo()
        calcular_cuota()
    
    def gestionar_prestamos(self):
        """Gestionar préstamos existentes"""
        ventana = tk.Toplevel()
        ventana.title("Gestión de Préstamos")
        ventana.geometry("1300x700")
        ventana.minsize(900, 500)
        
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ("ID", "Código", "Solicitante", "Monto", "Interés", "Cuota", "Plazo", "Restantes", "Saldo", "Estado", "Fecha")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 60, "Código": 100, "Solicitante": 200, "Monto": 120, "Interés": 80, "Cuota": 120, 
                      "Plazo": 70, "Restantes": 80, "Saldo": 130, "Estado": 90, "Fecha": 110}
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 100))
        
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Detalles
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
        
        lbl_cuota = tk.Label(detalles_frame, text="Próxima cuota: $0", font=("Arial", 10))
        lbl_cuota.pack(anchor=tk.W, pady=2)
        
        lbl_fecha = tk.Label(detalles_frame, text="Fecha próximo pago: ", font=("Arial", 10))
        lbl_fecha.pack(anchor=tk.W, pady=2)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        prestamo_actual_id = None
        
        def cargar_prestamos():
            for item in tree.get_children():
                tree.delete(item)
            
            # La consulta debe devolver las columnas en este ORDEN:
            # 0: id_prestamo
            # 1: codigo_prestamo
            # 2: solicitante
            # 3: monto_prestado
            # 4: interes_mensual
            # 5: cuota_mensual
            # 6: cuotas_totales
            # 7: cuotas_restantes
            # 8: saldo_pendiente
            # 9: estado
            # 10: fecha_prestamo
            query = """
                SELECT p.id_prestamo, 
                    p.codigo_prestamo,
                    CASE WHEN p.es_externo = TRUE THEN p.nombre_externo 
                            ELSE COALESCE(s.nombre || ' ' || s.apellido, 'Particular')
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
                tree.insert("", tk.END, values=("No hay préstamos", "", "", "", "", "", "", "", "", "", ""))
                return
            
            for p in prestamos:
                # Extraer valores con formato
                id_prestamo = p[0]
                codigo = p[1] if p[1] else "S/C"
                solicitante = p[2] if p[2] else "Particular"
                monto = float(p[3]) if p[3] else 0
                interes = float(p[4]) if p[4] else 0
                cuota = float(p[5]) if p[5] else 0
                cuotas_totales = int(p[6]) if p[6] else 0
                cuotas_restantes = int(p[7]) if p[7] else 0
                saldo = float(p[8]) if p[8] else 0
                estado = p[9] if p[9] else "activo"
                fecha = p[10] if p[10] else ""
                
                # Crear tupla de valores con formato de moneda
                valores = (
                    id_prestamo,
                    codigo,
                    solicitante,
                    f"${monto:,.2f}",
                    f"{interes}%",
                    f"${cuota:,.2f}",
                    cuotas_totales,
                    cuotas_restantes,
                    f"${saldo:,.2f}",
                    estado,
                    fecha
                )
                
                if estado == "activo":
                    tree.insert("", tk.END, values=valores, tags=("activo",))
                elif estado == "pagado":
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
                       interes_mensual, monto_prestado
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
                lbl_cuota.config(text=f"Próxima cuota: ${cuota:,.2f}")
                lbl_fecha.config(text=f"Fecha próximo pago: {fecha}")
        
        def registrar_pago():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            
            # ========== FUNCIONES DE FORMATEO ==========
            def formatear_miles(entry):
                def _formatear(event=None):
                    try:
                        texto = entry.get()
                        if texto:
                            # Eliminar formato anterior
                            limpio = texto.replace('$', '').replace(',', '').strip()
                            if limpio and limpio.replace('.', '', 1).isdigit():
                                num = float(limpio)
                                entry.delete(0, tk.END)
                                entry.insert(0, f"{num:,.0f}")
                    except:
                        pass
                return _formatear

            def quitar_formato(entry):
                def _quitar(event=None):
                    try:
                        texto = entry.get()
                        if texto:
                            limpio = texto.replace('$', '').replace(',', '').strip()
                            entry.delete(0, tk.END)
                            entry.insert(0, limpio)
                    except:
                        pass
                return _quitar
            
            # Obtener datos actuales del préstamo
            q = """SELECT saldo_pendiente, cuota_mensual, interes_mensual, 
                        cuotas_restantes, fecha_proximo_pago, codigo_prestamo
                FROM prestamos WHERE id_prestamo = ?"""
            prestamo = self.db.fetch_one(q, (prestamo_actual_id,))
            if not prestamo:
                messagebox.showerror("Error", "Préstamo no encontrado")
                return
            
            capital_pendiente = float(prestamo[0]) if prestamo[0] else 0
            cuota_actual = float(prestamo[1]) if prestamo[1] else 0
            interes_porcentaje = float(prestamo[2]) if prestamo[2] else 0
            cuotas_restantes = int(prestamo[3]) if prestamo[3] else 0
            fecha_prox_pago = prestamo[4] if prestamo[4] else ""
            codigo = prestamo[5] if prestamo[5] else "S/C"
            
            if capital_pendiente <= 0:
                messagebox.showinfo("Información", "Este préstamo ya está pagado")
                return
            
            # Calcular interés del período sobre el CAPITAL pendiente
            interes_periodo = capital_pendiente * (interes_porcentaje / 100)
            
            # Ventana de pago
            pago_win = tk.Toplevel(ventana)
            pago_win.title(f"Registrar Pago - {codigo}")
            pago_win.geometry("500x600")
            pago_win.minsize(450, 500)
            pago_win.transient()
            pago_win.grab_set()
            
            # Contenedor con scroll
            main_container = ttk.Frame(pago_win)
            main_container.pack(fill=tk.BOTH, expand=True)
            
            canvas = tk.Canvas(main_container, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            main_frame_pago = ttk.Frame(scrollable_frame, padding="20")
            main_frame_pago.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(main_frame_pago, text="REGISTRAR PAGO", font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            # ========== INFORMACIÓN DEL PRÉSTAMO ==========
            info_frame = ttk.LabelFrame(main_frame_pago, text="Información del Préstamo", padding="10")
            info_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(info_frame, text=f"Código: {codigo}", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Capital pendiente: ${capital_pendiente:,.2f}", 
                    font=("Arial", 12, "bold"), fg="red").pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Interés del período ({interes_porcentaje}%): ${interes_periodo:,.2f}", 
                    font=("Arial", 10), fg="blue").pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Cuota actual: ${cuota_actual:,.2f}").pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Cuotas restantes: {cuotas_restantes}").pack(anchor=tk.W)
            tk.Label(info_frame, text=f"Próximo vencimiento: {fecha_prox_pago}").pack(anchor=tk.W)
            
            # ========== TIPO DE PAGO ==========
            tipo_frame = ttk.LabelFrame(main_frame_pago, text="Tipo de Pago", padding="10")
            tipo_frame.pack(fill=tk.X, pady=5)
            
            tipo_pago_var = tk.StringVar(value="normal")
            ttk.Radiobutton(tipo_frame, text="Pago normal (interés + abono a capital)", 
                        variable=tipo_pago_var, value="normal").pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(tipo_frame, text="Pago de solo intereses", 
                        variable=tipo_pago_var, value="solo_interes").pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(tipo_frame, text="Abono a capital (con intereses del período)", 
                        variable=tipo_pago_var, value="abono").pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(tipo_frame, text="Pago total (liquidar todo)", 
                        variable=tipo_pago_var, value="total").pack(anchor=tk.W, pady=2)
            
            # ========== CAMPOS DE PAGO ==========
            pago_frame = ttk.LabelFrame(main_frame_pago, text="Datos del Pago", padding="10")
            pago_frame.pack(fill=tk.X, pady=5)
            
            # Monto total
            ttk.Label(pago_frame, text="Monto total a pagar ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            entry_monto = ttk.Entry(pago_frame, width=20, font=("Arial", 11))
            entry_monto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            entry_monto.bind('<FocusOut>', formatear_miles(entry_monto))
            entry_monto.bind('<FocusIn>', quitar_formato(entry_monto))
            
            # Abono a capital (solo para tipo abono)
            ttk.Label(pago_frame, text="Abono a capital ($):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            entry_abono = ttk.Entry(pago_frame, width=20)
            entry_abono.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            entry_abono.insert(0, "0")
            entry_abono.config(state="disabled")
            entry_abono.bind('<FocusOut>', formatear_miles(entry_abono))
            entry_abono.bind('<FocusIn>', quitar_formato(entry_abono))
            
            # Fecha de pago
            ttk.Label(pago_frame, text="Fecha de pago:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            entry_fecha = ttk.Entry(pago_frame, width=20)
            entry_fecha.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            # Forma de pago
            ttk.Label(pago_frame, text="Forma de pago:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            combo_forma = ttk.Combobox(pago_frame, values=["Efectivo", "Transferencia", "Débito", "Cheque"], 
                                    state="readonly", width=18)
            combo_forma.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
            combo_forma.set("Efectivo")
            
            # Observaciones
            ttk.Label(pago_frame, text="Observaciones:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
            text_obs = tk.Text(pago_frame, height=3, width=25)
            text_obs.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Desglose
            lbl_desglose = tk.Label(pago_frame, text="", font=("Arial", 9), justify=tk.LEFT, fg="green")
            lbl_desglose.grid(row=5, column=0, columnspan=2, pady=10)
            
            def actualizar_campos(*args):
                tipo = tipo_pago_var.get()
                entry_monto.config(state="normal")
                entry_abono.config(state="disabled")
                entry_monto.delete(0, tk.END)
                
                if tipo == "normal":
                    entry_monto.insert(0, f"{cuota_actual:,.0f}".replace(',', ''))
                    lbl_desglose.config(text=f"💡 Pago normal:\n   Interés: ${interes_periodo:,.2f}\n   Abono a capital: ${cuota_actual - interes_periodo:,.2f}")
                elif tipo == "solo_interes":
                    entry_monto.insert(0, f"{interes_periodo:,.0f}".replace(',', ''))
                    lbl_desglose.config(text=f"💡 Pago de solo intereses:\n   No se reduce el capital\n   Próximo interés: ${interes_periodo:,.2f}")
                elif tipo == "abono":
                    entry_abono.config(state="normal")
                    entry_monto.delete(0, tk.END)
                    lbl_desglose.config(text=f"💡 Abono a capital:\n   Debe pagar también los intereses del período (${interes_periodo:,.2f})")
                else:  # total
                    entry_monto.insert(0, f"{capital_pendiente + interes_periodo:,.0f}".replace(',', ''))
                    lbl_desglose.config(text=f"💡 Pago total:\n   Se liquidará el préstamo completamente")
            
            def calcular_abono(*args):
                if tipo_pago_var.get() == "abono":
                    try:
                        abono = float(entry_abono.get().replace(',', '')) if entry_abono.get() else 0
                        if abono > 0:
                            total = interes_periodo + abono
                            entry_monto.delete(0, tk.END)
                            entry_monto.insert(0, f"{total:,.0f}".replace(',', ''))
                            nuevo_capital = capital_pendiente - abono
                            if nuevo_capital < 0:
                                nuevo_capital = 0
                            nuevo_interes = nuevo_capital * (interes_porcentaje / 100)
                            nueva_cuota = nuevo_capital + nuevo_interes
                            lbl_desglose.config(text=f"💡 Abono a capital:\n"
                                                    f"   Interés: ${interes_periodo:,.2f}\n"
                                                    f"   Abono: ${abono:,.2f}\n"
                                                    f"   Nuevo capital: ${nuevo_capital:,.2f}\n"
                                                    f"   Nuevo interés: ${nuevo_interes:,.2f}\n"
                                                    f"   Nueva cuota: ${nueva_cuota:,.2f}")
                    except:
                        pass
            
            tipo_pago_var.trace_add('write', lambda *args: actualizar_campos())
            entry_abono.bind("<KeyRelease>", lambda e: calcular_abono())
            
            actualizar_campos()
            
            def guardar_pago():
                try:
                    tipo_pago = tipo_pago_var.get()
                    fecha_pago = entry_fecha.get()
                    forma_pago = combo_forma.get()
                    observaciones = text_obs.get("1.0", tk.END).strip()
                    
                    if tipo_pago == "normal":
                        monto_pagado = cuota_actual
                        interes_pagado = interes_periodo
                        abono_capital = monto_pagado - interes_periodo
                        nuevo_capital = capital_pendiente - abono_capital
                        if nuevo_capital < 0:
                            nuevo_capital = 0
                        # RECÁLCULO CORRECTO: interés sobre el NUEVO capital
                        nuevo_interes = nuevo_capital * (interes_porcentaje / 100) if nuevo_capital > 0 else 0
                        nueva_cuota = nuevo_capital + nuevo_interes
                        nuevas_cuotas = cuotas_restantes - 1 if nuevo_capital > 0 else 0
                        
                    elif tipo_pago == "solo_interes":
                        monto_pagado = interes_periodo
                        interes_pagado = interes_periodo
                        abono_capital = 0
                        nuevo_capital = capital_pendiente
                        # El interés sigue siendo el mismo porque el capital no cambió
                        nueva_cuota = cuota_actual
                        nuevas_cuotas = cuotas_restantes
                        
                    elif tipo_pago == "abono":
                        abono_capital = float(entry_abono.get().replace(',', '')) if entry_abono.get() else 0
                        if abono_capital <= 0:
                            messagebox.showwarning("Error", "Ingrese un monto para abonar a capital")
                            return
                        if abono_capital > capital_pendiente:
                            messagebox.showwarning("Error", f"El abono no puede superar el capital pendiente (${capital_pendiente:,.2f})")
                            return
                        monto_pagado = interes_periodo + abono_capital
                        interes_pagado = interes_periodo
                        nuevo_capital = capital_pendiente - abono_capital
                        if nuevo_capital < 0:
                            nuevo_capital = 0
                        # RECÁLCULO CORRECTO: interés sobre el NUEVO capital
                        nuevo_interes = nuevo_capital * (interes_porcentaje / 100) if nuevo_capital > 0 else 0
                        nueva_cuota = nuevo_capital + nuevo_interes
                        nuevas_cuotas = cuotas_restantes
                        
                    else:  # total
                        monto_pagado = capital_pendiente + interes_periodo
                        interes_pagado = interes_periodo
                        abono_capital = capital_pendiente
                        nuevo_capital = 0
                        nueva_cuota = 0
                        nuevas_cuotas = 0
                    
                    nuevo_estado = "pagado" if nuevo_capital <= 0 else "activo"
                    
                    fecha_actual = datetime.strptime(fecha_pago, "%Y-%m-%d")
                    fecha_proxima = fecha_actual + timedelta(days=30)
                    
                    # Insertar pago
                    self.db.execute("""
                        INSERT INTO pagos_prestamo 
                        (id_prestamo, monto_pagado, fecha_pago, forma_pago, 
                        interes_pagado, abono_capital, saldo_restante, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (prestamo_actual_id, monto_pagado, fecha_pago, forma_pago,
                        interes_pagado, abono_capital, nuevo_capital, observaciones))
                    
                    # Actualizar préstamo
                    self.db.execute("""
                        UPDATE prestamos 
                        SET saldo_pendiente = ?, cuota_mensual = ?, 
                            cuotas_restantes = ?, estado = ?, fecha_proximo_pago = ?
                        WHERE id_prestamo = ?
                    """, (nuevo_capital, nueva_cuota, nuevas_cuotas, 
                        nuevo_estado, fecha_proxima.strftime("%Y-%m-%d"), prestamo_actual_id))
                    
                    # Mostrar resumen con el nuevo interés calculado
                    resumen = f"✅ Pago registrado\n\n"
                    resumen += f"💰 Monto pagado: ${monto_pagado:,.2f}\n"
                    resumen += f"💸 Interés pagado: ${interes_pagado:,.2f}\n"
                    resumen += f"🏦 Abono a capital: ${abono_capital:,.2f}\n"
                    resumen += f"📊 Nuevo capital: ${nuevo_capital:,.2f}\n"
                    if nuevo_capital > 0:
                        nuevo_interes_mostrar = nuevo_capital * (interes_porcentaje / 100)
                        resumen += f"🔄 Nuevo interés próximo período: ${nuevo_interes_mostrar:,.2f}\n"
                        resumen += f"🔄 Nueva cuota: ${nueva_cuota:,.2f}\n"
                    
                    messagebox.showinfo("Éxito", resumen)
                    pago_win.destroy()
                    cargar_prestamos()
                    mostrar_detalles()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {str(e)}")

            # Botones
            btn_frame = ttk.Frame(main_frame_pago)
            btn_frame.pack(fill=tk.X, pady=20)
            
            ttk.Button(btn_frame, text="✅ REGISTRAR PAGO", command=guardar_pago, width=18).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="❌ CANCELAR", command=pago_win.destroy, width=18).pack(side=tk.LEFT, padx=10)

        def modificar_prestamo():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            
            # Obtener datos
            query = "SELECT monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, estado FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(query, (prestamo_actual_id,))
            if not prestamo:
                return
            
            mod_win = tk.Toplevel(ventana)
            mod_win.title("Modificar Préstamo")
            mod_win.geometry("400x400")
            mod_win.transient()
            mod_win.grab_set()
            
            ttk.Label(mod_win, text="MODIFICAR PRÉSTAMO", font=("Arial", 14, "bold")).pack(pady=10)
            
            frame = ttk.Frame(mod_win, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Monto:").grid(row=0, column=0, sticky=tk.W, pady=5)
            entry_monto = ttk.Entry(frame)
            entry_monto.grid(row=0, column=1, pady=5)
            entry_monto.insert(0, str(prestamo[0]))
            
            ttk.Label(frame, text="Interés (%):").grid(row=1, column=0, sticky=tk.W, pady=5)
            entry_interes = ttk.Entry(frame)
            entry_interes.grid(row=1, column=1, pady=5)
            entry_interes.insert(0, str(prestamo[1]))
            
            ttk.Label(frame, text="Cuota:").grid(row=2, column=0, sticky=tk.W, pady=5)
            entry_cuota = ttk.Entry(frame)
            entry_cuota.grid(row=2, column=1, pady=5)
            entry_cuota.insert(0, str(prestamo[2]))
            
            ttk.Label(frame, text="Cuotas totales:").grid(row=3, column=0, sticky=tk.W, pady=5)
            entry_ct = ttk.Entry(frame)
            entry_ct.grid(row=3, column=1, pady=5)
            entry_ct.insert(0, str(prestamo[3]))
            
            ttk.Label(frame, text="Cuotas restantes:").grid(row=4, column=0, sticky=tk.W, pady=5)
            entry_cr = ttk.Entry(frame)
            entry_cr.grid(row=4, column=1, pady=5)
            entry_cr.insert(0, str(prestamo[4]))
            
            ttk.Label(frame, text="Estado:").grid(row=5, column=0, sticky=tk.W, pady=5)
            combo_estado = ttk.Combobox(frame, values=["activo", "pagado", "vencido"], state="readonly")
            combo_estado.grid(row=5, column=1, pady=5)
            combo_estado.set(prestamo[5])
            
            def guardar():
                try:
                    self.db.execute("""
                        UPDATE prestamos SET 
                            monto_prestado = ?, interes_mensual = ?, cuota_mensual = ?,
                            cuotas_totales = ?, cuotas_restantes = ?, estado = ?
                        WHERE id_prestamo = ?
                    """, (float(entry_monto.get()), float(entry_interes.get()), float(entry_cuota.get()),
                          int(entry_ct.get()), int(entry_cr.get()), combo_estado.get(), prestamo_actual_id))
                    messagebox.showinfo("Éxito", "Préstamo modificado")
                    mod_win.destroy()
                    cargar_prestamos()
                    mostrar_detalles()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            ttk.Button(frame, text="Guardar", command=guardar).grid(row=6, column=0, columnspan=2, pady=20)
        
        def eliminar_prestamo():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            
            if messagebox.askyesno("Confirmar", "¿Eliminar este préstamo? No se puede deshacer."):
                try:
                    self.db.execute("DELETE FROM pagos_prestamo WHERE id_prestamo = ?", (prestamo_actual_id,))
                    self.db.execute("DELETE FROM prestamos WHERE id_prestamo = ?", (prestamo_actual_id,))
                    messagebox.showinfo("Éxito", "Préstamo eliminado")
                    cargar_prestamos()
                    mostrar_detalles()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        
        ttk.Button(btn_frame, text="Registrar Pago", command=registrar_pago, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Modificar", command=modificar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=eliminar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=lambda: [cargar_prestamos(), mostrar_detalles()], width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=ventana.destroy, width=14).pack(side=tk.RIGHT, padx=5)
        
        tree.bind("<<TreeviewSelect>>", mostrar_detalles)
        cargar_prestamos()
    
    def prestamos_vencidos(self):
        """Mostrar préstamos vencidos"""
        ventana = tk.Toplevel()
        ventana.title("Préstamos Vencidos")
        ventana.geometry("1000x500")
        
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="PRÉSTAMOS VENCIDOS", font=("Arial", 14, "bold")).pack(pady=10)
        
        columns = ("ID", "Solicitante", "Teléfono", "Monto", "Saldo", "Cuota", "Días Vencido")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Obtener préstamos activos con fecha vencida
        from datetime import date
        hoy = date.today()
        
        query = """
            SELECT p.id_prestamo, 
                   CASE WHEN p.es_externo = 1 THEN p.nombre_externo ELSE s.nombre || ' ' || s.apellido END,
                   CASE WHEN p.es_externo = 1 THEN p.celular_externo ELSE s.celular END,
                   p.monto_prestado, p.saldo_pendiente, p.cuota_mensual,
                   p.fecha_proximo_pago
            FROM prestamos p
            LEFT JOIN socios s ON p.id_socio = s.id_socio
            WHERE p.estado = 'activo'
        """
        prestamos = self.db.fetch_all(query)
        
        for p in prestamos:
            fecha_prox = p[6]
            if fecha_prox:
                try:
                    fecha_prox_date = datetime.strptime(fecha_prox, "%Y-%m-%d").date()
                    if fecha_prox_date < hoy:
                        dias = (hoy - fecha_prox_date).days
                        monto = float(p[3]) if p[3] else 0
                        saldo = float(p[4]) if p[4] else 0
                        cuota = float(p[5]) if p[5] else 0
                        tree.insert("", tk.END, values=(
                            p[0], p[1], p[2], 
                            f"${monto:,.2f}", f"${saldo:,.2f}", f"${cuota:,.2f}", 
                            f"{dias} días"
                        ))
                except:
                    pass
        
        ttk.Button(main_frame, text="Actualizar", command=lambda: [tree.delete(*tree.get_children()), self.prestamos_vencidos()]).pack(pady=10)
    
    def registrar_pago(self):
        """Registrar pago de préstamo (acceso directo)"""
        self.gestionar_prestamos()