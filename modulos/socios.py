# modulos/socios.py
import tkinter as tk
from modulos.responsive import configurar_ventana_responsive, configurar_treeview_responsive
from tkinter import ttk, messagebox, filedialog
import webbrowser
from datetime import datetime
import csv

class ModuloSocios:
    def __init__(self, database):
        self.db = database
    
    def agregar_socio(self):
        """Agregar nuevo socio"""
        socio_win = tk.Toplevel()
        socio_win.title("Agregar Nuevo Socio")
        socio_win.geometry("600x600")
        
        main_frame = ttk.Frame(socio_win, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="REGISTRAR NUEVO SOCIO", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Campos del formulario
        campos = [
            ("Código Socio*:", "entry", "", True),
            ("Nombre*:", "entry", "", True),
            ("Apellido*:", "entry", "", True),
            ("Cédula*:", "entry", "", True),
            ("Celular*:", "entry", "", True),
            ("Correo:", "entry", "", False),
            ("Dirección:", "entry", "", False),
            ("Ciudad:", "entry", "", False),
            ("Estado:", "combo", ["activo", "inactivo", "suspendido"], True),
            ("Observaciones:", "text", "", False)
        ]
        
        entries = {}
        for i, (label, tipo, valores, requerido) in enumerate(campos):
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=5)
            
            lbl_text = f"{label}{'*' if requerido else ''}"
            ttk.Label(frame, text=lbl_text, width=15).pack(side=tk.LEFT)
            
            if tipo == "entry":
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[label.replace(":", "").replace("*", "").strip().lower()] = entry
            elif tipo == "combo":
                combo = ttk.Combobox(frame, values=valores, state="readonly", width=20)
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                combo.set(valores[0] if valores else "")
                entries[label.replace(":", "").replace("*", "").strip().lower()] = combo
            elif tipo == "text":
                text = tk.Text(frame, height=3, width=40)
                text.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[label.replace(":", "").replace("*", "").strip().lower()] = text
        
        # Generar código automático
        def generar_codigo():
            try:
                codigo = self.generar_codigo_automatico()
                entries['código socio'].delete(0, tk.END)
                entries['código socio'].insert(0, codigo)
            except:
                entries['código socio'].insert(0, "SOC001")
        
        ttk.Button(main_frame, text="Generar Código Automático", 
                  command=generar_codigo).pack(pady=10)
        
        def guardar_socio():
            """Guardar socio en la base de datos"""
            try:
                # Validar campos requeridos
                valores = []
                for key, widget in entries.items():
                    if key in ['código socio', 'nombre', 'apellido', 'cédula', 'celular', 'estado']:
                        if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                            valor = widget.get().strip()
                        elif isinstance(widget, tk.Text):
                            valor = widget.get("1.0", tk.END).strip()
                        else:
                            valor = ""
                        
                        if not valor and key != 'estado':
                            messagebox.showwarning("Campo requerido", 
                                                 f"El campo {key} es obligatorio")
                            return
                        valores.append(valor)
                    elif isinstance(widget, tk.Text):
                        valores.append(widget.get("1.0", tk.END).strip())
                    else:
                        valores.append(widget.get().strip())
                
                # Insertar en la base de datos
                query = """
                INSERT INTO socios (codigo_socio, nombre, apellido, cedula, celular, 
                                   correo, direccion, ciudad, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                if self.db.execute(query, valores):
                    messagebox.showinfo("Éxito", "Socio registrado correctamente")
                    socio_win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo guardar el socio")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Guardar Socio", 
                  command=guardar_socio, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=socio_win.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        # Generar código automáticamente
        socio_win.after(100, generar_codigo)

        # Campo Celular (con formato)
        ttk.Label(frame, text="Celular*:").pack(side=tk.LEFT)
        entry_celular = ttk.Entry(frame)
        entry_celular.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def formatear_celular(event):
            valor = entry_celular.get()
            if valor and valor.isdigit():
                # Formatear como 300 123 4567
                if len(valor) == 10:
                    formateado = f"{valor[:3]} {valor[3:6]} {valor[6:]}"
                    entry_celular.delete(0, tk.END)
                    entry_celular.insert(0, formateado)
        
        entry_celular.bind('<FocusOut>', formatear_celular)
    
    def generar_codigo_automatico(self):
        """Generar código automático para socio"""
        try:
            self.db.cursor.execute("SELECT MAX(id_socio) FROM socios")
            ultimo_id = self.db.cursor.fetchone()[0]
            nuevo_id = (ultimo_id or 0) + 1
            return f"SOC{nuevo_id:04d}"
        except:
            return "SOC0001"
    
    def listar_socios(self):
        """Listar todos los socios"""
        listar_win = tk.Toplevel()

        # Configurar ventana responsive
        configurar_ventana_responsive(listar_win, ancho_inicial=1000, alto_inicial=600, minimo_ancho=800, minimo_alto=400)
        
        main_frame = ttk.Frame(listar_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de herramientas
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(toolbar, text="Filtrar por:").pack(side=tk.LEFT, padx=5)
        
        # Filtros
        filtro_frame = ttk.Frame(toolbar)
        filtro_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filtro_frame, text="Estado:").pack(side=tk.LEFT)
        combo_estado = ttk.Combobox(filtro_frame, values=["Todos", "activo", "inactivo", "suspendido"], 
                                   state="readonly", width=10)
        combo_estado.pack(side=tk.LEFT, padx=5)
        combo_estado.set("Todos")
        
        ttk.Label(filtro_frame, text="Buscar:").pack(side=tk.LEFT, padx=(10, 5))
        entry_buscar = ttk.Entry(filtro_frame, width=30)
        entry_buscar.pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Código", "Nombre", "Cédula", "Celular", "Correo", "Estado", "Ingreso")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        configurar_treeview_responsive(tree, main_frame)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def cargar_socios(filtro_estado="Todos", texto_buscar=""):
            """Cargar socios con filtros"""
            try:
                # Limpiar treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                # Construir consulta
                query = """
                SELECT id_socio, codigo_socio, nombre || ' ' || apellido, 
                       cedula, celular, correo, estado, fecha_ingreso
                FROM socios 
                WHERE 1=1
                """
                params = []
                
                if filtro_estado != "Todos":
                    query += " AND estado = ?"
                    params.append(filtro_estado)
                
                if texto_buscar:
                    query += " AND (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?)"
                    buscar_pattern = f"%{texto_buscar}%"
                    params.extend([buscar_pattern, buscar_pattern, buscar_pattern, buscar_pattern])
                
                query += " ORDER BY id_socio DESC"
                
                socios = self.db.fetch_all(query, params)
                
                # Insertar datos
                for socio in socios:
                    tree.insert("", tk.END, values=socio)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando socios: {str(e)}")
        
        def filtrar():
            """Aplicar filtros"""
            estado = combo_estado.get()
            texto = entry_buscar.get().strip()
            cargar_socios(estado, texto)
        
        def editar_socio():
            """Editar socio seleccionado"""
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Seleccionar", "Seleccione un socio para editar")
                return
            
            item = tree.item(seleccion[0])
            id_socio = item['values'][0]
            self.editar_socio_dialog(id_socio, listar_win)
        
        def eliminar_socio():
            """Eliminar socio seleccionado"""
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Seleccionar", "Seleccione un socio para eliminar")
                return
            
            item = tree.item(seleccion[0])
            id_socio = item['values'][0]
            nombre = item['values'][2]
            
            confirmar = messagebox.askyesno("Confirmar", 
                                          f"¿Está seguro de eliminar al socio: {nombre}?")
            if confirmar:
                if self.eliminar_socio_db(id_socio):
                    messagebox.showinfo("Éxito", "Socio eliminado correctamente")
                    cargar_socios()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el socio")
        
        # Botones de acción
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="Filtrar", 
                  command=filtrar).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Editar", 
                  command=editar_socio).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", 
                  command=eliminar_socio).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refrescar", 
                  command=lambda: cargar_socios()).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Exportar", 
                  command=self.exportar_socios).pack(side=tk.LEFT, padx=5)
        
        # Cargar socios inicialmente
        cargar_socios()
    
    def editar_socio_dialog(self, id_socio, parent):
        """Diálogo para editar socio"""
        # Obtener datos del socio
        query = "SELECT * FROM socios WHERE id_socio = ?"
        socio = self.db.fetch_one(query, (id_socio,))
        
        if not socio:
            messagebox.showerror("Error", "Socio no encontrado")
            return
        
        editar_win = tk.Toplevel(parent)
        editar_win.title(f"Editar Socio: {socio[2]} {socio[3]}")
        editar_win.geometry("600x600")
        
        main_frame = ttk.Frame(editar_win, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="EDITAR SOCIO", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Campos (similar a agregar pero con datos actuales)
        # ... implementación similar a agregar_socio ...
        
        # Botones Guardar/Cancelar
    
    def eliminar_socio_db(self, id_socio):
        """Eliminar socio de la base de datos"""
        try:
            query = "DELETE FROM socios WHERE id_socio = ?"
            return self.db.execute(query, (id_socio,))
        except:
            return False
    
    def buscar_socio(self):
        """Búsqueda avanzada de socios"""
        buscar_win = tk.Toplevel()
        buscar_win.title("Búsqueda Avanzada de Socios")
        buscar_win.geometry("700x500")
        
        # Implementar búsqueda avanzada
        # ... código para búsqueda avanzada ...
    
    def importar_socios(self):
        """Importar socios desde archivo CSV"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    contador = 0
                    
                    for row in reader:
                        # Procesar cada fila
                        query = """
                        INSERT INTO socios (codigo_socio, nombre, apellido, cedula, celular, correo)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """
                        
                        valores = (
                            row.get('codigo', ''),
                            row.get('nombre', ''),
                            row.get('apellido', ''),
                            row.get('cedula', ''),
                            row.get('celular', ''),
                            row.get('correo', '')
                        )
                        
                        if self.db.execute(query, valores):
                            contador += 1
                    
                    messagebox.showinfo("Importación", 
                                      f"Se importaron {contador} socios correctamente")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error importando socios: {str(e)}")
    
    def exportar_socios(self):
        """Exportar socios a CSV"""
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if archivo:
            try:
                socios = self.db.fetch_all("""
                    SELECT codigo_socio, nombre, apellido, cedula, celular, correo, estado, fecha_ingreso
                    FROM socios 
                    ORDER BY id_socio
                """)
                
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Código', 'Nombre', 'Apellido', 'Cédula', 'Celular', 'Correo', 'Estado', 'Ingreso'])
                    writer.writerows(socios)
                
                messagebox.showinfo("Exportación", f"Socios exportados a: {archivo}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando socios: {str(e)}")