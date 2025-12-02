# Models/Trenes.py
import random

class Tren:
    """Representa un tipo de tren con sus características y estado actual."""
    
    def __init__(self, id_tren: int, nombre: str, energia: str, velocidad_max: int, capacidad: int = None, via: int = 1):
        self.id = id_tren
        self.nombre = nombre
        self.energia = energia
        self.velocidad_max = velocidad_max
        self.capacidad = capacidad if capacidad is not None else 236
        self.posicion = 0 # Índice de la estación actual (0 a 3)
        self.via = via    
        self.canvas_id = None 

        # self.pasajeros_actuales pasa de ser un entero a una lista de objetos Cliente (inicialmente vacía)
        self.pasajeros_actuales = [] # <--- MODIFICACIÓN
        self.tiempo_restante_min = 0 
        # NUEVO: 1 = hacia adelante (estación 0 -> 3), -1 = hacia atrás (estación 3 -> 0)
        self.direccion = 1 

    def calcular_tiempo_hasta_siguiente(self, distancia_km: float):
        if self.velocidad_max <= 0:
            self.tiempo_restante_min = 0.0
            return 0.0
        else:
            tiempo_total_viaje_min = (distancia_km / self.velocidad_max) * 60
            self.tiempo_restante_min = tiempo_total_viaje_min
            return tiempo_total_viaje_min

    def mover_siguiente_estacion(self, num_estaciones_totales: int):
        """
        Calcula la nueva posición del tren y cambia la dirección si llega al final.
        num_estaciones_totales debe ser 4 en tu caso.
        """
        
        if self.direccion == 1:
            # Moviéndose hacia adelante: 0 -> 1 -> 2 -> 3
            if self.posicion == num_estaciones_totales - 1:
                # Llegó a la última estación, cambia de dirección
                self.direccion = -1
                self.posicion -= 1
            else:
                self.posicion += 1
        else:
            # Moviéndose hacia atrás: 3 -> 2 -> 1 -> 0
            if self.posicion == 0:
                # Llegó a la primera estación, cambia de dirección
                self.direccion = 1
                self.posicion += 1
            else:
                self.posicion -= 1
        
        # Opcional: Cambiar la vía si cambian de dirección para una mejor visualización
        # self.via = 1 if self.direccion == 1 else 2


    def obtener_resumen(self) -> str:
        """Devuelve un string formateado con los datos principales del tren."""
        resumen = (
            f"--- {self.nombre} (ID: {self.id}) ---\n"
            f"⚡ Energía: {self.energia}\n"
            f"🚀 Velocidad máxima: {self.velocidad_max} km/h\n"
        )
        resumen += f"👥 Capacidad: {self.capacidad} pasajeros\n"
        resumen += f"🚶 Pasajeros actuales: {len(self.pasajeros_actuales)}\n" # <--- MODIFICACIÓN: Usamos len()
        resumen += f"⏱️ Tiempo restante para llegar: {self.tiempo_restante_min:.1f} min\n"
        resumen += f"🔄 Dirección: {'Adelante' if self.direccion == 1 else 'Atrás'}\n"
        
        return resumen


