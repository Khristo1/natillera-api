# modulos/reportes.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class ModuloReportes:
    def __init__(self, database):
        self.db = database
    
    def reporte_general(self):
        """Generar reporte general"""
        ventana = tk.Toplevel()
        ventana.title("Reporte General")
        ventana.geometry("700x500")
        
        main_frame = ttk.Frame(ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de texto para el reporte
        text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=25)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            # Obtener estadísticas
            reporte = "=== REPORTE GENERAL - NATILLERA FAMILIAR ===\n"
            reporte += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            reporte += "=" * 50 + "\n\n"
            
            # Total socios
            self.db.cursor.execute("SELECT COUNT(*) FROM socios")
            total_socios = self.db.cursor.fetchone()[0]
            reporte += f"Total Socios: {total_socios}\n"
            
            # Socios activos
            self.db.cursor.execute("SELECT COUNT(*) FROM socios WHERE estado = 'activo'")
            socios_activos = self.db.cursor.fetchone()[0]
            reporte += f"Socios Activos: {socios_activos}\n"
            
            # Total aportes
            self.db.cursor.execute("SELECT SUM(monto) FROM aportes")
            total_aportes = self.db.cursor.fetchone()[0] or 0
            reporte += f"Total Aportes: ${total_aportes:,.2f}\n"
            
            # Aportes del mes actual
            mes_actual = datetime.now().strftime("%B")
            año_actual = datetime.now().year
            self.db.cursor.execute("SELECT SUM(monto) FROM aportes WHERE mes = %s AND año = %s", 
                                 (mes_actual, año_actual))
            aportes_mes = self.db.cursor.fetchone()[0] or 0
            reporte += f"Aportes {mes_actual}: ${aportes_mes:,.2f}\n"
            
            # Préstamos activos
            self.db.cursor.execute("SELECT COUNT(*), SUM(monto_prestado) FROM prestamos WHERE estado = 'vigente'")
            prestamos_info = self.db.cursor.fetchone()
            reporte += f"Préstamos Activos: {prestamos_info[0] or 0} (${prestamos_info[1] or 0:,.2f})\n"
            
            # Actividades
            self.db.cursor.execute("SELECT COUNT(*), SUM(ganancias) FROM actividades")
            actividades_info = self.db.cursor.fetchone()
            reporte += f"Actividades: {actividades_info[0] or 0} (Ganancias: ${actividades_info[1] or 0:,.2f})\n"
            
            reporte += "\n" + "=" * 50 + "\n"
            reporte += "FIN DEL REPORTE\n"
            
            # Mostrar reporte
            text_area.insert(tk.END, reporte)
            text_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def reporte_por_socio(self):
        """Reporte por socio específico"""
        ventana = tk.Toplevel()
        ventana.title("Reporte por Socio")
        ventana.geometry("400x200")
        
        main_frame = ttk.Frame(ventana, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="SELECCIONAR SOCIO", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Combobox para seleccionar socio
        combo_socio = ttk.Combobox(main_frame, state="readonly", width=40)
        combo_socio.pack(pady=10)
        
        # Cargar socios
        try:
            socios = self.db.fetch_all("""
                SELECT id_socio, codigo_socio || ' - ' || nombre || ' ' || apellido
                FROM socios 
                ORDER BY nombre
            """)
            
            combo_socio['values'] = [f"{id_} - {nombre}" for id_, nombre in socios]
            if socios:
                combo_socio.current(0)
        except Exception as e:
            print(f"Error cargando socios: {str(e)}")
        
        def generar_reporte():
            """Generar reporte del socio seleccionado"""
            if combo_socio.get():
                socio_id = int(combo_socio.get().split(" - ")[0])
                self.mostrar_reporte_socio(socio_id)
                ventana.destroy()
        
        ttk.Button(main_frame, text="Generar Reporte", 
                  command=generar_reporte, width=20).pack(pady=20)
    
    def mostrar_reporte_socio(self, socio_id):
        """Mostrar reporte detallado del socio"""
        ventana = tk.Toplevel()
        ventana.title("Reporte de Socio")
        ventana.geometry("600x400")
        
        main_frame = ttk.Frame(ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=20)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            # Obtener datos del socio
            query_socio = """
            SELECT codigo_socio, nombre, apellido, cedula, celular, 
                   fecha_ingreso, estado
            FROM socios 
            WHERE id_socio = %s
            """
            socio = self.db.fetch_one(query_socio, (socio_id,))
            
            if socio:
                reporte = f"=== REPORTE DE SOCIO ===\n"
                reporte += f"Socio: {socio[1]} {socio[2]}\n"
                reporte += f"Código: {socio[0]}\n"
                reporte += f"Cédula: {socio[3]}\n"
                reporte += f"Celular: {socio[4]}\n"
                reporte += f"Ingreso: {socio[5]}\n"
                reporte += f"Estado: {socio[6]}\n"
                reporte += "=" * 40 + "\n\n"
                
                # Aportes del socio
                query_aportes = """
                SELECT mes, año, monto, fecha_aporte
                FROM aportes 
                WHERE id_socio = %s
                ORDER BY año DESC, fecha_aporte DESC
                """
                aportes = self.db.fetch_all(query_aportes, (socio_id,))
                
                reporte += "APORTES REALIZADOS:\n"
                total_aportes = 0
                for aporte in aportes:
                    reporte += f"  {aporte[0]} {aporte[1]}: ${aporte[2]:,.2f} ({aporte[3]})\n"
                    total_aportes += aporte[2]
                
                reporte += f"\nTotal Aportado: ${total_aportes:,.2f}\n\n"
                
                # Préstamos del socio
                query_prestamos = """
                SELECT monto_prestado, interes_mensual, cuota_mensual, 
                       cuotas_totales, cuotas_restantes, estado
                FROM prestamos 
                WHERE id_socio = %s
                ORDER BY fecha_prestamo DESC
                """
                prestamos = self.db.fetch_all(query_prestamos, (socio_id,))
                
                if prestamos:
                    reporte += "PRÉSTAMOS:\n"
                    for i, prestamo in enumerate(prestamos):
                        reporte += f"  Préstamo {i+1}:\n"
                        reporte += f"    Monto: ${prestamo[0]:,.2f}\n"
                        reporte += f"    Interés: {prestamo[1]}%\n"
                        reporte += f"    Cuota: ${prestamo[2]:,.2f}\n"
                        reporte += f"    Cuotas: {prestamo[4]}/{prestamo[3]}\n"
                        reporte += f"    Estado: {prestamo[5]}\n\n"
                
                text_area.insert(tk.END, reporte)
                text_area.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Socio no encontrado")
                ventana.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def estado_cuentas(self):
        """Estado de cuentas"""
        messagebox.showinfo("Estado de Cuentas", "Funcionalidad en desarrollo")
    
    def flujo_caja(self):
        """Flujo de caja"""
        messagebox.showinfo("Flujo de Caja", "Funcionalidad en desarrollo")
    
    def generar_pdf(self):
        """Generar PDF del reporte"""
        messagebox.showinfo("PDF", "Funcionalidad en desarrollo")