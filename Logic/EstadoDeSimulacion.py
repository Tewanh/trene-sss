import tkinter as tk
from datetime import datetime, timedelta

class EstadoSimulacion(tk.Frame):
    def __init__(self, master=None, fecha_inicio_str="2015-01-01 00:00:00"):
        super().__init__(master, padx=10, pady=10, bg='#333333')
        self.configure(relief=tk.RAISED, borderwidth=2)

        # Inicializa el tiempo simulado a partir del string proporcionado
        try:
            self.tiempo_actual_simulado = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"Error en formato de fecha: {fecha_inicio_str}. Usando 2015-01-01.")
            self.tiempo_actual_simulado = datetime(2015, 1, 1, 0, 0, 0)
        
        # Etiqueta para la hora
        self.label_hora = tk.Label(self, text="", font=("Helvetica", 24, "bold"), fg="#00ff00", bg='#333333')
        self.label_hora.pack(anchor='center')

        # Etiqueta para la fecha
        self.label_fecha = tk.Label(self, text="", font=("Helvetica", 12), fg="#ffffff", bg='#333333')
        self.label_fecha.pack(anchor='center')

        # Inicializa la visualización con la fecha de inicio
        self.actualizar_display()

    def actualizar_display(self):
        """Actualiza las etiquetas de la GUI con el tiempo simulado actual."""
        formato_hora = self.tiempo_actual_simulado.strftime("%H:%M:%S")
        formato_fecha = self.tiempo_actual_simulado.strftime("%a, %d %b %Y")
        
        self.label_hora.config(text=formato_hora)
        self.label_fecha.config(text=formato_fecha)

    def avanzar_tiempo(self, delta: timedelta):
        """Función pública para avanzar el tiempo simulado desde la app principal."""
        self.tiempo_actual_simulado += delta
        self.actualizar_display()
        print(f"Tiempo avanzado a: {self.tiempo_actual_simulado}")
        return self.tiempo_actual_simulado
