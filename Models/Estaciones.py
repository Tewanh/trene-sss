# Models/Estaciones.py
import datetime as dt
import random

class Estacion:
    """Representa una estación de tren con sus datos y lógica de simulación."""

    def __init__(self, nombre: str, region: str, descripcion: str, conexiones: list[str], poblacion_total: int, hora_inicio: dt.datetime = None, hora_final: dt.datetime = None):
        self.nombre = nombre
        self.region = region
        self.descripcion = descripcion
        self.conexiones = conexiones
        self.poblacion_total = poblacion_total
        
        # self.generador = Generador(hora_inicio, hora_final) # Comentado si Generador no existe
        self.poblacion_flotante = self.poblacion_total * 0.05

    def obtener_resumen(self) -> str:
        """Devuelve un string formateado con los datos principales de la estación."""
        return (
            f"--- {self.nombre} ---\n"
            f"📍 {self.region}\n"
            f"🏙️ {self.descripcion}\n"
            f"🚉 Conexiones: {', '.join(self.conexiones)}\n"
            f"Población: {self.poblacion_total:,}\n"
        )

    # Puedes mantener mostrar_info si lo usas para debuggear en consola
    def mostrar_info(self):
        print(self.obtener_resumen())
