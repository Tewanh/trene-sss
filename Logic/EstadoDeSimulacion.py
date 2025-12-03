# Logic/EstadoDeSimulacion.py
import tkinter as tk
from datetime import datetime, timedelta

class EstadoSimulacion(tk.Frame):
    def __init__(self, master=None, fecha_inicio_str="2015-01-01 07:00:00"):
        super().__init__(master, padx=10, pady=10, bg='#333333')
        self.configure(relief=tk.RAISED, borderwidth=2)

        # Formato de fecha para registros y carga de datos
        self.formato_fecha = "%Y-%m-%d %H:%M:%S"

        
        try:
            self.tiempo_actual_simulado = datetime.strptime(fecha_inicio_str, self.formato_fecha)
        except ValueError as e:
            print(f"Error en formato de fecha inicial: {fecha_inicio_str}. Usando valor por defecto. Error: {e}")
            self.tiempo_actual_simulado = datetime(2015, 1, 1, 7, 0, 0)

        self.estaciones = {}
        self.trenes = {}
        self.rutas = {}

        
        self.contador_id_cliente = 0

       
        self.registro_eventos = []

        
        self.label_hora = tk.Label(self, text="", font=("Helvetica", 24, "bold"), fg="#00ff00", bg='#333333')
        self.label_hora.pack(anchor='center')

        self.label_fecha = tk.Label(self, text="", font=("Helvetica", 12), fg="#ffffff", bg='#333333')
        self.label_fecha.pack(anchor='center')

        
        self.actualizar_display()


    def actualizar_display(self):
        
        formato_hora = self.tiempo_actual_simulado.strftime("%H:%M:%S")
        formato_fecha = self.tiempo_actual_simulado.strftime("%a, %d %b %Y")

        self.label_hora.config(text=formato_hora)
        self.label_fecha.config(text=formato_fecha)

    def avanzar_tiempo(self, delta: timedelta):
        
        self.tiempo_actual_simulado += delta
        self.actualizar_display()
        return self.tiempo_actual_simulado

    def avanzar_una_hora(self):
       
        self.avanzar_tiempo(timedelta(hours=1))

   
    def obtener_siguiente_id_cliente(self) -> int:
        
        self.contador_id_cliente += 1
        return self.contador_id_cliente

    def registrar_evento(self, tipo: str, info_evento: str):
        
        tiempo_str = self.tiempo_actual_simulado.strftime(self.formato_fecha)

        evento = {
            'tiempo': tiempo_str,
            'tipo': tipo,          
            'info': info_evento    
        }
        self.registro_eventos.append(evento)

    def aplicar_datos_cargados(self, datos: dict):
    
        if "tiempo_actual_simulado" in datos:
            self.tiempo_actual_simulado = datetime.strptime(
                datos["tiempo_actual_simulado"], self.formato_fecha
            )

    
        self.registro_eventos = datos.get("registro_eventos", [])
        self.contador_id_cliente = datos.get("contador_id_cliente", 0)

      
