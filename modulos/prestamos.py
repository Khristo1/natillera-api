# modulos/prestamos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

class ModuloPrestamos:
    def __init__(self, database):
        self.db = database
    
    def nuevo_prestamo(self):
        """Ventana para nuevo préstamo"""
        # ... (código completo que ya tienes)
        # Si no lo tienes, pídemelo y te lo doy
    
    def gestionar_prestamos(self):
        """Gestionar préstamos existentes - Ventana completa"""
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
                          p[5], p[6], p[7], f"${saldo:,.2f}", p[9], p[10])
                
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
        
        ttk.Button(btn_frame, text="Registrar Pago", command=registrar_pago, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=lambda: [cargar_prestamos(), mostrar_detalles()], width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=ventana.destroy, width=15).pack(side=tk.RIGHT, padx=5)
        
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