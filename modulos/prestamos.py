# modulos/prestamos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

class ModuloPrestamos:
    def __init__(self, database):
        self.db = database

    def nuevo_prestamo(self):
        """Ventana para nuevo préstamo - Socio o Particular (con scroll)"""
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

        # ========== TIPO DE SOLICITANTE ==========
        tipo_frame = ttk.LabelFrame(main_frame, text="TIPO DE SOLICITANTE", padding="10")
        tipo_frame.pack(fill=tk.X, pady=5)

        tipo_var = tk.StringVar(value="socio")
        ttk.Radiobutton(tipo_frame, text="Socio (registrado)", variable=tipo_var, value="socio",
                       command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(tipo_frame, text="Particular (no socio)", variable=tipo_var, value="particular",
                       command=lambda: toggle_tipo()).pack(anchor=tk.W, pady=2)

        # ========== DATOS DEL SOCIO ==========
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

        lbl_socio_seleccionado = tk.Label(socio_frame, text="⚡ Socio seleccionado: Ninguno", font=("Arial", 10, "bold"), fg="green")
        lbl_socio_seleccionado.pack(anchor=tk.W, pady=5)

        # ========== DATOS DEL PARTICULAR ==========
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

        lbl_recomendador = tk.Label(particular_frame, text="⚡ Recomendador: Ninguno", font=("Arial", 10, "bold"), fg="blue")
        lbl_recomendador.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.W)

        # ========== DATOS DEL PRÉSTAMO ==========
        datos_frame = ttk.LabelFrame(main_frame, text="DATOS DEL PRÉSTAMO", padding="10")
        datos_frame.pack(fill=tk.X, pady=10)

        ttk.Label(datos_frame, text="Fecha del préstamo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha = ttk.Entry(datos_frame)
        entry_fecha.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(datos_frame, text="Monto ($):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_monto = ttk.Entry(datos_frame)
        entry_monto.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_monto.insert(0, "0")

        ttk.Label(datos_frame, text="Interés (%):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        combo_interes = ttk.Combobox(datos_frame, values=["5%", "10%"], state="readonly", width=10)
        combo_interes.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        combo_interes.set("5%")

        ttk.Label(datos_frame, text="Plazo (meses):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry_plazo = ttk.Entry(datos_frame)
        entry_plazo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_plazo.insert(0, "12")

        ttk.Label(datos_frame, text="Cuota mensual:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        lbl_cuota = tk.Label(datos_frame, text="$0.00", font=("Arial", 12, "bold"), fg="blue")
        lbl_cuota.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(datos_frame, text="Fecha de primera cuota:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        entry_fecha_pago = ttk.Entry(datos_frame)
        entry_fecha_pago.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_fecha_pago.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))

        ttk.Label(datos_frame, text="Observaciones:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        text_obs = tk.Text(datos_frame, height=3, width=35)
        text_obs.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        # ========== FUNCIONES ==========
        def calcular_cuota(*args):
            try:
                monto = float(entry_monto.get().replace(',', ''))
                interes = int(combo_interes.get().replace('%', ''))
                plazo = int(entry_plazo.get())
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

        def registrar_prestamo():
            try:
                fecha_prestamo = entry_fecha.get()
                monto = float(entry_monto.get().replace(',', ''))
                interes = int(combo_interes.get().replace('%', ''))
                plazo = int(entry_plazo.get())
                fecha_pago = entry_fecha_pago.get()
                obs = text_obs.get("1.0", tk.END).strip()
                if monto <= 0 or plazo <= 0:
                    messagebox.showwarning("Error", "Monto y plazo deben ser mayores a cero")
                    return
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
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 0)"""
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
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 1, ?, ?, ?)"""
                    self.db.execute(query, (monto, interes, cuota, plazo, plazo, fecha_prestamo,
                                            fecha_pago, total, obs, nombre, celular, recomendador_id))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para particular: {nombre}")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(main_frame, text="✅ APROBAR PRÉSTAMO", command=registrar_prestamo, width=20).pack(pady=10)
        ttk.Button(main_frame, text="❌ CANCELAR", command=ventana.destroy, width=20).pack(pady=5)

        buscar_socios()
        toggle_tipo()
        calcular_cuota()

    def gestionar_prestamos(self):
        """Gestión de préstamos con scroll y funciones completas"""
        ventana = tk.Toplevel()
        ventana.title("Gestión de Préstamos")
        ventana.geometry("1300x700")
        ventana.minsize(900, 500)

        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Solicitante", "Monto", "Interés", "Cuota", "Plazo", "Restantes", "Saldo", "Estado", "Fecha")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        widths = {"ID": 60, "Solicitante": 200, "Monto": 120, "Interés": 80, "Cuota": 120,
                  "Plazo": 70, "Restantes": 80, "Saldo": 130, "Estado": 90, "Fecha": 110}
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 100))
        scroll_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        scroll_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

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

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        prestamo_actual_id = None

        def cargar_prestamos():
            for item in tree.get_children():
                tree.delete(item)
            query = "SELECT id_prestamo, monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, saldo_pendiente, estado, fecha_prestamo, es_externo, nombre_externo, id_socio FROM prestamos ORDER BY fecha_prestamo DESC"
            prestamos = self.db.fetch_all(query)
            if not prestamos:
                tree.insert("", tk.END, values=("No hay préstamos", "", "", "", "", "", "", "", "", ""))
                return
            for p in prestamos:
                if p[9] == 1:
                    solicitante = p[10] if p[10] else "Particular"
                else:
                    socio = self.db.fetch_one("SELECT nombre || ' ' || apellido FROM socios WHERE id_socio = ?", (p[11],))
                    solicitante = socio[0] if socio else "Socio eliminado"
                monto = float(p[1]) if p[1] else 0
                interes = float(p[2]) if p[2] else 0
                cuota = float(p[3]) if p[3] else 0
                saldo = float(p[6]) if p[6] else 0
                valores = (p[0], solicitante, f"${monto:,.2f}", f"{interes}%", f"${cuota:,.2f}", p[4], p[5], f"${saldo:,.2f}", p[7], p[8])
                if p[7] == "activo":
                    tree.insert("", tk.END, values=valores, tags=("activo",))
                elif p[7] == "pagado":
                    tree.insert("", tk.END, values=valores, tags=("pagado",))
                else:
                    tree.insert("", tk.END, values=valores, tags=("vencido",))
            tree.tag_configure('activo', foreground='green')
            tree.tag_configure('pagado', foreground='blue')
            tree.tag_configure('vencido', foreground='red')

        def mostrar_detalles(event=None):
            nonlocal prestamo_actual_id
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])['values']
            if vals[0] == "No hay préstamos":
                return
            prestamo_actual_id = vals[0]
            q = "SELECT saldo_pendiente, cuota_mensual, fecha_proximo_pago, interes_mensual, monto_prestado FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(q, (prestamo_actual_id,))
            if prestamo:
                lbl_solicitante.config(text=f"Solicitante: {vals[1]}")
                lbl_monto.config(text=f"Monto: ${float(prestamo[4]):,.2f}")
                lbl_interes.config(text=f"Interés: {float(prestamo[3])}%")
                lbl_saldo.config(text=f"Saldo pendiente: ${float(prestamo[0]):,.2f}")
                lbl_cuota.config(text=f"Próxima cuota: ${float(prestamo[1]):,.2f}")
                lbl_fecha.config(text=f"Fecha próximo pago: {prestamo[2]}")

        def registrar_pago():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Seleccione un préstamo")
                return
            q = "SELECT saldo_pendiente, cuota_mensual FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(q, (prestamo_actual_id,))
            if not prestamo:
                return
            saldo, cuota = float(prestamo[0]), float(prestamo[1])
            if saldo <= 0:
                messagebox.showinfo("Préstamo ya pagado")
                return
            monto = simpledialog.askfloat("Pago", f"Saldo: ${saldo:,.2f}\nCuota sugerida: ${cuota:,.2f}\n\nMonto a pagar:", minvalue=0.01, maxvalue=saldo)
            if monto:
                nuevo_saldo = saldo - monto
                nuevo_estado = "pagado" if nuevo_saldo <= 0 else "activo"
                self.db.execute("INSERT INTO pagos_prestamo (id_prestamo, monto_pagado, fecha_pago, forma_pago, saldo_restante) VALUES (?, ?, date('now'), 'Efectivo', ?)", (prestamo_actual_id, monto, nuevo_saldo))
                self.db.execute("UPDATE prestamos SET saldo_pendiente = ?, estado = ? WHERE id_prestamo = ?", (nuevo_saldo, nuevo_estado, prestamo_actual_id))
                messagebox.showinfo("Éxito", f"Pago registrado. Nuevo saldo: ${nuevo_saldo:,.2f}")
                cargar_prestamos()
                mostrar_detalles()

        def modificar_prestamo():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Seleccione un préstamo")
                return
            q = "SELECT monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, estado FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(q, (prestamo_actual_id,))
            if not prestamo:
                return
            win = tk.Toplevel(ventana)
            win.title("Modificar Préstamo")
            win.geometry("400x400")
            frame = ttk.Frame(win, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)
            ttk.Label(frame, text="Monto:").grid(row=0, column=0, sticky=tk.W)
            e_monto = ttk.Entry(frame); e_monto.grid(row=0, column=1); e_monto.insert(0, str(prestamo[0]))
            ttk.Label(frame, text="Interés:").grid(row=1, column=0, sticky=tk.W)
            e_interes = ttk.Entry(frame); e_interes.grid(row=1, column=1); e_interes.insert(0, str(prestamo[1]))
            ttk.Label(frame, text="Cuota:").grid(row=2, column=0, sticky=tk.W)
            e_cuota = ttk.Entry(frame); e_cuota.grid(row=2, column=1); e_cuota.insert(0, str(prestamo[2]))
            ttk.Label(frame, text="Cuotas totales:").grid(row=3, column=0, sticky=tk.W)
            e_ct = ttk.Entry(frame); e_ct.grid(row=3, column=1); e_ct.insert(0, str(prestamo[3]))
            ttk.Label(frame, text="Cuotas restantes:").grid(row=4, column=0, sticky=tk.W)
            e_cr = ttk.Entry(frame); e_cr.grid(row=4, column=1); e_cr.insert(0, str(prestamo[4]))
            ttk.Label(frame, text="Estado:").grid(row=5, column=0, sticky=tk.W)
            cb_estado = ttk.Combobox(frame, values=["activo", "pagado", "vencido"], state="readonly")
            cb_estado.grid(row=5, column=1); cb_estado.set(prestamo[5])
            def guardar():
                self.db.execute("UPDATE prestamos SET monto_prestado=?, interes_mensual=?, cuota_mensual=?, cuotas_totales=?, cuotas_restantes=?, estado=? WHERE id_prestamo=?", (float(e_monto.get()), float(e_interes.get()), float(e_cuota.get()), int(e_ct.get()), int(e_cr.get()), cb_estado.get(), prestamo_actual_id))
                messagebox.showinfo("Modificado")
                win.destroy()
                cargar_prestamos()
                mostrar_detalles()
            ttk.Button(frame, text="Guardar", command=guardar).grid(row=6, column=0, columnspan=2, pady=20)

        def eliminar_prestamo():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Seleccione un préstamo")
                return
            if messagebox.askyesno("Confirmar", "¿Eliminar permanentemente?"):
                self.db.execute("DELETE FROM pagos_prestamo WHERE id_prestamo = ?", (prestamo_actual_id,))
                self.db.execute("DELETE FROM prestamos WHERE id_prestamo = ?", (prestamo_actual_id,))
                messagebox.showinfo("Eliminado")
                cargar_prestamos()
                mostrar_detalles()

        ttk.Button(btn_frame, text="Registrar Pago", command=registrar_pago, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Modificar", command=modificar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=eliminar_prestamo, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=lambda: [cargar_prestamos(), mostrar_detalles()], width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=ventana.destroy, width=14).pack(side=tk.RIGHT, padx=5)

        tree.bind("<<TreeviewSelect>>", mostrar_detalles)
        cargar_prestamos()

    def prestamos_vencidos(self):
        ventana = tk.Toplevel()
        ventana.title("Préstamos Vencidos")
        ventana.geometry("1000x500")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text="PRÉSTAMOS VENCIDOS", font=("Arial", 14, "bold")).pack(pady=10)
        columns = ("ID", "Solicitante", "Teléfono", "Monto", "Saldo", "Cuota", "Días Vencido")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        from datetime import date
        hoy = date.today()
        query = "SELECT id_prestamo, CASE WHEN es_externo=1 THEN nombre_externo ELSE (SELECT nombre || ' ' || apellido FROM socios WHERE id_socio = prestamos.id_socio) END, CASE WHEN es_externo=1 THEN celular_externo ELSE (SELECT celular FROM socios WHERE id_socio = prestamos.id_socio) END, monto_prestado, saldo_pendiente, cuota_mensual, fecha_proximo_pago FROM prestamos WHERE estado='activo'"
        prestamos = self.db.fetch_all(query)
        for p in prestamos:
            if p[6] and datetime.strptime(p[6], "%Y-%m-%d").date() < hoy:
                dias = (hoy - datetime.strptime(p[6], "%Y-%m-%d").date()).days
                tree.insert("", tk.END, values=(p[0], p[1], p[2], f"${float(p[3]):,.2f}", f"${float(p[4]):,.2f}", f"${float(p[5]):,.2f}", f"{dias} días"))
        ttk.Button(frame, text="Actualizar", command=lambda: [tree.delete(*tree.get_children()), self.prestamos_vencidos()]).pack(pady=10)

    def registrar_pago(self):
        self.gestionar_prestamos()