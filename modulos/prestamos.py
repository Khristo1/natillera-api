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
        ventana.geometry("750x700")
        ventana.minsize(700, 600)
        ventana.transient()
        ventana.grab_set()
        
        main_frame = ttk.Frame(ventana, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="NUEVO PRÉSTAMO", 
                font=("Arial", 16, "bold"), fg="navy").pack(pady=(0, 20))
        
        # ========== TIPO DE PRÉSTAMO ==========
        tipo_frame = ttk.LabelFrame(main_frame, text="1. TIPO DE PRÉSTAMO", padding="10")
        tipo_frame.pack(fill=tk.X, pady=10)
        
        tipo_var = tk.StringVar(value="socio")
        ttk.Radiobutton(tipo_frame, text="Préstamo a Socio (registrado)", variable=tipo_var, value="socio", command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(tipo_frame, text="Préstamo a Particular (no socio)", variable=tipo_var, value="particular", command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
        
        # ========== FRAME PARA SOCIO ==========
        socio_frame = ttk.LabelFrame(main_frame, text="2. SELECCIONAR SOCIO", padding="10")
        socio_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        search_frame = ttk.Frame(socio_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Buscar socio:").pack(side=tk.LEFT, padx=5)
        entry_buscar = ttk.Entry(search_frame, width=30)
        entry_buscar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="🔍 Buscar", command=lambda: buscar_socios()).pack(side=tk.LEFT, padx=5)
        
        tree_socio_frame = ttk.Frame(socio_frame)
        tree_socio_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("ID", "Código", "Nombre", "Cédula", "Celular")
        tree_socios = ttk.Treeview(tree_socio_frame, columns=columns, show="headings", height=5)
        for col in columns:
            tree_socios.heading(col, text=col)
            tree_socios.column(col, width=100)
        
        scroll_y = ttk.Scrollbar(tree_socio_frame, orient=tk.VERTICAL, command=tree_socios.yview)
        tree_socios.configure(yscroll=scroll_y.set)
        tree_socios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        lbl_socio_seleccionado = tk.Label(socio_frame, text="⚡ Socio seleccionado: Ninguno", font=("Arial", 10, "bold"), fg="green")
        lbl_socio_seleccionado.pack(anchor=tk.W, pady=5)
        
        # ========== FRAME PARA PARTICULAR ==========
        particular_frame = ttk.LabelFrame(main_frame, text="2. DATOS DEL PARTICULAR", padding="10")
        
        # Campos para particular
        ttk.Label(particular_frame, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_nombre_particular = ttk.Entry(particular_frame, width=35)
        entry_nombre_particular.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(particular_frame, text="Cédula:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_cedula_particular = ttk.Entry(particular_frame, width=35)
        entry_cedula_particular.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(particular_frame, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_celular_particular = ttk.Entry(particular_frame, width=35)
        entry_celular_particular.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Frame para socio recomendador
        ttk.Label(particular_frame, text="Recomendado por (socio):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        frame_recomendador = ttk.Frame(particular_frame)
        frame_recomendador.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        entry_recomendador_buscar = ttk.Entry(frame_recomendador, width=25)
        entry_recomendador_buscar.pack(side=tk.LEFT)
        ttk.Button(frame_recomendador, text="Buscar", command=lambda: buscar_recomendador()).pack(side=tk.LEFT, padx=5)
        
        tree_recomendador_frame = ttk.Frame(particular_frame)
        tree_recomendador_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        columns_rec = ("ID", "Código", "Nombre", "Cédula")
        tree_recomendador = ttk.Treeview(tree_recomendador_frame, columns=columns_rec, show="headings", height=3)
        for col in columns_rec:
            tree_recomendador.heading(col, text=col)
            tree_recomendador.column(col, width=100)
        
        scroll_rec = ttk.Scrollbar(tree_recomendador_frame, orient=tk.VERTICAL, command=tree_recomendador.yview)
        tree_recomendador.configure(yscroll=scroll_rec.set)
        tree_recomendador.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_rec.pack(side=tk.RIGHT, fill=tk.Y)
        
        lbl_recomendador = tk.Label(particular_frame, text="⚡ Recomendador: Ninguno", font=("Arial", 10, "bold"), fg="blue")
        lbl_recomendador.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # ========== FRAME DATOS DEL PRÉSTAMO ==========
        datos_frame = ttk.LabelFrame(main_frame, text="3. DATOS DEL PRÉSTAMO", padding="10")
        datos_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(datos_frame, text="Monto ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_monto = ttk.Entry(datos_frame)
        entry_monto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_monto.insert(0, "0")
        
        ttk.Label(datos_frame, text="Interés mensual (%):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_interes = ttk.Entry(datos_frame)
        entry_interes.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_interes.insert(0, "10")
        
        ttk.Label(datos_frame, text="Cuota mensual sugerida ($):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_cuota = ttk.Entry(datos_frame)
        entry_cuota.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_cuota.insert(0, "0")
        ttk.Label(datos_frame, text="(0 para calcular automática)", font=("Arial", 8), fg="gray").grid(row=3, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(datos_frame, text="Plazo (meses):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        entry_plazo = ttk.Entry(datos_frame)
        entry_plazo.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_plazo.insert(0, "12")
        
        ttk.Label(datos_frame, text="Fecha préstamo:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha = ttk.Entry(datos_frame)
        entry_fecha.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(datos_frame, text="Observaciones:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        text_obs = tk.Text(datos_frame, height=3, width=35)
        text_obs.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
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
            texto = entry_recomendador_buscar.get().strip()
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
        
        def formatear_monto(event=None):
            try:
                texto = entry_monto.get()
                if texto:
                    limpio = texto.replace('$', '').replace(',', '').strip()
                    if limpio and limpio.replace('.', '', 1).isdigit():
                        num = float(limpio)
                        if num > 0:
                            entry_monto.delete(0, tk.END)
                            entry_monto.insert(0, f"{num:,.0f}")
            except:
                pass
        
        entry_monto.bind('<FocusOut>', formatear_monto)
        entry_monto.bind('<FocusIn>', lambda e: entry_monto.delete(0, tk.END))
        
        def registrar():
            try:
                monto_texto = entry_monto.get().replace(',', '')
                monto = float(monto_texto) if monto_texto else 0
                interes = float(entry_interes.get())
                plazo = int(entry_plazo.get())
                fecha = entry_fecha.get()
                cuota_sugerida = float(entry_cuota.get().replace(',', '')) if entry_cuota.get() else 0
                obs = text_obs.get("1.0", tk.END).strip()
                
                if monto <= 0:
                    messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                    return
                
                # Calcular cuota
                interes_mes = monto * (interes / 100)
                if cuota_sugerida > 0:
                    cuota = cuota_sugerida
                else:
                    cuota = (monto / plazo) + interes_mes
                
                fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
                fecha_prox = fecha_dt + timedelta(days=30)
                
                if tipo_var.get() == "socio":
                    # Préstamo a socio existente
                    if not socio_seleccionado_id:
                        messagebox.showwarning("Error", "Seleccione un socio")
                        return
                    
                    query = """INSERT INTO prestamos 
                        (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                        cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                        saldo_pendiente, observaciones, estado, es_externo, nombre_externo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 0, NULL)"""
                    
                    self.db.execute(query, (socio_seleccionado_id, monto, interes, cuota, plazo, plazo, 
                                            fecha, fecha_prox.strftime("%Y-%m-%d"), monto, obs))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para socio: {socio_seleccionado_nombre}")
                    
                else:
                    # Préstamo a particular
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
                    
                    self.db.execute(query, (monto, interes, cuota, plazo, plazo, fecha,
                                            fecha_prox.strftime("%Y-%m-%d"), monto, obs,
                                            nombre, cedula, celular, recomendador_id))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para particular: {nombre}")
                
                ventana.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {str(e)}")
        
        # ========== BOTONES ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="📝 REGISTRAR PRÉSTAMO", command=registrar, width=20).pack(side=tk.LEFT, padx=10)
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
        """Mostrar préstamos vencidos"""
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
        
        query = """
        SELECT p.id_prestamo, s.nombre || ' ' || s.apellido, s.celular,
               p.monto_prestado, p.saldo_pendiente, p.cuota_mensual,
               julianday('now') - julianday(p.fecha_proximo_pago) as dias_vencido
        FROM prestamos p
        JOIN socios s ON p.id_socio = s.id_socio
        WHERE p.estado = 'activo' AND p.fecha_proximo_pago < date('now')
        ORDER BY dias_vencido DESC
        """
        prestamos = self.db.fetch_all(query)
        
        for p in prestamos:
            monto = float(p[3]) if p[3] is not None else 0
            saldo = float(p[4]) if p[4] is not None else 0
            cuota = float(p[5]) if p[5] is not None else 0
            dias = int(p[6]) if p[6] is not None else 0
            tree.insert("", tk.END, values=(p[0], p[1], p[2], f"${monto:,.2f}", f"${saldo:,.2f}", f"${cuota:,.2f}", f"{dias} días"))
        
        ttk.Button(main_frame, text="Actualizar", command=lambda: [tree.delete(*tree.get_children()), self.prestamos_vencidos()]).pack(pady=10)
    
    def registrar_pago(self):
        """Registrar pago de préstamo (acceso directo)"""
        self.gestionar_prestamos()