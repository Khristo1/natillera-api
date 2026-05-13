# modulos/prestamos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import urllib.parse
from datetime import datetime, timedelta

class ModuloPrestamos:
    def __init__(self, database):
        self.db = database
    
    def nuevo_prestamo(self):
        ventana = tk.Toplevel()
        ventana.title("Nuevo Préstamo")
        ventana.geometry("850x750")
        ventana.minsize(750, 600)
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
        
        # Título
        tk.Label(main_frame, text="NUEVO PRÉSTAMO", font=("Arial", 18, "bold"), fg="navy").pack(pady=(0, 20))
        
        # ========== SELECCIONAR SOCIO ==========
        socio_frame = ttk.LabelFrame(main_frame, text="1. SELECCIONAR SOCIO", padding="10")
        socio_frame.pack(fill=tk.X, pady=10)
        
        search_frame = ttk.Frame(socio_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Buscar socio:").pack(side=tk.LEFT, padx=5)
        entry_buscar = ttk.Entry(search_frame, width=30)
        entry_buscar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Buscar", command=lambda: buscar_socios()).pack(side=tk.LEFT, padx=5)
        
        # Treeview de socios
        tree_frame = ttk.Frame(socio_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        cols = ("ID", "Código", "Nombre", "Cédula", "Celular")
        tree_socios = ttk.Treeview(tree_frame, columns=cols, show="headings", height=5)
        for col in cols:
            tree_socios.heading(col, text=col)
            tree_socios.column(col, width=100)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree_socios.yview)
        tree_socios.configure(yscrollcommand=scroll_y.set)
        tree_socios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        lbl_socio = tk.Label(socio_frame, text="⚡ Socio seleccionado: Ninguno", font=("Arial", 10, "bold"), fg="green")
        lbl_socio.pack(anchor=tk.W, pady=5)
        
        # ========== DATOS DEL PRÉSTAMO ==========
        datos_frame = ttk.LabelFrame(main_frame, text="2. DATOS DEL PRÉSTAMO", padding="10")
        datos_frame.pack(fill=tk.X, pady=10)
        
        # Monto
        row0 = ttk.Frame(datos_frame)
        row0.pack(fill=tk.X, pady=5)
        ttk.Label(row0, text="Monto del préstamo ($):", width=20).pack(side=tk.LEFT)
        entry_monto = ttk.Entry(row0)
        entry_monto.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_monto.insert(0, "0")
        
        # Interés mensual
        row1 = ttk.Frame(datos_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="Interés mensual (%):", width=20).pack(side=tk.LEFT)
        entry_interes = ttk.Entry(row1)
        entry_interes.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_interes.insert(0, "10")
        
        # Plazo
        row2 = ttk.Frame(datos_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="Plazo (meses):", width=20).pack(side=tk.LEFT)
        entry_plazo = ttk.Entry(row2)
        entry_plazo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_plazo.insert(0, "12")
        
        # Cuota sugerida
        row3 = ttk.Frame(datos_frame)
        row3.pack(fill=tk.X, pady=5)
        ttk.Label(row3, text="Cuota sugerida ($):", width=20).pack(side=tk.LEFT)
        entry_cuota = ttk.Entry(row3)
        entry_cuota.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_cuota.insert(0, "0")
        
        # Fecha
        row4 = ttk.Frame(datos_frame)
        row4.pack(fill=tk.X, pady=5)
        ttk.Label(row4, text="Fecha préstamo:", width=20).pack(side=tk.LEFT)
        entry_fecha = ttk.Entry(row4)
        entry_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Observaciones
        row5 = ttk.Frame(datos_frame)
        row5.pack(fill=tk.X, pady=5)
        ttk.Label(row5, text="Observaciones:", width=20).pack(side=tk.LEFT)
        text_obs = tk.Text(row5, height=3)
        text_obs.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ========== SIMULACIÓN ==========
        sim_frame = ttk.LabelFrame(main_frame, text="3. SIMULACIÓN", padding="10")
        sim_frame.pack(fill=tk.X, pady=10)
        lbl_sim = tk.Label(sim_frame, text="Complete los datos", justify=tk.LEFT)
        lbl_sim.pack()
        
        # ========== BOTONES ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        btn_guardar = ttk.Button(btn_frame, text="REGISTRAR PRÉSTAMO", command=lambda: registrar_prestamo())
        btn_guardar.pack(side=tk.LEFT, padx=10)
        
        btn_cancelar = ttk.Button(btn_frame, text="CANCELAR", command=ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=10)
        
        # ========== FUNCIONES ==========
        socio_id = None
        socio_nombre = None
        
        def buscar_socios():
            texto = entry_buscar.get().strip()
            for item in tree_socios.get_children():
                tree_socios.delete(item)
            
            if not texto:
                query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular FROM socios WHERE estado = 'activo' ORDER BY nombre LIMIT 30"
                socios = self.db.fetch_all(query)
            else:
                query = "SELECT id_socio, codigo_socio, nombre || ' ' || apellido, cedula, celular FROM socios WHERE estado = 'activo' AND (nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ? OR codigo_socio LIKE ?) ORDER BY nombre LIMIT 30"
                p = f"%{texto}%"
                socios = self.db.fetch_all(query, (p, p, p, p))
            
            for s in socios:
                tree_socios.insert("", tk.END, values=s)
        
        def on_select(event):
            nonlocal socio_id, socio_nombre
            sel = tree_socios.selection()
            if sel:
                vals = tree_socios.item(sel[0])['values']
                if vals:
                    socio_id = vals[0]
                    socio_nombre = vals[2]
                    lbl_socio.config(text=f"✅ Socio seleccionado: {socio_nombre}")
        
        tree_socios.bind("<<TreeviewSelect>>", on_select)
        
        def actualizar_simulacion():
            try:
                monto_txt = entry_monto.get().replace(',', '')
                monto = float(monto_txt) if monto_txt else 0
                interes = float(entry_interes.get()) if entry_interes.get() else 0
                plazo = int(entry_plazo.get()) if entry_plazo.get() else 0
                cuota_sug = float(entry_cuota.get().replace(',', '')) if entry_cuota.get() else 0
                
                if monto > 0 and plazo > 0:
                    interes_mes = monto * (interes / 100)
                    if cuota_sug > 0:
                        total = cuota_sug * plazo
                        lbl_sim.config(text=f"Cuota: ${cuota_sug:,.2f} | Total: ${total:,.2f} | Interés total: ${total - monto:,.2f}")
                    else:
                        cuota_aprox = (monto / plazo) + interes_mes
                        lbl_sim.config(text=f"Interés primer mes: ${interes_mes:,.2f} | Cuota sugerida aprox: ${cuota_aprox:,.2f}")
                else:
                    lbl_sim.config(text="Complete monto y plazo")
            except:
                lbl_sim.config(text="Complete datos válidos")
        
        entry_monto.bind("<KeyRelease>", lambda e: actualizar_simulacion())
        entry_interes.bind("<KeyRelease>", lambda e: actualizar_simulacion())
        entry_plazo.bind("<KeyRelease>", lambda e: actualizar_simulacion())
        entry_cuota.bind("<KeyRelease>", lambda e: actualizar_simulacion())
        
        def registrar_prestamo():
            try:
                if not socio_id:
                    messagebox.showwarning("Error", "Seleccione un socio")
                    return
                
                monto_txt = entry_monto.get().replace(',', '')
                monto = float(monto_txt) if monto_txt else 0
                interes = float(entry_interes.get())
                plazo = int(entry_plazo.get())
                fecha = entry_fecha.get()
                cuota_sug = float(entry_cuota.get().replace(',', '')) if entry_cuota.get() else 0
                obs = text_obs.get("1.0", tk.END).strip()
                
                if monto <= 0:
                    messagebox.showwarning("Error", "Monto inválido")
                    return
                
                interes_mes = monto * (interes / 100)
                if cuota_sug > 0:
                    cuota = cuota_sug
                else:
                    cuota = (monto / plazo) + interes_mes
                
                fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
                fecha_prox = fecha_dt + timedelta(days=30)
                
                q = """INSERT INTO prestamos (id_socio, monto_prestado, interes_mensual, cuota_mensual, cuotas_totales, cuotas_restantes, fecha_prestamo, fecha_proximo_pago, saldo_pendiente, observaciones, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo')"""
                
                if self.db.execute(q, (socio_id, monto, interes, cuota, plazo, plazo, fecha, fecha_prox.strftime("%Y-%m-%d"), monto, obs)):
                    messagebox.showinfo("Éxito", f"Préstamo registrado para {socio_nombre}\nMonto: ${monto:,.2f}\nCuota: ${cuota:,.2f}")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo registrar")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Inicializar
        buscar_socios()
        actualizar_simulacion()
        
        # Scroll con mouse
        def on_mousewheel(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind("<MouseWheel>", on_mousewheel)
    
    def gestionar_prestamos(self):
        messagebox.showinfo("Gestión", "Funcionalidad en desarrollo")
    
    def prestamos_vencidos(self):
        messagebox.showinfo("Vencidos", "Funcionalidad en desarrollo")
    
    def registrar_pago(self):
        messagebox.showinfo("Pago", "Funcionalidad en desarrollo")