# modulos/reportes_prestamos.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ReportesPrestamos:
    def __init__(self, database):
        self.db = database
    
    def reporte_general_prestamos(self):
        """Reporte general de todos los préstamos"""
        ventana = tk.Toplevel()
        ventana.title("Reporte General de Préstamos")
        ventana.geometry("1300x700")
        ventana.minsize(1000, 500)
        
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(main_frame, text="REPORTE GENERAL DE PRÉSTAMOS", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Fecha del reporte
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        tk.Label(main_frame, text=f"Generado: {fecha_actual}", 
                font=("Arial", 10), fg="gray").pack(pady=(0, 10))
        
        # Frame para filtros
        filtros_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        filtros_frame.pack(fill=tk.X, pady=10)
        
        row1 = ttk.Frame(filtros_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Estado:").pack(side=tk.LEFT, padx=5)
        combo_estado = ttk.Combobox(row1, values=["Todos", "activo", "pagado", "vencido"], 
                                    state="readonly", width=12)
        combo_estado.pack(side=tk.LEFT, padx=5)
        combo_estado.set("Todos")
        
        ttk.Label(row1, text="Fecha desde:").pack(side=tk.LEFT, padx=5)
        entry_desde = ttk.Entry(row1, width=12)
        entry_desde.pack(side=tk.LEFT, padx=5)
        entry_desde.insert(0, "2024-01-01")
        
        ttk.Label(row1, text="Fecha hasta:").pack(side=tk.LEFT, padx=5)
        entry_hasta = ttk.Entry(row1, width=12)
        entry_hasta.pack(side=tk.LEFT, padx=5)
        entry_hasta.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(row1, text="🔍 Filtrar", command=lambda: cargar_reporte()).pack(side=tk.LEFT, padx=20)
        
        # Treeview principal
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("ID", "Código", "Solicitante", "Monto", "Interés", "Cuota", 
                   "Cuotas", "Pagadas", "Saldo", "Estado", "Fecha")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 50, "Código": 140, "Solicitante": 180, "Monto": 120, 
                      "Interés": 70, "Cuota": 120, "Cuotas": 60, "Pagadas": 70, 
                      "Saldo": 130, "Estado": 90, "Fecha": 100}
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 100))
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=scroll_y.set, xscrollcommand=scroll_x.set)
        
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame de resumen
        resumen_frame = ttk.LabelFrame(main_frame, text="Resumen", padding="10")
        resumen_frame.pack(fill=tk.X, pady=10)
        
        lbl_total_prestamos = tk.Label(resumen_frame, text="Total préstamos: 0", font=("Arial", 11, "bold"))
        lbl_total_prestamos.pack(side=tk.LEFT, padx=20)
        
        lbl_monto_total = tk.Label(resumen_frame, text="Monto total: $0", font=("Arial", 11, "bold"), fg="blue")
        lbl_monto_total.pack(side=tk.LEFT, padx=20)
        
        lbl_saldo_total = tk.Label(resumen_frame, text="Saldo total: $0", font=("Arial", 11, "bold"), fg="red")
        lbl_saldo_total.pack(side=tk.LEFT, padx=20)
        
        def cargar_reporte():
            for item in tree.get_children():
                tree.delete(item)
            
            estado = combo_estado.get()
            fecha_desde = entry_desde.get()
            fecha_hasta = entry_hasta.get()
            
            query = """
                SELECT p.id_prestamo, p.codigo_prestamo,
                       CASE WHEN p.es_externo = TRUE THEN p.nombre_externo 
                            ELSE COALESCE(s.nombre || ' ' || s.apellido, 'Particular')
                       END as solicitante,
                       p.monto_prestado, p.interes_mensual, p.cuota_mensual,
                       p.cuotas_totales, p.cuotas_restantes, p.saldo_pendiente,
                       p.estado, p.fecha_prestamo
                FROM prestamos p
                LEFT JOIN socios s ON p.id_socio = s.id_socio
                WHERE p.fecha_prestamo BETWEEN ? AND ?
            """
            params = [fecha_desde, fecha_hasta]
            
            if estado != "Todos":
                query += " AND p.estado = ?"
                params.append(estado)
            
            query += " ORDER BY p.fecha_prestamo DESC"
            
            prestamos = self.db.fetch_all(query, params)
            
            total_monto = 0
            total_saldo = 0
            
            for p in prestamos:
                monto = float(p[3]) if p[3] else 0
                saldo = float(p[8]) if p[8] else 0
                pagadas = int(p[6]) - int(p[7]) if p[6] and p[7] else 0
                
                total_monto += monto
                total_saldo += saldo
                
                valores = (
                    p[0], p[1] if p[1] else "S/C", p[2], f"${monto:,.2f}", 
                    f"{p[4]}%", f"${p[5]:,.2f}", p[6], pagadas, 
                    f"${saldo:,.2f}", p[9], p[10]
                )
                
                if p[9] == "activo":
                    tree.insert("", tk.END, values=valores, tags=("activo",))
                elif p[9] == "pagado":
                    tree.insert("", tk.END, values=valores, tags=("pagado",))
                else:
                    tree.insert("", tk.END, values=valores, tags=("vencido",))
            
            tree.tag_configure('activo', foreground='green')
            tree.tag_configure('pagado', foreground='blue')
            tree.tag_configure('vencido', foreground='red')
            
            lbl_total_prestamos.config(text=f"Total préstamos: {len(prestamos)}")
            lbl_monto_total.config(text=f"Monto total: ${total_monto:,.2f}")
            lbl_saldo_total.config(text=f"Saldo total: ${total_saldo:,.2f}")
        
        def ver_detalles():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            item = tree.item(seleccion[0])
            prestamo_id = item['values'][0]
            self.detalle_pagos_prestamo(prestamo_id)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📋 Ver Pagos", command=ver_detalles, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 Exportar", command=lambda: self.exportar_reporte(tree), width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ Imprimir", command=lambda: self.imprimir_reporte(tree), width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cerrar", command=ventana.destroy, width=15).pack(side=tk.RIGHT, padx=5)
        
        cargar_reporte()
    
    def reporte_prestamos_socio(self):
        """Reporte de préstamos por socio"""
        ventana = tk.Toplevel()
        ventana.title("Reporte de Préstamos por Socio")
        ventana.geometry("1300x700")
        ventana.minsize(1000, 500)
        
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="REPORTE DE PRÉSTAMOS POR SOCIO", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame para seleccionar socio
        socio_frame = ttk.LabelFrame(main_frame, text="Seleccionar Socio", padding="10")
        socio_frame.pack(fill=tk.X, pady=10)
        
        search_frame = ttk.Frame(socio_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Buscar socio:").pack(side=tk.LEFT, padx=5)
        entry_buscar = ttk.Entry(search_frame, width=40)
        entry_buscar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tree_socios = ttk.Treeview(socio_frame, columns=("ID", "Código", "Nombre", "Cédula"), 
                                   show="headings", height=5)
        for col in ("ID", "Código", "Nombre", "Cédula"):
            tree_socios.heading(col, text=col)
            tree_socios.column(col, width=120)
        
        scroll_socios = ttk.Scrollbar(socio_frame, orient=tk.VERTICAL, command=tree_socios.yview)
        tree_socios.configure(yscroll=scroll_socios.set)
        tree_socios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scroll_socios.pack(side=tk.RIGHT, fill=tk.Y)
        
        def buscar_socios():
            texto = entry_buscar.get().strip()
            for item in tree_socios.get_children():
                tree_socios.delete(item)
            
            if not texto:
                query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula FROM socios WHERE estado = 'activo' ORDER BY nombre LIMIT 30"
                socios = self.db.fetch_all(query)
            else:
                query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula FROM socios WHERE estado = 'activo' AND (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?) ORDER BY nombre LIMIT 30"
                p = f"%{texto}%"
                socios = self.db.fetch_all(query, (p, p, p, p))
            
            for s in socios:
                tree_socios.insert("", tk.END, values=s)
        
        ttk.Button(search_frame, text="🔍 Buscar", command=buscar_socios).pack(side=tk.LEFT, padx=5)
        
        lbl_socio_seleccionado = tk.Label(socio_frame, text="⚡ Socio seleccionado: Ninguno", 
                                         font=("Arial", 10, "bold"), fg="green")
        lbl_socio_seleccionado.pack(anchor=tk.W, pady=5)
        
        socio_seleccionado_id = None
        socio_seleccionado_nombre = None
        
        def on_socio_select(event):
            nonlocal socio_seleccionado_id, socio_seleccionado_nombre
            sel = tree_socios.selection()
            if sel:
                vals = tree_socios.item(sel[0])['values']
                if vals:
                    socio_seleccionado_id = vals[0]
                    socio_seleccionado_nombre = vals[2]
                    lbl_socio_seleccionado.config(text=f"✅ Socio seleccionado: {socio_seleccionado_nombre}")
                    cargar_prestamos_socio()
        
        tree_socios.bind("<<TreeviewSelect>>", on_socio_select)
        
        # Treeview de préstamos del socio
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("ID", "Código", "Monto", "Interés", "Cuota", "Cuotas", "Pagadas", "Saldo", "Estado", "Fecha")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=scroll_y.set, xscrollcommand=scroll_x.set)
        
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame de resumen
        resumen_frame = ttk.LabelFrame(main_frame, text="Resumen del Socio", padding="10")
        resumen_frame.pack(fill=tk.X, pady=10)
        
        lbl_total_prestamos = tk.Label(resumen_frame, text="Total préstamos: 0", font=("Arial", 11, "bold"))
        lbl_total_prestamos.pack(side=tk.LEFT, padx=20)
        
        lbl_monto_total = tk.Label(resumen_frame, text="Monto total: $0", font=("Arial", 11, "bold"), fg="blue")
        lbl_monto_total.pack(side=tk.LEFT, padx=20)
        
        lbl_saldo_total = tk.Label(resumen_frame, text="Saldo total: $0", font=("Arial", 11, "bold"), fg="red")
        lbl_saldo_total.pack(side=tk.LEFT, padx=20)
        
        def cargar_prestamos_socio():
            if not socio_seleccionado_id:
                return
            
            for item in tree.get_children():
                tree.delete(item)
            
            query = """
                SELECT p.id_prestamo, p.codigo_prestamo,
                       p.monto_prestado, p.interes_mensual, p.cuota_mensual,
                       p.cuotas_totales, p.cuotas_restantes, p.saldo_pendiente,
                       p.estado, p.fecha_prestamo
                FROM prestamos p
                WHERE p.id_socio = ?
                ORDER BY p.fecha_prestamo DESC
            """
            prestamos = self.db.fetch_all(query, (socio_seleccionado_id,))
            
            total_monto = 0
            total_saldo = 0
            
            for p in prestamos:
                monto = float(p[2]) if p[2] else 0
                saldo = float(p[7]) if p[7] else 0
                pagadas = int(p[5]) - int(p[6]) if p[5] and p[6] else 0
                
                total_monto += monto
                total_saldo += saldo
                
                valores = (
                    p[0], p[1] if p[1] else "S/C", f"${monto:,.2f}", 
                    f"{p[3]}%", f"${p[4]:,.2f}", p[5], pagadas, 
                    f"${saldo:,.2f}", p[8], p[9]
                )
                
                if p[8] == "activo":
                    tree.insert("", tk.END, values=valores, tags=("activo",))
                elif p[8] == "pagado":
                    tree.insert("", tk.END, values=valores, tags=("pagado",))
                else:
                    tree.insert("", tk.END, values=valores, tags=("vencido",))
            
            tree.tag_configure('activo', foreground='green')
            tree.tag_configure('pagado', foreground='blue')
            tree.tag_configure('vencido', foreground='red')
            
            lbl_total_prestamos.config(text=f"Total préstamos: {len(prestamos)}")
            lbl_monto_total.config(text=f"Monto total: ${total_monto:,.2f}")
            lbl_saldo_total.config(text=f"Saldo total: ${total_saldo:,.2f}")
        
        def ver_detalles():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Error", "Seleccione un préstamo")
                return
            item = tree.item(seleccion[0])
            prestamo_id = item['values'][0]
            self.detalle_pagos_prestamo(prestamo_id)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📋 Ver Pagos", command=ver_detalles, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cerrar", command=ventana.destroy, width=15).pack(side=tk.RIGHT, padx=5)
        
        buscar_socios()
    
    def detalle_pagos_prestamo(self, prestamo_id):
        """Mostrar detalle de pagos de un préstamo específico"""
        # Obtener datos del préstamo
        query = """
            SELECT p.codigo_prestamo,
                   CASE WHEN p.es_externo = TRUE THEN p.nombre_externo 
                        ELSE COALESCE(s.nombre || ' ' || s.apellido, 'Particular')
                   END as solicitante,
                   p.monto_prestado, p.interes_mensual, p.saldo_pendiente
            FROM prestamos p
            LEFT JOIN socios s ON p.id_socio = s.id_socio
            WHERE p.id_prestamo = ?
        """
        prestamo = self.db.fetch_one(query, (prestamo_id,))
        if not prestamo:
            messagebox.showerror("Error", "Préstamo no encontrado")
            return
        
        ventana = tk.Toplevel()
        ventana.title(f"Pagos - {prestamo[0]}")
        ventana.geometry("1000x500")
        ventana.minsize(800, 400)
        
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del préstamo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Préstamo", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text=f"Código: {prestamo[0]}", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Solicitante: {prestamo[1]}").pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Monto: ${float(prestamo[2]):,.2f} | Interés: {prestamo[3]}% | Saldo: ${float(prestamo[4]):,.2f}").pack(anchor=tk.W)
        
        # Treeview de pagos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("ID", "Fecha", "Monto Pagado", "Interés Pagado", "Abono Capital", "Saldo Restante", "Forma Pago")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scroll_y.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar pagos
        query_pagos = """
            SELECT id_pago, fecha_pago, monto_pagado, interes_pagado, 
                   abono_capital, saldo_restante, forma_pago
            FROM pagos_prestamo
            WHERE id_prestamo = ?
            ORDER BY fecha_pago DESC
        """
        pagos = self.db.fetch_all(query_pagos, (prestamo_id,))
        
        total_pagado = 0
        for pago in pagos:
            monto = float(pago[2]) if pago[2] else 0
            total_pagado += monto
            tree.insert("", tk.END, values=(
                pago[0], pago[1], f"${monto:,.2f}", 
                f"${pago[3]:,.2f}" if pago[3] else "$0",
                f"${pago[4]:,.2f}" if pago[4] else "$0",
                f"${pago[5]:,.2f}" if pago[5] else "$0",
                pago[6] if pago[6] else "Efectivo"
            ))
        
        # Resumen
        resumen_frame = ttk.Frame(main_frame)
        resumen_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(resumen_frame, text=f"Total pagado: ${total_pagado:,.2f}", 
                font=("Arial", 12, "bold"), fg="green").pack(side=tk.LEFT, padx=20)
        tk.Label(resumen_frame, text=f"Saldo actual: ${float(prestamo[4]):,.2f}", 
                font=("Arial", 12, "bold"), fg="red").pack(side=tk.LEFT, padx=20)
        
        if not pagos:
            tk.Label(main_frame, text="No hay pagos registrados para este préstamo", 
                    font=("Arial", 12), fg="gray").pack(pady=20)
        
        ttk.Button(main_frame, text="Cerrar", command=ventana.destroy, width=15).pack(pady=10)
    
    def exportar_reporte(self, tree):
        """Exportar reporte a CSV"""
        from tkinter import filedialog
        import csv
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"reporte_prestamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if file_path:
            items = tree.get_children()
            datos = []
            for item in items:
                datos.append(tree.item(item)['values'])
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([tree.heading(col)['text'] for col in tree['columns']])
                writer.writerows(datos)
            
            messagebox.showinfo("Éxito", f"Reporte exportado a:\n{file_path}")
    
    def imprimir_reporte(self, tree):
        """Imprimir reporte (vista previa)"""
        # Crear ventana de vista previa
        preview = tk.Toplevel()
        preview.title("Vista Previa del Reporte")
        preview.geometry("800x600")
        
        text_area = tk.Text(preview, wrap=tk.NONE)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_y = tk.Scrollbar(preview, orient=tk.VERTICAL, command=text_area.yview)
        scroll_x = tk.Scrollbar(preview, orient=tk.HORIZONTAL, command=text_area.xview)
        text_area.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Generar texto del reporte
        reporte = "=" * 80 + "\n"
        reporte += "REPORTE DE PRÉSTAMOS\n"
        reporte += f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        reporte += "=" * 80 + "\n\n"
        
        # Obtener columnas
        columns = [tree.heading(col)['text'] for col in tree['columns']]
        reporte += " | ".join(columns) + "\n"
        reporte += "-" * 80 + "\n"
        
        for item in tree.get_children():
            valores = tree.item(item)['values']
            reporte += " | ".join(str(v) for v in valores) + "\n"
        
        text_area.insert(tk.END, reporte)
        text_area.config(state=tk.DISABLED)
        
        ttk.Button(preview, text="Cerrar", command=preview.destroy).pack(pady=10)