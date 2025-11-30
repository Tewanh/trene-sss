# Models/Estaciones.py
import datetime as dt
import random
from Models.Generador import GeneradorPorProporcion 

class Estacion:
    """Representa una estación de tren con sus datos y lógica de simulación."""

    def __init__(self, nombre: str, region: str, descripcion: str, conexiones: list[str], poblacion_total: int, hora_inicio: dt.datetime = None, hora_final: dt.datetime = None):
        self.nombre = nombre
        self.region = region
        self.descripcion = descripcion
        self.conexiones = conexiones
        self.poblacion_total = poblacion_total
        
        self.generador = GeneradorPorProporcion(poblacion=self.poblacion_total) 
        self.poblacion_flotante = self.poblacion_total * 0.05
        self.clientes_esperando = [] 

    def obtener_resumen(self) -> str:
        """Devuelve un string formateado con los datos principales de la estación."""
        return (
            f"--- {self.nombre} ---\n"
            f"📍 {self.region}\n"
            f"🏙️ {self.descripcion}\n"
            f"🚉 Conexiones: {', '.join(self.conexiones)}\n"
            f"Población: {self.poblacion_total:,}\n"
            f"👥 Clientes esperando: {len(self.clientes_esperando)}\n"
        )

    def simular_generacion_clientes(self, minutos_turno: int):
        # El constructor es None porque estamos usando strings simples como clientes por ahora.
        nuevos_clientes = self.generador.generar_clientes(minutos_turno, constructor=None) 
        self.clientes_esperando.extend(nuevos_clientes)

    def mostrar_info(self):
        print(self.obtener_resumen())

