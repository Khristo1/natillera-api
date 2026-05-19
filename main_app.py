# main_app.py - APLICACIÓN PRINCIPAL MODULAR con RESPONSIVE
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
from modulos import reportes_prestamos

# Importar módulos
from modulos import socios, aportes, prestamos, actividades, reportes, database

# Importar funciones responsive
from modulos.responsive import configurar_ventana_responsive, configurar_frame_expansible

class NatilleraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NATILLERA 2026 - SISTEMA MODULAR")
        
        # Configurar ventana principal responsive
        configurar_ventana_responsive(self.root, ancho_inicial=1200, alto_inicial=700, 
                                      minimo_ancho=900, minimo_alto=500)
        
        # Conexión a base de datos
        self.db = database.Database()
        
        # Inicializar módulos
        self.modulo_socios = socios.ModuloSocios(self.db)
        self.modulo_aportes = aportes.ModuloAportes(self.db)
        self.modulo_prestamos = prestamos.ModuloPrestamos(self.db)
        self.modulo_actividades = actividades.ModuloActividades(self.db)
        self.modulo_reportes = reportes.ModuloReportes(self.db)
        self.modulo_reportes_prestamos = reportes_prestamos.ReportesPrestamos(self.db)
        
        # Configurar interfaz
        self.setup_ui()
        
        # Cargar estadísticas iniciales
        self.cargar_estadisticas()
    
    def setup_ui(self):
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Menú principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ====== MENÚ SOCIOS ======
        menu_socios = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Socios", menu=menu_socios)
        menu_socios.add_command(label="Agregar Nuevo Socio", 
                               command=self.modulo_socios.agregar_socio)
        menu_socios.add_command(label="Listar/Editar Socios", 
                               command=self.modulo_socios.listar_socios)
        menu_socios.add_command(label="Buscar Socio", 
                               command=self.modulo_socios.buscar_socio)
        menu_socios.add_separator()
        menu_socios.add_command(label="Importar Socios", 
                               command=self.modulo_socios.importar_socios)
        menu_socios.add_command(label="Exportar Socios", 
                               command=self.modulo_socios.exportar_socios)
        
        # ====== MENÚ APORTES ======
        menu_aportes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aportes", menu=menu_aportes)
        menu_aportes.add_command(label="Registrar Aporte", 
                                command=self.modulo_aportes.registrar_aporte)
        menu_aportes.add_command(label="Historial de Aportes", 
                                command=self.modulo_aportes.historial_aportes)
        menu_aportes.add_command(label="Aportes Pendientes", 
                                command=self.modulo_aportes.aportes_pendientes)
        menu_aportes.add_separator()
        menu_aportes.add_command(label="Registro Masivo", 
                                command=self.modulo_aportes.registro_masivo)
        
        # ====== MENÚ PRÉSTAMOS ======
        menu_prestamos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Préstamos", menu=menu_prestamos)
        menu_prestamos.add_command(label="Nuevo Préstamo", 
                                  command=self.modulo_prestamos.nuevo_prestamo)
        menu_prestamos.add_command(label="Gestionar Préstamos", 
                                  command=self.modulo_prestamos.gestionar_prestamos)
        menu_prestamos.add_command(label="Préstamos Vencidos", 
                                  command=self.modulo_prestamos.prestamos_vencidos)
        menu_prestamos.add_command(label="Registrar Pago", 
                                  command=self.modulo_prestamos.registrar_pago)
        
        # ====== MENÚ ACTIVIDADES ======
        menu_actividades = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Actividades", menu=menu_actividades)
        menu_actividades.add_command(label="Nueva Actividad", 
                                    command=self.modulo_actividades.nueva_actividad)
        menu_actividades.add_command(label="Gestionar Actividades", 
                                    command=self.modulo_actividades.gestionar_actividades)
        menu_actividades.add_command(label="Registrar Pago Actividad", 
                                    command=self.modulo_actividades.registrar_pago_actividad)
        menu_actividades.add_command(label="Reporte de Actividades", 
                                    command=self.modulo_actividades.reporte_actividades)
        menu_actividades.add_command(label="Registrar Pago Actividad", 
                                    command=self.modulo_actividades.registrar_pago_actividad)
        
        # ====== MENÚ REPORTES ======
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=menu_reportes)
        menu_reportes.add_command(label="Reporte General", 
                                command=self.modulo_reportes.reporte_general)
        menu_reportes.add_command(label="Reporte por Socio", 
                                command=self.modulo_reportes.reporte_por_socio)
        menu_reportes.add_separator()
        # NUEVAS OPCIONES - REPORTES DE PRÉSTAMOS
        menu_reportes.add_command(label="📊 Reporte General de Préstamos", 
                                command=self.modulo_reportes_prestamos.reporte_general_prestamos)
        menu_reportes.add_command(label="👤 Reporte de Préstamos por Socio", 
                                command=self.modulo_reportes_prestamos.reporte_prestamos_socio)
        menu_reportes.add_separator()
        menu_reportes.add_command(label="Estado de Cuentas", 
                                command=self.modulo_reportes.estado_cuentas)
        menu_reportes.add_command(label="Flujo de Caja", 
                                command=self.modulo_reportes.flujo_caja)
        menu_reportes.add_separator()
        menu_reportes.add_command(label="Generar PDF", 
                                command=self.modulo_reportes.generar_pdf)
        
        # ====== MENÚ CONFIGURACIÓN ======
        menu_config = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=menu_config)
        menu_config.add_command(label="Configurar Empresa", 
                               command=self.configurar_empresa)
        menu_config.add_command(label="Parámetros del Sistema", 
                               command=self.parametros_sistema)
        menu_config.add_separator()
        menu_config.add_command(label="Respaldar Base de Datos", 
                               command=self.respaldar_db)
        menu_config.add_command(label="Restaurar Base de Datos", 
                               command=self.restaurar_db)
        menu_config.add_separator()
        menu_config.add_command(label="Salir", command=self.root.quit)
        
        # Frame principal expandible
        main_frame = ttk.Frame(self.root, padding="20")
        configurar_frame_expansible(main_frame)
        
        # Título
        title = tk.Label(main_frame, text="NATILLERA 2026", 
                        font=("Arial", 24, "bold"), fg="navy")
        title.pack(pady=10)
        
        subtitle = tk.Label(main_frame, text="Sistema Modular de Gestión", 
                          font=("Arial", 12), fg="gray")
        subtitle.pack(pady=5)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Panel de estadísticas
        self.setup_panel_estadisticas(main_frame)
        
        # Panel de botones rápidos
        self.setup_botones_rapidos(main_frame)
        
        # Barra de estado
        self.status_bar = tk.Label(self.root, 
                                  text="Sistema listo - Base de datos: SQLite", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                                  bg="green", fg="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_panel_estadisticas(self, parent):
        """Configurar panel de estadísticas"""
        stats_frame = tk.Frame(parent, bg="white", bd=2, relief=tk.RAISED)
        stats_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(stats_frame, text="ESTADÍSTICAS DEL SISTEMA", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg="white")
        stats_grid.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Configurar columnas expansibles
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        self.stats_labels = {}
        estadisticas = [
            ("Total Socios", "0", "socios", "blue"),
            ("Socios Activos", "0", "socios_activos", "green"),
            ("Aportes Mes", "$0", "aportes_mes", "darkgreen"),
            ("Fondo Total", "$0", "fondo_total", "purple"),
            ("Préstamos Act.", "0", "prestamos_activos", "orange"),
            ("Préstamos Ven.", "0", "prestamos_vencidos", "red"),
            ("Actividades", "0", "actividades", "brown"),
            ("Ganancias Tot.", "$0", "ganancias", "darkblue")
        ]
        
        for i, (titulo, valor, clave, color) in enumerate(estadisticas):
            frame = tk.Frame(stats_grid, bg="white")
            frame.grid(row=i//4, column=i%4, padx=10, pady=10, sticky="nsew")
            
            tk.Label(frame, text=titulo, font=("Arial", 10), 
                    bg="white").pack()
            lbl_valor = tk.Label(frame, text=valor, font=("Arial", 16, "bold"), 
                               fg=color, bg="white")
            lbl_valor.pack()
            
            self.stats_labels[clave] = lbl_valor
    
    def setup_botones_rapidos(self, parent):
        """Configurar botones de acción rápida"""
        action_frame = tk.Frame(parent)
        action_frame.pack(pady=30)
        
        acciones = [
            ("➕ AGREGAR SOCIO", self.modulo_socios.agregar_socio, "blue"),
            ("💰 REGISTRAR APORTE", self.modulo_aportes.registrar_aporte, "green"),
            ("🏦 PRÉSTAMO", self.modulo_prestamos.nuevo_prestamo, "orange"),
            ("📅 NUEVA ACTIVIDAD", self.modulo_actividades.nueva_actividad, "purple"),
            ("📊 REPORTE GENERAL", self.modulo_reportes.reporte_general, "brown"),
            ("⚙️ CONFIGURACIÓN", self.configurar_empresa, "gray")
        ]
        
        for i, (texto, comando, color) in enumerate(acciones):
            btn = tk.Button(action_frame, text=texto, command=comando,
                          bg=color, fg="white", font=("Arial", 10, "bold"),
                          width=18, height=2, cursor="hand2")
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
    
    def cargar_estadisticas(self):
        """Cargar estadísticas actualizadas"""
        try:
            stats = self.db.obtener_estadisticas()
            
            for clave, valor in stats.items():
                if clave in self.stats_labels:
                    self.stats_labels[clave].config(text=valor)
        
        except Exception as e:
            print(f"Error cargando estadísticas: {e}")
    
    def configurar_empresa(self):
        """Configurar datos de la empresa - Responsive"""
        config_win = tk.Toplevel(self.root)
        config_win.title("Configurar Empresa")
        
        # Configurar ventana responsive
        configurar_ventana_responsive(config_win, ancho_inicial=500, alto_inicial=400,
                                      minimo_ancho=400, minimo_alto=300)
        
        main_frame = ttk.Frame(config_win, padding="20")
        configurar_frame_expansible(main_frame)
        
        tk.Label(main_frame, text="CONFIGURACIÓN DE EMPRESA", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Campos configurables
        campos = [
            ("Nombre de la Natillera:", "Natillera 2026"),
            ("Monto Aporte Mensual:", "50000"),
            ("Interés Préstamos (%):", "5"),
            ("Día Corte de Mes:", "30"),
            ("Mora por Atraso (%):", "2")
        ]
        
        entries = {}
        for i, (label, default) in enumerate(campos):
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=8)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            key = label.lower().replace(" ", "_").replace(":", "")
            entries[key] = entry
        
        def guardar_config():
            try:
                config_data = {}
                for key, entry in entries.items():
                    config_data[key] = entry.get()
                
                # Guardar en la tabla de configuración
                for clave, valor in config_data.items():
                    self.db.execute(
                        "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)",
                        (clave, valor)
                    )
                
                messagebox.showinfo("Configuración", "Configuración guardada exitosamente")
                config_win.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando configuración: {e}")
        
        ttk.Button(main_frame, text="Guardar", 
                  command=guardar_config, width=15).pack(pady=20)
    
    def parametros_sistema(self):
        """Parámetros del sistema"""
        messagebox.showinfo("Parámetros", "Configuración de parámetros del sistema")
    
    def respaldar_db(self):
        """Respaldar base de datos"""
        try:
            import shutil
            import datetime
            
            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"backup_natillera_{fecha}.db"
            
            if os.path.exists('natillera.db'):
                shutil.copy2('natillera.db', nombre_backup)
                messagebox.showinfo("Respaldo", f"Respaldo creado: {nombre_backup}")
            else:
                messagebox.showinfo("Respaldo", "No hay datos para respaldar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creando respaldo: {e}")
    
    def restaurar_db(self):
        """Restaurar base de datos"""
        from tkinter import filedialog
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de respaldo",
            filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            respuesta = messagebox.askyesno(
                "Restaurar",
                "⚠️ ADVERTENCIA: Esto sobrescribirá la base de datos actual. ¿Continuar?"
            )
            
            if respuesta:
                try:
                    import shutil
                    shutil.copy2(archivo, 'natillera.db')
                    messagebox.showinfo("Éxito", "Base de datos restaurada. Reinicie la aplicación.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error restaurando: {e}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = NatilleraApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Crear carpeta de módulos si no existe
    if not os.path.exists('modulos'):
        os.makedirs('modulos')
    
    main()