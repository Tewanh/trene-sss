# Models/Trenes.py
import random

class Tren:
    """Representa un tipo de tren con sus características y estado actual."""
    
    def __init__(self, id_tren: int, nombre: str, energia: str, velocidad_max: int, capacidad: int = None, via: int = 1):
        self.id = id_tren
        self.nombre = nombre
        self.energia = energia
        self.velocidad_max = velocidad_max
        self.capacidad = capacidad
        self.posicion = 0 # Estación actual (índice de 0 a 3)
        self.via = via    # Vía 1 o Vía 2
        self.canvas_id = None # ID del objeto dibujado en el canvas de Tkinter

        self.pasajeros_a_bordo = random.randint(0, self.capacidad if self.capacidad else 100)
        self.tiempo_restante_min = 0

    def calcular_tiempo_hasta_siguiente(self, distancia_km: float):
        if self.velocidad_max <= 0:
            self.tiempo_restante_min = 0
        else:
            self.tiempo_restante_min = round((distancia_km / self.velocidad_max) * 60)

    def mover_siguiente_estacion(self):
        if self.tiempo_restante_min > 0:
            self.tiempo_restante_min -= 60  
            if self.tiempo_restante_min < 0:
                self.tiempo_restante_min = 0
        else:
            self.posicion += 1
            if self.posicion > 3:
                self.posicion = 0
            # Simulación: Cambia el número de pasajeros al llegar a la estación
            self.pasajeros_a_bordo = random.randint(0, self.capacidad if self.capacidad else 100)

    def obtener_resumen(self) -> str:
        resumen = (
            f"--- {self.nombre} (ID: {self.id}) ---\n"
            f"⚡ Energía: {self.energia}\n"
            f"🚀 Velocidad máxima: {self.velocidad_max} km/h\n"
        )
        if self.capacidad:
            resumen += f"👥 Capacidad: {self.capacidad} pasajeros\n"
        
        resumen += f"🧑‍⚖️ Pasajeros a bordo: {self.pasajeros_a_bordo}\n"
        resumen += f"⏱️ Tiempo restante para llegar: {self.tiempo_restante_min} min\n"
        return resumen
