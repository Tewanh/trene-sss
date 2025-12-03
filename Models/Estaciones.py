import random
from Models.Clientes import Cliente

class Estacion:
    def __init__(self, nombre, region, descripcion, conexiones, poblacion_total):
        self.nombre = nombre
        self.region = region
        self.descripcion = descripcion
        self.conexiones = conexiones
        self.poblacion_total = poblacion_total

        # Clientes esperando tren en la estación
        self.clientes_esperando = []

        # Población flotante aproximada (20% del total)
        self.poblacion_flotante = int(self.poblacion_total * 0.20)

        # Generador será asignado desde interfaz
        self.generador = None

        # Normalizar nombres y crear mapas
        self.normalizar_nombres()

    # ----------------------------------------------------------
    # NORMALIZACIÓN DE DATOS
    # ----------------------------------------------------------
    def normalizar_nombres(self):
        # Versiones normalizadas (para matching)
        self.nombre_normalizado = self.nombre.strip().lower().replace(" ", "")
        self.region_normalizada = self.region.strip().lower().replace(" ", "")

        # Mapas inversos (evitan errores en interfaz)
        self.regiones_norm_to_original = {
            self.region_normalizada: self.region
        }

        self.destinos_norm_to_original = {
            self.nombre_normalizado: self.nombre
        }

    # ----------------------------------------------------------
    # GENERACIÓN DE CLIENTES
    # ----------------------------------------------------------
    def simular_generacion_clientes(self, minutos_turno, lista_nombres_estaciones):
        """
        Este método es llamado desde interfaz.mover_trenes_ui.
        Produce clientes nuevos según el generador asignado.
        """

        if self.generador is None:
            return []

        nuevos = self.generador.generar_clientes(
            minutos=minutos_turno,
            constructor=lambda origen, tiempo, est=self: Cliente(
                id_cliente=random.randint(1, 9_999_999),
                estacion_origen=est.nombre,
                estacion_destino=random.choice(
                    [x for x in lista_nombres_estaciones if x != est.nombre]
                ),
                tiempo_creacion=tiempo
            )
        )

        # Agregar los nuevos clientes a la estación
        self.clientes_esperando.extend(nuevos)

        return nuevos

    # ----------------------------------------------------------
    # RESUMEN PARA LA INTERFAZ
    # ----------------------------------------------------------
    def obtener_resumen(self):
        return (
            f"Estación: {self.nombre}\n"
            f"Región: {self.region}\n"
            f"Descripción: {self.descripcion}\n"
            f"Conexiones: {', '.join(self.conexiones)}\n"
            f"Población total: {self.poblacion_total}\n"
            f"Población flotante estimada: {self.poblacion_flotante}\n"
            f"Clientes esperando: {len(self.clientes_esperando)}\n"
        )

    # ----------------------------------------------------------
    # REPRESENTACIÓN
    # ----------------------------------------------------------
    def __repr__(self):
        return f"<Estacion {self.nombre} | Esperando: {len(self.clientes_esperando)}>"
