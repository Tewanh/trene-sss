# Models/Trenes.py
from datetime import datetime, timedelta

class Tren:
    def __init__(self, id_tren: int, nombre: str, energia: str, velocidad_max: int, capacidad: int = None, via: int = 1):
        self.id = id_tren
        self.nombre = nombre
        self.energia = energia
        self.velocidad_max = velocidad_max
        self.capacidad = capacidad if capacidad is not None else 236
        self.posicion = 0
        self.via = via

        # Lista de clientes dentro del tren
        self.pasajeros_actuales = []

        # Tiempo restante para llegar a la siguiente estación (minutos)
        self.tiempo_restante_min = 0.0

        # Dirección: 1 hacia adelante, -1 hacia atrás
        self.direccion = 1

        # --- VELOCIDAD REAL (no máxima) ---
        # Iniciar con una velocidad razonable (no 0 y no la máxima).
        # Usamos la mitad de la velocidad máxima o al menos 10 km/h para que el tren avance.
        self.velocidad_actual = max(10, int(self.velocidad_max * 0.5))

    # -------------------------------------------------------
    #  CÁLCULO DE TIEMPO USANDO velocidad_actual
    # -------------------------------------------------------
    def calcular_tiempo_hasta_siguiente(self, distancia_km: float):
        """
        Calcula el tiempo estimado en minutos para llegar a la siguiente estación,
        basado en velocidad_actual (NO velocidad_max). Evita división por cero.
        """
        vel = max(1, self.velocidad_actual)  # evitar división por cero
        tiempo_total_viaje_min = (distancia_km / vel) * 60.0
        self.tiempo_restante_min = tiempo_total_viaje_min
        return tiempo_total_viaje_min

    # -------------------------------------------------------
    #  ACTUALIZACIÓN DE POSICIÓN (reducción del tiempo restante)
    # -------------------------------------------------------
    def actualizar_posicion(self):
        """
        Reduce el tiempo de viaje 1 minuto (llamado por la simulación por cada minuto).
        Si el tiempo llega a 0 o menos, avanza a la siguiente estación de acuerdo a self.direccion.
        """
        # Se espera que la función que llama a actualizar_posicion lo haga en incrementos de 1 minuto.
        self.tiempo_restante_min -= 1.0

        if self.tiempo_restante_min <= 0:
            # Llegada: mover posición física según dirección
            self.posicion += self.direccion

            # Si tocó extremos, forzamos límites y cambiamos dirección
            # Nota: la simulación (interfaz) usa NUM_ESTACIONES = 4 (0..3)
            if self.posicion >= 3:
                self.posicion = 3
                self.direccion = -1
            elif self.posicion <= 0:
                self.posicion = 0
                self.direccion = 1

    # -------------------------------------------------------
    #  METODO PARA AUMENTAR VELOCIDAD (INTERFAZ)
    # -------------------------------------------------------
    def aumentar_velocidad_actual(self, incremento=10):
        """
        Aumenta la velocidad_actual sin pasar de velocidad_max.
        """
        nueva = self.velocidad_actual + incremento
        if nueva > self.velocidad_max:
            nueva = self.velocidad_max
        self.velocidad_actual = nueva

    # -------------------------------------------------------
    #  Resumen para interfaz
    # -------------------------------------------------------
    def obtener_resumen(self):
        return (
            f"Tren {self.nombre} (ID {self.id})\n"
            f"  Energía: {self.energia}\n"
            f"  Velocidad máxima: {self.velocidad_max} km/h\n"
            f"  Velocidad actual: {self.velocidad_actual} km/h\n"
            f"  Capacidad: {self.capacidad}\n"
            f"  Pasajeros a bordo: {len(self.pasajeros_actuales)}\n"
            f"  Vía: {self.via}\n"
            f"  Posición: {self.posicion}\n"
            f"  Dirección: {'→' if self.direccion == 1 else '←'}\n"
        )


