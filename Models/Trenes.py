# Models/Trenes.py
class Tren:
    """Representa un tipo de tren con sus características y estado actual."""
    def __init__(self, id_tren: int, nombre: str, energia: str, velocidad_max: int, capacidad: int = None, via: int = 1):
        self.id = id_tren
        self.nombre = nombre
        self.energia = energia
        self.velocidad_max = velocidad_max
        self.capacidad = capacidad
        # Estado de simulación inicial
        self.posicion = 0 # Posición inicial en la vía (0 a 3, representando las 4 estaciones)
        self.via = via    # Vía 1 o Vía 2
        self.canvas_id = None # ID del objeto dibujado en el canvas de Tkinter

    def obtener_resumen(self) -> str:
        resumen = (
            f"--- {self.nombre} (ID: {self.id}) ---\n"
            f"⚡ Energía: {self.energia}\n"
            f"🚀 Velocidad máxima: {self.velocidad_max} km/h\n"
        )
        if self.capacidad:
            resumen += f"👥 Capacidad: {self.capacidad} pasajeros\n"
        return resumen
    
    def mover_siguiente_estacion(self):
        """Avanza el tren a la siguiente estación (simulación básica)."""
        # En este ejemplo, simplemente movemos a la siguiente posición.
        # Una lógica real consideraría horarios, distancias, etc.
        self.posicion += 1
        if self.posicion > 3: # Si pasa la última estación, vuelve a la primera (ruta circular simple)
            self.posicion = 0
