# modulos/prestamos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

class ModuloPrestamos:
    def __init__(self, database):
        self.db = database
    
    def nuevo_prestamo(self):
        """Ventana para nuevo préstamo - Socio o Particular (Versión Unificada)"""
        ventana = tk.Toplevel()
        ventana.title("Nuevo Préstamo")
        ventana.geometry("800x750")
        ventana.minsize(750, 650)
        ventana.transient()
        ventana.grab_set()

        # ... (el código de scroll, frames, etc. lo dejamos como estaba) ...
        # Por brevedad, asumimos que la estructura de la interfaz (frames, entries, etc.)
        # es la misma que construimos ayer. Si la cambiaste, avísame.
        # Me centraré en la función interna registrar_prestamo que es la que causa el error.

        # ========== FUNCIÓN INTERNA PARA REGISTRAR ==========
        def registrar_prestamo():
            try:
                # --- Obtener valores de los campos ---
                monto_texto = entry_monto.get().replace(',', '')
                monto = float(monto_texto) if monto_texto else 0
                interes = float(entry_interes.get())
                cuotas = int(entry_cuotas.get())
                abono_inicial_texto = entry_abono_inicial.get().replace(',', '')
                abono_inicial = float(abono_inicial_texto) if abono_inicial_texto else 0
                cuota_sugerida_texto = entry_cuota_sugerida.get().replace(',', '')
                cuota_sugerida = float(cuota_sugerida_texto) if cuota_sugerida_texto else 0
                fecha_inicial = entry_fecha_inicial.get()
                fecha_primera = entry_fecha_primera.get()
                obs = text_obs.get("1.0", tk.END).strip()

                if monto <= 0:
                    messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                    return

                # --- Cálculos ---
                saldo_inicial = monto - abono_inicial
                if saldo_inicial < 0:
                    saldo_inicial = 0

                interes_mensual_calc = saldo_inicial * (interes / 100)
                if cuota_sugerida > 0:
                    cuota = cuota_sugerida
                else:
                    cuota = (saldo_inicial / cuotas) + interes_mensual_calc

                if tipo_var.get() == "socio":
                    # --- PRÉSTAMO A SOCIO (EXISTENTE) ---
                    if not socio_seleccionado_id:
                        messagebox.showwarning("Error", "Seleccione un socio")
                        return

                    query = """
                        INSERT INTO prestamos 
                        (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                        cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                        saldo_pendiente, observaciones, estado, es_externo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 0)
                    """
                    self.db.execute(query, (socio_seleccionado_id, monto, interes, cuota, cuotas, cuotas,
                                            fecha_inicial, fecha_primera, saldo_inicial, obs))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para socio: {socio_seleccionado_nombre}")

                else:
                    # --- PRÉSTAMO A PARTICULAR ---
                    nombre = entry_nombre_particular.get().strip()
                    celular = entry_celular_particular.get().strip()

                    if not nombre or not celular:
                        messagebox.showwarning("Error", "Complete nombre y celular del particular")
                        return

                    query = """
                        INSERT INTO prestamos 
                        (id_socio, monto_prestado, interes_mensual, cuota_mensual,
                        cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago,
                        saldo_pendiente, observaciones, estado, es_externo, nombre_externo,
                        celular_externo, id_recomendador)
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 1, ?, ?, ?)
                    """
                    self.db.execute(query, (monto, interes, cuota, cuotas, cuotas, fecha_inicial,
                                            fecha_primera, saldo_inicial, obs,
                                            nombre, celular, recomendador_id))
                    messagebox.showinfo("Éxito", f"Préstamo registrado para particular: {nombre}")

                ventana.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {str(e)}")
    
       
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

        # ========== FUNCIONES (DEFINIDAS ANTES DE LOS BOTONES) ==========
        
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
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            
            # Obtener datos
            q = """SELECT saldo_pendiente, cuota_mensual, interes_mensual, 
                        monto_prestado, cuotas_restantes, fecha_proximo_pago
                FROM prestamos WHERE id_prestamo = ?"""
            prestamo = self.db.fetch_one(q, (prestamo_actual_id,))
            if not prestamo:
                messagebox.showerror("Error", "Préstamo no encontrado")
                return
            
            capital_pendiente = float(prestamo[0])
            cuota_actual = float(prestamo[1])
            interes = float(prestamo[2])
            
            interes_periodo = capital_pendiente * (interes / 100)
            
            # Ventana de pago simple
            monto = simpledialog.askfloat("Pago", 
                f"Capital: ${capital_pendiente:,.2f}\n"
                f"Interés: ${interes_periodo:,.2f}\n"
                f"Cuota: ${cuota_actual:,.2f}\n\n"
                f"Monto a pagar: $")
            
            if monto and monto >= interes_periodo:
                abono = monto - interes_periodo
                nuevo_capital = capital_pendiente - abono
                if nuevo_capital < 0:
                    nuevo_capital = 0
                nueva_cuota = nuevo_capital + (nuevo_capital * (interes / 100))
                
                # Guardar
                self.db.execute("""UPDATE prestamos 
                    SET saldo_pendiente = ?, cuota_mensual = ?
                    WHERE id_prestamo = ?""", 
                    (nuevo_capital, nueva_cuota, prestamo_actual_id))
                
                self.db.execute("""INSERT INTO pagos_prestamo 
                    (id_prestamo, monto_pagado, interes_pagado, abono_capital, saldo_restante)
                    VALUES (?, ?, ?, ?, ?)""",
                    (prestamo_actual_id, monto, interes_periodo, abono, nuevo_capital))
                
                messagebox.showinfo("Éxito", f"Nuevo capital: ${nuevo_capital:,.2f}\nNueva cuota: ${nueva_cuota:,.2f}")
                cargar_prestamos()
                mostrar_detalles()

        def modificar_prestamo():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            q = "SELECT monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, estado FROM prestamos WHERE id_prestamo = ?"
            prestamo = self.db.fetch_one(q, (prestamo_actual_id,))
            if not prestamo:
                return
            win = tk.Toplevel(ventana)
            win.title("Modificar Préstamo")
            win.geometry("400x450")
            win.transient()
            win.grab_set()
            frame = ttk.Frame(win, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)
            ttk.Label(frame, text="Monto ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
            e_monto = ttk.Entry(frame)
            e_monto.grid(row=0, column=1, pady=5)
            e_monto.insert(0, str(prestamo[0]))
            ttk.Label(frame, text="Interés (%):").grid(row=1, column=0, sticky=tk.W, pady=5)
            e_interes = ttk.Entry(frame)
            e_interes.grid(row=1, column=1, pady=5)
            e_interes.insert(0, str(prestamo[1]))
            ttk.Label(frame, text="Cuota ($):").grid(row=2, column=0, sticky=tk.W, pady=5)
            e_cuota = ttk.Entry(frame)
            e_cuota.grid(row=2, column=1, pady=5)
            e_cuota.insert(0, str(prestamo[2]))
            ttk.Label(frame, text="Cuotas totales:").grid(row=3, column=0, sticky=tk.W, pady=5)
            e_ct = ttk.Entry(frame)
            e_ct.grid(row=3, column=1, pady=5)
            e_ct.insert(0, str(prestamo[3]))
            ttk.Label(frame, text="Cuotas restantes:").grid(row=4, column=0, sticky=tk.W, pady=5)
            e_cr = ttk.Entry(frame)
            e_cr.grid(row=4, column=1, pady=5)
            e_cr.insert(0, str(prestamo[4]))
            ttk.Label(frame, text="Estado:").grid(row=5, column=0, sticky=tk.W, pady=5)
            cb_estado = ttk.Combobox(frame, values=["activo", "pagado", "vencido"], state="readonly")
            cb_estado.grid(row=5, column=1, pady=5)
            cb_estado.set(prestamo[5])
            def guardar():
                try:
                    self.db.execute("UPDATE prestamos SET monto_prestado=?, interes_mensual=?, cuota_mensual=?, cuotas_totales=?, cuotas_restantes=?, estado=? WHERE id_prestamo=?", 
                                (float(e_monto.get()), float(e_interes.get()), float(e_cuota.get()), int(e_ct.get()), int(e_cr.get()), cb_estado.get(), prestamo_actual_id))
                    messagebox.showinfo("Éxito", "Préstamo modificado")
                    win.destroy()
                    cargar_prestamos()
                    mostrar_detalles()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))
            ttk.Button(frame, text="Guardar Cambios", command=guardar).grid(row=6, column=0, columnspan=2, pady=20)

        def eliminar_prestamo():
            nonlocal prestamo_actual_id
            if not prestamo_actual_id:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            if messagebox.askyesno("Confirmar", "¿Eliminar permanentemente este préstamo? No se puede deshacer."):
                self.db.execute("DELETE FROM pagos_prestamo WHERE id_prestamo = ?", (prestamo_actual_id,))
                self.db.execute("DELETE FROM prestamos WHERE id_prestamo = ?", (prestamo_actual_id,))
                messagebox.showinfo("Éxito", "Préstamo eliminado")
                cargar_prestamos()
                mostrar_detalles()

        # ========== BOTONES (DESPUÉS DE LAS FUNCIONES) ==========
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