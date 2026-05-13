# modulos/aportes.py
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from datetime import datetime
import urllib.parse
import csv
import os

class ModuloAportes:
    def __init__(self, database):
        self.db = database
    
    def registrar_aporte(self):
        """Registrar nuevo aporte"""
        aporte_win = tk.Toplevel()
        aporte_win.title("Registrar Aporte")
        aporte_win.geometry("750x650")
        aporte_win.minsize(700, 550)
        aporte_win.transient()
        aporte_win.grab_set()
        
        # Frame principal con scroll para ventanas pequeñas
        main_container = ttk.Frame(aporte_win)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="REGISTRAR APORTE", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para seleccionar socio
        socio_frame = ttk.LabelFrame(main_frame, text="Seleccionar Socio", padding="10")
        socio_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame de búsqueda
        search_frame = ttk.Frame(socio_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Buscar por nombre, cédula o código:").pack(side=tk.LEFT, padx=5)
        entry_buscar = ttk.Entry(search_frame, width=30)
        entry_buscar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Treeview para mostrar socios
        columns = ("ID", "Código", "Nombre", "Cédula", "Celular")
        tree_socios = ttk.Treeview(socio_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree_socios.heading(col, text=col)
            tree_socios.column(col, width=120)
        
        # Scrollbars para el treeview
        tree_scroll_y = ttk.Scrollbar(socio_frame, orient=tk.VERTICAL, command=tree_socios.yview)
        tree_scroll_x = ttk.Scrollbar(socio_frame, orient=tk.HORIZONTAL, command=tree_socios.xview)
        tree_socios.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        tree_socios.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        def buscar_socios(event=None):
            """Buscar socios en la base de datos"""
            texto = entry_buscar.get().strip()
            
            # Limpiar treeview
            for item in tree_socios.get_children():
                tree_socios.delete(item)
            
            # Si no hay texto de búsqueda, cargar todos los socios activos
            if not texto:
                query = """
                SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular
                FROM socios 
                WHERE estado = 'activo'
                ORDER BY nombre
                LIMIT 50
                """
                socios = self.db.fetch_all(query)
            else:
                query = """
                SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular
                FROM socios 
                WHERE estado = 'activo' AND 
                      (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?)
                ORDER BY nombre
                LIMIT 50
                """
                buscar_pattern = f"%{texto}%"
                socios = self.db.fetch_all(query, (buscar_pattern, buscar_pattern, buscar_pattern, buscar_pattern))
            
            # Insertar resultados
            if socios:
                for socio in socios:
                    tree_socios.insert("", tk.END, values=socio)
                
                # Seleccionar el primero automáticamente
                if tree_socios.get_children():
                    tree_socios.selection_set(tree_socios.get_children()[0])
            else:
                tree_socios.insert("", tk.END, values=("", "", "No se encontraron socios", "", ""))
        
        # Botón de búsqueda
        ttk.Button(search_frame, text="🔍 Buscar", command=buscar_socios).pack(side=tk.LEFT, padx=5)
        
        # Label para mostrar socio seleccionado
        lbl_socio_seleccionado = tk.Label(socio_frame, text="Socio seleccionado: Ninguno", 
                                          font=("Arial", 10, "bold"), fg="blue")
        lbl_socio_seleccionado.pack(anchor=tk.W, pady=5)
        
        def on_socio_seleccionado(event):
            """Cuando se selecciona un socio en el treeview"""
            seleccion = tree_socios.selection()
            if seleccion:
                item = tree_socios.item(seleccion[0])
                valores = item['values']
                if valores and len(valores) > 2 and valores[2] != "No se encontraron socios":
                    lbl_socio_seleccionado.config(text=f"Socio seleccionado: {valores[2]} - Cédula: {valores[3]}")
                else:
                    lbl_socio_seleccionado.config(text="Socio seleccionado: Ninguno")
        
        tree_socios.bind("<<TreeviewSelect>>", on_socio_seleccionado)
        
        # Frame para datos del aporte
        datos_frame = ttk.LabelFrame(main_frame, text="Datos del Aporte", padding="10")
        datos_frame.pack(fill=tk.X, pady=10)
        
        # Monto
        ttk.Label(datos_frame, text="Monto ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_monto = ttk.Entry(datos_frame)
        entry_monto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
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
        
        # Mes y año
        ttk.Label(datos_frame, text="Mes:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        combo_mes = ttk.Combobox(datos_frame, values=[
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ], state="readonly", width=15)
        combo_mes.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        combo_mes.current(datetime.now().month - 1)
        
        ttk.Label(datos_frame, text="Año:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_año = ttk.Entry(datos_frame)
        entry_año.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_año.insert(0, str(datetime.now().year))
        
        # Forma de pago
        ttk.Label(datos_frame, text="Forma de Pago:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        combo_pago = ttk.Combobox(datos_frame, 
                                 values=["Efectivo", "Transferencia", "Débito", "Cheque"], 
                                 state="readonly", width=15)
        combo_pago.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        combo_pago.set("Efectivo")
        
        # Observaciones
        ttk.Label(datos_frame, text="Observaciones:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        text_obs = tk.Text(datos_frame, height=3, width=40)
        text_obs.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        def registrar():
            """Registrar el aporte"""
            try:
                # Verificar socio seleccionado
                seleccion = tree_socios.selection()
                if not seleccion:
                    messagebox.showwarning("Error", "Seleccione un socio de la lista")
                    return
                
                item = tree_socios.item(seleccion[0])
                valores = item['values']
                
                if not valores or len(valores) < 5 or valores[2] == "No se encontraron socios":
                    messagebox.showwarning("Error", "Seleccione un socio válido")
                    return
                
                id_socio = valores[0]
                socio_nombre = valores[2]
                
                # Validar monto
                monto_texto = entry_monto.get().replace(',', '')
                if not monto_texto or not monto_texto.replace('.', '', 1).isdigit():
                    messagebox.showwarning("Error", "Ingrese un monto válido")
                    return
                
                monto = float(monto_texto) if monto_texto else 0
                if monto <= 0:
                    messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                    return
                
                # Validar mes y año
                mes = combo_mes.get()
                año_texto = entry_año.get().strip()
                
                if not mes:
                    messagebox.showwarning("Error", "Seleccione un mes")
                    return
                
                if not año_texto.isdigit() or len(año_texto) != 4:
                    messagebox.showwarning("Error", "Ingrese un año válido (4 dígitos)")
                    return
                
                año = int(año_texto)
                forma_pago = combo_pago.get()
                observaciones = text_obs.get("1.0", tk.END).strip()
                
                # Verificar si ya existe aporte para ese mes y año
                query_verificar = """
                SELECT COUNT(*) FROM aportes 
                WHERE id_socio = ? AND mes = ? AND año = ? AND estado != 'anulado'
                """
                existe = self.db.fetch_one(query_verificar, (id_socio, mes, año))
                
                if existe[0] > 0:
                    respuesta = messagebox.askyesno(
                        "Aporte existente",
                        f"Ya existe un aporte registrado para {mes} {año}.\n¿Desea registrar de todas formas?"
                    )
                    if not respuesta:
                        return
                
                # Insertar aporte
                query = """
                INSERT INTO aportes (id_socio, monto, mes, año, forma_pago, observaciones, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'pagado')
                """
                
                if self.db.execute(query, (id_socio, monto, mes, año, forma_pago, observaciones)):
                    messagebox.showinfo("Éxito", f"Aporte registrado correctamente para {socio_nombre}\nMonto: ${monto:,.2f}\nMes: {mes} {año}")
                    aporte_win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo registrar el aporte")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {str(e)}")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Registrar Aporte", 
                  command=registrar, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=aporte_win.destroy, width=18).pack(side=tk.LEFT, padx=5)
        
        # Buscar socios al iniciar (cargar lista inicial)
        buscar_socios()
    
    def historial_aportes(self):
        """Mostrar historial de aportes"""
        historial_win = tk.Toplevel()
        historial_win.title("Historial de Aportes")
        historial_win.geometry("1100x700")
        historial_win.minsize(900, 500)
        
        main_frame = ttk.Frame(historial_win, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        filtros_frame = ttk.LabelFrame(main_frame, text="Filtros de Búsqueda", padding="10")
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
        
        row1 = ttk.Frame(filtros_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Socio:").pack(side=tk.LEFT, padx=5)
        combo_socio = ttk.Combobox(row1, state="readonly", width=35)
        combo_socio.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Mes:").pack(side=tk.LEFT, padx=5)
        combo_mes = ttk.Combobox(row1, values=["Todos"] + [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ], state="readonly", width=12)
        combo_mes.pack(side=tk.LEFT, padx=5)
        combo_mes.set("Todos")
        
        ttk.Label(row1, text="Año:").pack(side=tk.LEFT, padx=5)
        entry_año = ttk.Entry(row1, width=8)
        entry_año.pack(side=tk.LEFT, padx=5)
        entry_año.insert(0, str(datetime.now().year))
        
        row2 = ttk.Frame(filtros_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Estado:").pack(side=tk.LEFT, padx=5)
        combo_estado = ttk.Combobox(row2, 
                                   values=["Todos", "pagado", "pendiente", "anulado"], 
                                   state="readonly", width=12)
        combo_estado.pack(side=tk.LEFT, padx=5)
        combo_estado.set("Todos")
        
        btn_frame_filtros = ttk.Frame(row2)
        btn_frame_filtros.pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame_filtros, text="Filtrar", command=lambda: cargar_aportes(), width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame_filtros, text="Exportar", command=lambda: self.exportar_aportes(tree), width=10).pack(side=tk.LEFT, padx=2)
        
        self.cargar_socios_combo(combo_socio)
        
        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Fecha", "Socio", "Monto", "Mes", "Año", "Forma Pago", "Estado")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X, pady=(10, 0))
        
        total_label = tk.Label(total_frame, text="Total: $0.00", 
                              font=("Arial", 14, "bold"), fg="green")
        total_label.pack(side=tk.RIGHT, padx=10)
        
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Modificar", command=lambda: modificar_aporte(), width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Anular", command=lambda: eliminar_aporte(), width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Eliminar Definitivo", command=lambda: self.eliminar_definitivo_aporte(tree, cargar_aportes), width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Actualizar", command=lambda: cargar_aportes(), width=10).pack(side=tk.RIGHT, padx=2)
        
        def cargar_aportes():
            try:
                for item in tree.get_children():
                    tree.delete(item)
                
                query = """
                SELECT a.id_aporte, a.fecha_aporte, s.nombre || ' ' || s.apellido,
                       a.monto, a.mes, a.año, a.forma_pago, a.estado
                FROM aportes a
                JOIN socios s ON a.id_socio = s.id_socio
                WHERE 1=1
                """
                params = []
                
                socio_val = combo_socio.get()
                if socio_val != "Todos" and socio_val:
                    try:
                        socio_id = int(socio_val.split(" - ")[0])
                        query += " AND a.id_socio = ?"
                        params.append(socio_id)
                    except:
                        pass
                
                mes_val = combo_mes.get()
                if mes_val != "Todos":
                    query += " AND a.mes = ?"
                    params.append(mes_val)
                
                año_val = entry_año.get().strip()
                if año_val and año_val.isdigit():
                    query += " AND a.año = ?"
                    params.append(int(año_val))
                
                estado_val = combo_estado.get()
                if estado_val != "Todos":
                    query += " AND a.estado = ?"
                    params.append(estado_val)
                
                query += " ORDER BY a.fecha_aporte DESC"
                
                aportes = self.db.fetch_all(query, params)
                
                total = 0
                for aporte in aportes:
                    tree.insert("", tk.END, values=aporte, tags=(aporte[7],))
                    if aporte[7] != "anulado":
                        total += float(aporte[3])
                
                tree.tag_configure('pagado', foreground='green')
                tree.tag_configure('pendiente', foreground='orange')
                tree.tag_configure('anulado', foreground='red')
                
                total_label.config(text=f"Total: ${total:,.2f}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando aportes: {str(e)}")
        
        def modificar_aporte():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Error", "Seleccione un aporte")
                return
            item = tree.item(seleccion[0])
            id_aporte = item['values'][0]
            if item['values'][7] == "anulado":
                messagebox.showwarning("Error", "No se puede modificar un aporte anulado")
                return
            self.modificar_aporte_window(id_aporte, historial_win, cargar_aportes)
        
        def eliminar_aporte():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Error", "Seleccione un aporte")
                return
            item = tree.item(seleccion[0])
            id_aporte = item['values'][0]
            socio = item['values'][2]
            monto = item['values'][3]
            if item['values'][7] == "anulado":
                messagebox.showwarning("Error", "Este aporte ya está anulado")
                return
            respuesta = messagebox.askyesno("Confirmar", f"¿Anular aporte de {socio} por ${monto}?")
            if respuesta:
                try:
                    self.db.execute("UPDATE aportes SET estado = 'anulado' WHERE id_aporte = ?", (id_aporte,))
                    messagebox.showinfo("Éxito", "Aporte anulado")
                    cargar_aportes()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        
        cargar_aportes()
        tree.bind("<Double-1>", lambda e: modificar_aporte())
    
    def eliminar_definitivo_aporte(self, tree, callback=None):
        """Eliminar definitivamente un aporte anulado"""
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un aporte")
            return
        item = tree.item(seleccion[0])
        id_aporte = item['values'][0]
        socio = item['values'][2]
        monto = item['values'][3]
        estado = item['values'][7]
        
        if estado != "anulado":
            messagebox.showwarning("Error", "Solo se pueden eliminar aportes anulados")
            return
        
        respuesta = messagebox.askyesno("⚠️ Eliminar Definitivo", 
            f"¿Eliminar DEFINITIVAMENTE el aporte de {socio} por ${monto}?\n\nEsta acción NO se puede deshacer.")
        
        if respuesta:
            try:
                self.db.execute("DELETE FROM aportes WHERE id_aporte = ?", (id_aporte,))
                messagebox.showinfo("Éxito", "Aporte eliminado definitivamente")
                if callback:
                    callback()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def modificar_aporte_window(self, id_aporte, parent_window=None, callback=None):
        """Ventana para modificar aporte"""
        query = """
        SELECT a.*, s.nombre || ' ' || s.apellido as nombre_socio
        FROM aportes a
        JOIN socios s ON a.id_socio = s.id_socio
        WHERE a.id_aporte = ?
        """
        aporte = self.db.fetch_one(query, (id_aporte,))
        if not aporte:
            messagebox.showerror("Error", "Aporte no encontrado")
            return
        
        modificar_win = tk.Toplevel()
        modificar_win.title("Modificar Aporte")
        modificar_win.geometry("600x500")
        modificar_win.transient(parent_window)
        modificar_win.grab_set()
        
        main_frame = ttk.Frame(modificar_win, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="MODIFICAR APORTE", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        info_frame = ttk.LabelFrame(main_frame, text="Información del Socio", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        ttk.Label(info_frame, text=f"Socio: {aporte[9]}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"ID Aporte: {aporte[0]}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Fecha de registro: {aporte[1]}").pack(anchor=tk.W)
        
        datos_frame = ttk.LabelFrame(main_frame, text="Datos del Aporte", padding="10")
        datos_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(datos_frame, text="Monto ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_monto = ttk.Entry(datos_frame)
        entry_monto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_monto.insert(0, str(aporte[2]))
        
        ttk.Label(datos_frame, text="Mes:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        combo_mes = ttk.Combobox(datos_frame, values=[
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ], state="readonly", width=15)
        combo_mes.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        for i, mes in enumerate(combo_mes['values']):
            if mes == aporte[3]:
                combo_mes.current(i)
                break
        
        ttk.Label(datos_frame, text="Año:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_año = ttk.Entry(datos_frame)
        entry_año.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        entry_año.insert(0, str(aporte[4]))
        
        ttk.Label(datos_frame, text="Forma de Pago:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        combo_pago = ttk.Combobox(datos_frame, 
                                 values=["Efectivo", "Transferencia", "Débito", "Cheque"], 
                                 state="readonly", width=15)
        combo_pago.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        combo_pago.set(aporte[5])
        
        ttk.Label(datos_frame, text="Estado:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        combo_estado = ttk.Combobox(datos_frame, 
                                   values=["pagado", "pendiente"], 
                                   state="readonly", width=15)
        combo_estado.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        combo_estado.set(aporte[6])
        
        ttk.Label(datos_frame, text="Observaciones:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        text_obs = tk.Text(datos_frame, height=3, width=40)
        text_obs.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        if aporte[7]:
            text_obs.insert("1.0", aporte[7])
        
        def guardar_cambios():
            try:
                monto_texto = entry_monto.get().strip()
                if not monto_texto or not monto_texto.replace('.', '', 1).isdigit():
                    messagebox.showwarning("Error", "Monto inválido")
                    return
                monto = float(monto_texto)
                if monto <= 0:
                    messagebox.showwarning("Error", "Monto debe ser mayor a cero")
                    return
                
                mes = combo_mes.get()
                año_texto = entry_año.get().strip()
                if not mes:
                    messagebox.showwarning("Error", "Seleccione un mes")
                    return
                if not año_texto.isdigit() or len(año_texto) != 4:
                    messagebox.showwarning("Error", "Año inválido")
                    return
                
                año = int(año_texto)
                forma_pago = combo_pago.get()
                estado = combo_estado.get()
                observaciones = text_obs.get("1.0", tk.END).strip()
                
                query = """
                UPDATE aportes 
                SET monto = ?, mes = ?, año = ?, forma_pago = ?, 
                    estado = ?, observaciones = ?
                WHERE id_aporte = ?
                """
                if self.db.execute(query, (monto, mes, año, forma_pago, estado, observaciones, id_aporte)):
                    messagebox.showinfo("Éxito", "Aporte modificado")
                    modificar_win.destroy()
                    if callback:
                        callback()
                else:
                    messagebox.showerror("Error", "No se pudo modificar")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar_cambios, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=modificar_win.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def cargar_socios_combo(self, combo_widget):
        """Cargar socios en combobox"""
        try:
            socios = self.db.fetch_all("""
                SELECT id_socio, codigo_socio || ' - ' || nombre || ' ' || apellido
                FROM socios 
                WHERE estado = 'activo'
                ORDER BY nombre
            """)
            valores = ["Todos"] + [f"{id_} - {nombre}" for id_, nombre in socios]
            combo_widget['values'] = valores
            combo_widget.set("Todos")
        except Exception as e:
            print(f"Error cargando socios: {str(e)}")
    
    def exportar_aportes(self, tree):
        """Exportar aportes a CSV"""
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"aportes_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            if not file_path:
                return
            
            items = tree.get_children()
            datos = []
            for item in items:
                datos.append(tree.item(item)['values'])
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Fecha', 'Socio', 'Monto', 'Mes', 'Año', 'Forma de Pago', 'Estado'])
                writer.writerows(datos)
            
            messagebox.showinfo("Éxito", f"Exportado a: {file_path}")
            os.startfile(os.path.dirname(file_path))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def aportes_pendientes(self):
        """Mostrar aportes pendientes"""
        pendientes_win = tk.Toplevel()
        pendientes_win.title("Aportes Pendientes")
        pendientes_win.geometry("900x500")
        
        main_frame = ttk.Frame(pendientes_win, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="APORTES PENDIENTES", font=("Arial", 14, "bold")).pack(pady=10)
        
        columns = ("ID Socio", "Socio", "Cédula", "Celular", "Último Aporte", "Meses Pendientes")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        pendientes = self.db.fetch_all("""
            SELECT s.id_socio, s.nombre || ' ' || s.apellido, s.cedula, s.celular,
                   MAX(a.mes || ' ' || a.año) as ultimo_aporte,
                   COUNT(CASE WHEN a.estado = 'pagado' THEN 1 END) as aportes_realizados
            FROM socios s
            LEFT JOIN aportes a ON s.id_socio = a.id_socio
            WHERE s.estado = 'activo'
            GROUP BY s.id_socio
            ORDER BY aportes_realizados ASC
        """)
        
        for p in pendientes:
            tree.insert("", tk.END, values=p)
    
    def registro_masivo(self):
        """Registro masivo de aportes"""
        messagebox.showinfo("Registro Masivo", "Funcionalidad en desarrollo")