import tkinter as tk
from datetime import datetime, timedelta

class EstadoSimulacion(tk.Frame):
    # La fecha y hora de inicio por defecto es 2015-01-01 a las 07:00:00
    def __init__(self, master=None, fecha_inicio_str="2015-01-01 07:00:00"):
        super().__init__(master, padx=10, pady=10, bg='#333333')
        self.configure(relief=tk.RAISED, borderwidth=2)

        # Inicializa el tiempo simulado a partir del string proporcionado
        try:
            self.tiempo_actual_simulado = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # En caso de error, usa esta fecha como respaldo
            print(f"Error en formato de fecha: {fecha_inicio_str}. Usando 2015-01-01 07:00:00.")
            self.tiempo_actual_simulado = datetime(2015, 1, 1, 7, 0, 0)
        
        # Elementos de la interfaz gráfica
        self.label_hora = tk.Label(self, text="", font=("Helvetica", 24, "bold"), fg="#00ff00", bg='#333333')
        self.label_hora.pack(anchor='center')
        self.label_fecha = tk.Label(self, text="", font=("Helvetica", 12), fg="#ffffff", bg='#333333')
        self.label_fecha.pack(anchor='center')
        self.actualizar_display()

    # ... (métodos actualizar_display y avanzar_tiempo sin cambios) ...
    def actualizar_display(self):
        formato_hora = self.tiempo_actual_simulado.strftime("%H:%M:%S")
        formato_fecha = self.tiempo_actual_simulado.strftime("%a, %d %b %Y")
        self.label_hora.config(text=formato_hora)
        self.label_fecha.config(text=formato_fecha)

    def avanzar_tiempo(self, delta: timedelta):
        self.tiempo_actual_simulado += delta
        self.actualizar_display()
        print(f"Tiempo avanzado a: {self.tiempo_actual_simulado}")
        return self.tiempo_actual_simulado
