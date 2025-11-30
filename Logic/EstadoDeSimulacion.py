# Logic/EstadoDeSimulacion.py
import tkinter as tk
from datetime import datetime, timedelta

class EstadoSimulacion(tk.Frame):
    def __init__(self, master=None, fecha_inicio_str="2015-01-01 07:00:00"):
        super().__init__(master, padx=10, pady=10, bg='#333333')
        self.configure(relief=tk.RAISED, borderwidth=2)

        try:
            # Manejo de conversión inicial de fecha
            self.tiempo_actual_simulado = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Error en formato de fecha inicial: {fecha_inicio_str}. Usando valor por defecto. Error: {e}")
            self.tiempo_actual_simulado = datetime(2015, 1, 1, 7, 0, 0)
        
        self.label_hora = tk.Label(self, text="", font=("Helvetica", 24, "bold"), fg="#00ff00", bg='#333333')
        self.label_hora.pack(anchor='center')

        self.label_fecha = tk.Label(self, text="", font=("Helvetica", 12), fg="#ffffff", bg='#333333')
        self.label_fecha.pack(anchor='center')

        self.actualizar_display()

    def actualizar_display(self):
        """Actualiza las etiquetas de la GUI con el tiempo simulado actual."""
        formato_hora = self.tiempo_actual_simulado.strftime("%H:%M:%S")
        formato_fecha = self.tiempo_actual_simulado.strftime("%a, %d %b %Y")
        
        self.label_hora.config(text=formato_hora)
        self.label_fecha.config(text=formato_fecha)

    def avanzar_tiempo(self, delta: timedelta):
        """Función pública para avanzar el tiempo simulado."""
        self.tiempo_actual_simulado += delta
        self.actualizar_display()
        return self.tiempo_actual_simulado
    
    def avanzar_una_hora(self):
        """Avanza el tiempo simulado exactamente 1 hora."""
        self.avanzar_tiempo(timedelta(hours=1))
