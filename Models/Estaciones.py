# Models/Estaciones.py — versión totalmente corregida y compatible con tu interfaz

import random
from Models.Generador import GeneradorPeak
from Models.Clientes import Cliente


class Estacion:
    """
    Representa una estación del sistema de trenes.
    Contiene:
    - nombre
    - región
    - descripción
    - conexiones
    - población total
    - generador de clientes
    - clientes esperando en el andén
    """

    def __init__(self, nombre, region, descripcion, conexiones, poblacion_total):
        self.nombre = nombre
        self.region = region
        self.descripcion = descripcion
        self.conexiones = conexiones
        self.poblacion_total = poblacion_total

        # Población flotante (20% ± 1%)
        self.poblacion_flotante = int(self.poblacion_total * random.uniform(0.19, 0.21))

        # Generador de clientes independiente por estación
        self.generador = GeneradorPeak(
            poblacion=self.poblacion_flotante,   # población que realmente viaja
            tasa_base_por_minuto=0.004,
            factor_peak=3.0
        )

        # Lista de clientes esperando en el andén
        self.clientes_esperando = []

        self.normalizar_nombres()

    # ---------------------------------------------------------
    # Normalizar nombres
    # ---------------------------------------------------------
    def normalizar_nombres(self):
        self.nombre = self.nombre.strip()
        self.conexiones = [c.strip() for c in self.conexiones]

    # ---------------------------------------------------------
    # Resumen textual para la interfaz
    # ---------------------------------------------------------
    def obtener_resumen(self):
        return (
            f"📍 {self.nombre}\n"
            f"Región: {self.region}\n"
            f"Descripción: {self.descripcion}\n"
            f"Población total: {self.poblacion_total}\n"
            f"Población flotante estimada: {self.poblacion_flotante}\n"
            f"Clientes esperando: {len(self.clientes_esperando)}\n"
            f"Conexiones: {', '.join(self.conexiones)}\n"
        )

    # ---------------------------------------------------------
    # Generar pasajeros manualmente (si se necesitara)
    # ---------------------------------------------------------
    def generar_pasajeros(self, minutos, lista_estaciones):
        nuevos = self.generador.generar_clientes(
            minutos=minutos,
            constructor=lambda _, tiempo, e=self: Cliente(
                None,
                e.nombre,
                tiempo,
                destino=random.choice([x.nombre for x in lista_estaciones if x.nombre != e.nombre])
            )
        )
        self.clientes_esperando.extend(nuevos)
        return nuevos
