# ProgramaPrincipal/interfaz.py  —  VERSIÓN CORREGIDA (reemplazar archivo)
import tkinter as tk
from tkinter import messagebox, Canvas, Button, Frame, Toplevel, Menu, Scrollbar, Text
from datetime import datetime, timedelta
import random

# Importaciones de los módulos (asegúrate que existan)
from Logic.Guardado import guardar_datos, cargar_datos
from Logic.EstadoDeSimulacion import EstadoSimulacion
from Models.Estaciones import Estacion
from Models.Trenes import Tren
from Models.Clientes import Cliente

# Constantes de datos de simulación
ESTACIONES_DATA = [
    {"nombre": "Estacion Central", "region": "Region Metropolitana", "descripcion": "Principal nodo ferroviario del pais", "conexiones": ["Rancagua", "Chillan"], "poblacion_total": 8242459},
    {"nombre": "Rancagua", "region": "Region de O'Higgins", "descripcion": "Distancia desde Santiago: ~87 km", "conexiones": ["Talca", "Estacion Central"], "poblacion_total": 274407},
    {"nombre": "Talca", "region": "Region del Maule", "descripcion": "Distancia desde Rancagua: ~200 km | Tiempo estimado: 2 h 30 min", "conexiones": ["Chillan", "Rancagua"], "poblacion_total": 242344},
    {"nombre": "Chillan", "region": "Region de Nuble", "descripcion": "Distancia desde Talca: ~180 km", "conexiones": ["Talca", "Estacion Central"], "poblacion_total": 204091}
]
DISTANCIAS_KM = [87.0, 200.0, 180.0]
NUM_ESTACIONES = len(ESTACIONES_DATA)
POSICIONES_X_ESTACIONES = [100, 300, 500, 700]


class SimulacionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Trenes - Proyecto Final")
        self.root.geometry("800x600")

        # Estado y modelos
        self.estado_simulacion_instance = None
        self.trenes_activos = []
        self.estaciones_objetos = []
        self.simulacion_iniciada = False

        # UI refs
        self.frame_control = None
        self.frame_simulacion_view = None
        self.canvas_vias = None
        self.btn_siguiente_turno_ref = None
        self.btn_iniciar_simulacion_ref = None
        self.text_resumen_local = None

        # Inicializar modelos y UI
        self.inicializar_estaciones()
        self.configurar_interfaz_principal()

    # -----------------------------
    # Inicializacion estaciones
    # -----------------------------
    def inicializar_estaciones(self):
        self.estaciones_objetos = []
        for data in ESTACIONES_DATA:
            est = Estacion(
                nombre=data['nombre'],
                region=data['region'],
                descripcion=data['descripcion'],
                conexiones=data['conexiones'],
                poblacion_total=data['poblacion_total']
            )
            # Normalizar si existe
            if hasattr(est, "normalizar_nombres"):
                est.normalizar_nombres()
            # Asegurar lista de clientes esperando
            if not hasattr(est, "clientes_esperando"):
                est.clientes_esperando = []
            # poblacion_flotante si no existe
            if not hasattr(est, "poblacion_flotante"):
                est.poblacion_flotante = int(est.poblacion_total * random.uniform(0.19, 0.21))
            self.estaciones_objetos.append(est)

    # -----------------------------
    # Trenes activos
    # -----------------------------
    def inicializar_trenes_activos(self):
        if not self.trenes_activos:
            # Creación de trenes con velocidad_actual inicial razonable
            t1 = Tren(id_tren=1, nombre="BMU", energia="Bimodal", velocidad_max=160, capacidad=236, via=1)
            t2 = Tren(id_tren=2, nombre="EMU", energia="Electrico", velocidad_max=120, capacidad=236, via=2)
            # Si Tren tiene atributo velocidad_actual, asegúrate de que no sea 0 absoluto para que calcule tiempos.
            if not hasattr(t1, "velocidad_actual"):
                t1.velocidad_actual = max(10, int(t1.velocidad_max * 0.5))
            if not hasattr(t2, "velocidad_actual"):
                t2.velocidad_actual = max(10, int(t2.velocidad_max * 0.5))
            self.trenes_activos.extend([t1, t2])
            for tren in self.trenes_activos:
                # recalcular tiempo inicial
                idx = 0
                distancia = DISTANCIAS_KM[idx]
                # calcular_tiempo_hasta_siguiente debe usar velocidad_actual (ver Trenes.py)
                tren.calcular_tiempo_hasta_siguiente(distancia)

    # -----------------------------
    # Subida/Bajada de pasajeros
    # -----------------------------
    def manejar_pasajeros_estacion(self, tren: Tren, estacion: Estacion):
        bajaron = 0
        subieron = 0

        nombre_est_norm = estacion.nombre.strip().lower()

        # Desembarque: pasajeros cuyo destino coincida con estación (destino puede ser string)
        pasajeros_restantes = []
        for p in tren.pasajeros_actuales:
            # p puede ser instancia Cliente con atributo destino o un dict al guardar/cargar
            destino = getattr(p, "destino", None) if not isinstance(p, dict) else p.get("destino")
            if destino and str(destino).strip().lower() == nombre_est_norm:
                bajaron += 1
                # no añadir a pasajeros_restantes
            else:
                pasajeros_restantes.append(p)
        tren.pasajeros_actuales = pasajeros_restantes

        # Embarque: suben si la dirección coincide con la dirección al destino
        esperando = estacion.clientes_esperando
        espacio_disponible = max(0, tren.capacidad - len(tren.pasajeros_actuales))
        if espacio_disponible <= 0:
            return bajaron, 0

        nombres_est_norm = [e.nombre.strip().lower() for e in self.estaciones_objetos]
        idx_actual = int(tren.posicion)

        for cliente in list(esperando):
            if espacio_disponible <= 0:
                break
            destino = getattr(cliente, "destino", None)
            if not destino:
                continue
            destino_norm = str(destino).strip().lower()
            if destino_norm not in nombres_est_norm:
                continue
            idx_dest = nombres_est_norm.index(destino_norm)
            destino_adelante = idx_dest > idx_actual
            tren_va_adelante = getattr(tren, "direccion", 1) == 1
            if destino_adelante == tren_va_adelante:
                # embarcar
                try:
                    esperando.remove(cliente)
                except ValueError:
                    pass
                tren.pasajeros_actuales.append(cliente)
                subieron += 1
                espacio_disponible -= 1

        return bajaron, subieron

    # -----------------------------
    # Movimiento de trenes (turno)
    # -----------------------------
    def mover_trenes_ui(self):
        if not self.simulacion_iniciada or not self.trenes_activos:
            return

        # calcular el delta de minutos mínimo
        tiempos = [max(0.01, t.tiempo_restante_min) for t in self.trenes_activos]
        min_delta = 1 if not tiempos else max(1, round(min(tiempos)))

        # Avanzar reloj simulado
        if self.estado_simulacion_instance:
            self.estado_simulacion_instance.avanzar_tiempo(timedelta(minutes=min_delta))

        llegadas_reportes = []

        for tren in self.trenes_activos:
            tren.tiempo_restante_min -= min_delta
            if tren.tiempo_restante_min <= 0:
                # actualizar posicion (método interno o manual)
                # si Tren tiene mover_siguiente_estacion, úsalo; si no, aplicamos lógica:
                if hasattr(tren, "mover_siguiente_estacion"):
                    tren.mover_siguiente_estacion(NUM_ESTACIONES)
                else:
                    tren.posicion += tren.direccion
                    if tren.posicion >= NUM_ESTACIONES - 1:
                        tren.posicion = NUM_ESTACIONES - 1
                        tren.direccion = -1
                    elif tren.posicion <= 0:
                        tren.posicion = 0
                        tren.direccion = 1

                estacion_llegada = self.estaciones_objetos[tren.posicion]
                bajaron, subieron = self.manejar_pasajeros_estacion(tren, estacion_llegada)

                llegadas_reportes.append(
                    f"{tren.nombre} llegó a {estacion_llegada.nombre}. Bajan {bajaron}, suben {subieron}. A bordo: {len(tren.pasajeros_actuales)}"
                )

                # elegir índice de distancia para el siguiente tramo en función de la dirección
                pos = int(tren.posicion)
                if getattr(tren, "direccion", 1) == 1:
                    idx_dist = min(pos, NUM_ESTACIONES - 2)
                else:
                    idx_dist = max(0, pos - 1)
                distancia_siguiente = DISTANCIAS_KM[idx_dist]
                tren.calcular_tiempo_hasta_siguiente(distancia_siguiente)

        # Generación por estación (cada turno) con tasa aleatoria o usando poblacion_flotante
        for estacion in self.estaciones_objetos:
            # actualizar poblacion flotante entre 19%-21% cada turno (según requisito)
            porcentaje = random.uniform(0.19, 0.21)
            estacion.poblacion_flotante = int(estacion.poblacion_total * porcentaje)

            # Generar algunos clientes por minuto (no toda la población de golpe)
            # Usamos un generador simple: 0.002 * poblacion_flotante por minuto (ajustable)
            tasa_por_minuto = 0.002
            clientes_a_generar = int(estacion.poblacion_flotante * tasa_por_minuto * min_delta)
            # Para no colapsar, cap corto; quita el min() si deseas generar al 100%
            clientes_a_generar = min(clientes_a_generar, 500)  # cap por turno

            nombres_destinos = [e.nombre for e in self.estaciones_objetos if e.nombre != estacion.nombre]
            for _ in range(clientes_a_generar):
                destino = random.choice(nombres_destinos)
                c = Cliente(id=random.randint(1, 99999999), estacion_origen=estacion, destino=destino)
                estacion.clientes_esperando.append(c)

        # Redibujar UI
        if self.canvas_vias:
            try:
                self.dibujar_vias_y_estaciones(self.canvas_vias)
            except Exception:
                pass

        if llegadas_reportes:
            messagebox.showinfo("Llegada de Tren", "\n".join(llegadas_reportes))

        if self.text_resumen_local and getattr(self.text_resumen_local, "winfo_exists", lambda: False)():
            self.actualizar_ventana_informacion_completa()

    # -----------------------------
    # DIBUJADO UI
    # -----------------------------
    def dibujar_vias_y_estaciones(self, canvas: Canvas):
        self.inicializar_trenes_activos()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10:
            return

        via_y_1 = (canvas_height / 2) - 15
        via_y_2 = (canvas_height / 2) + 15

        canvas.delete("via")
        canvas.delete("estacion_clickable")
        canvas.delete("estacion_label")

        canvas.create_line(50, via_y_1, canvas_width - 50, via_y_1, fill="#555", width=3, tags="via")
        canvas.create_line(50, via_y_2, canvas_width - 50, via_y_2, fill="#555", width=3, tags="via")

        for i, x in enumerate(POSICIONES_X_ESTACIONES):
            rect = canvas.create_rectangle(x - 15, via_y_1 - 5, x + 15, via_y_2 + 5,
                                           fill="red", outline="black", tags="estacion_clickable")
            canvas.tag_bind(rect, "<Button-1>", lambda e, est=self.estaciones_objetos[i]: self.mostrar_info_estacion(est))
            canvas.create_text(x, via_y_2 + 30, text=self.estaciones_objetos[i].nombre, font=("Helvetica", 9, "bold"),
                               tags="estacion_label")

        canvas.delete("tren")
        canvas.delete("tren_text")

        for tren in self.trenes_activos:
            pos_x = POSICIONES_X_ESTACIONES[tren.posicion]
            offset_y = -15 if tren.via == 1 else 15
            pos_y = canvas_height / 2 + offset_y
            canvas.create_rectangle(pos_x - 10, pos_y - 5, pos_x + 10, pos_y + 5,
                                    fill="blue" if tren.via == 1 else "orange",
                                    tags=("tren", f"tren_{tren.id}"))
            canvas.create_text(pos_x, pos_y, text=tren.nombre, fill="white", font=("Helvetica", 6, "bold"),
                               tags=("tren_text", f"tren_{tren.id}_text"))

    # -----------------------------
    # INICIAR / REINICIAR
    # -----------------------------
    def iniciar_simulacion_ui(self):
        if self.simulacion_iniciada:
            return
        self.inicializar_trenes_activos()
        self.simulacion_iniciada = True
        if self.btn_iniciar_simulacion_ref:
            try:
                self.btn_iniciar_simulacion_ref.pack_forget()
            except:
                pass
        if self.btn_siguiente_turno_ref:
            try:
                self.btn_siguiente_turno_ref.config(state=tk.NORMAL)
            except:
                pass

        # panel de simulacion
        self.root.geometry("800x600")
        if self.frame_simulacion_view:
            try:
                self.frame_simulacion_view.destroy()
            except:
                pass
        self.frame_simulacion_view = Frame(self.root, bg='white', padx=10, pady=10)
        self.root.grid_columnconfigure(1, weight=1)
        self.frame_simulacion_view.grid(row=0, column=1, sticky="nsew")
        self.canvas_vias = Canvas(self.frame_simulacion_view, bg='white', highlightthickness=0)
        self.canvas_vias.pack(fill=tk.BOTH, expand=True)
        self.canvas_vias.bind("<Configure>", lambda event: self.dibujar_vias_y_estaciones(self.canvas_vias))
        self.mostrar_ventana_informacion_completa()

    def reiniciar_simulacion(self):
        if messagebox.askokcancel("Reiniciar", "¿Estás seguro de reiniciar la simulación a la fecha/hora original y vaciar datos?"):
            fecha_reinicio = datetime(2015, 1, 1, 7, 0, 0)
            if self.estado_simulacion_instance:
                self.estado_simulacion_instance.tiempo_actual_simulado = fecha_reinicio
                try:
                    self.estado_simulacion_instance.actualizar_display()
                except:
                    pass
            for estacion in self.estaciones_objetos:
                estacion.clientes_esperando = []
            self.trenes_activos = []
            self.inicializar_trenes_activos()
            self.simulacion_iniciada = False
            if self.canvas_vias:
                try:
                    self.canvas_vias.delete("all")
                    self.dibujar_vias_y_estaciones(self.canvas_vias)
                except:
                    pass
            if self.btn_siguiente_turno_ref:
                try:
                    self.btn_siguiente_turno_ref.config(state=tk.DISABLED)
                except:
                    pass
            if self.frame_simulacion_view:
                try:
                    self.frame_simulacion_view.destroy()
                except:
                    pass
            if self.btn_iniciar_simulacion_ref:
                try:
                    self.btn_iniciar_simulacion_ref.pack(pady=10, fill=tk.X)
                except:
                    pass
            if self.text_resumen_local and getattr(self.text_resumen_local, "winfo_exists", lambda: False)():
                try:
                    self.text_resumen_local.master.master.destroy()
                except:
                    pass
                self.text_resumen_local = None

    # -----------------------------
    # RESUMEN / INFO
    # -----------------------------
    def generar_texto_resumen(self):
        texto = "--- Estado Actual de la Simulación ---\n\n"
        for est in self.estaciones_objetos:
            texto += est.obtener_resumen() + "\n"
        for tr in self.trenes_activos:
            texto += tr.obtener_resumen() + "\n"
        return texto

    def actualizar_ventana_informacion_completa(self):
        if self.text_resumen_local and getattr(self.text_resumen_local, "winfo_exists", lambda: False)():
            try:
                self.text_resumen_local.config(state=tk.NORMAL)
                self.text_resumen_local.delete(1.0, tk.END)
                self.text_resumen_local.insert(tk.END, self.generar_texto_resumen())
                self.text_resumen_local.config(state=tk.DISABLED)
                ventana_info = self.text_resumen_local.master.master
                ventana_info.title(f"Detalles de Simulación ({self.estado_simulacion_instance.tiempo_actual_simulado.strftime('%H:%M:%S')})")
            except:
                pass

    def mostrar_ventana_informacion_completa(self):
        if self.estado_simulacion_instance is None or not self.trenes_activos:
            messagebox.showerror("Error", "La simulación debe estar iniciada y con trenes activos para ver detalles.")
            return
        if self.text_resumen_local and getattr(self.text_resumen_local, "winfo_exists", lambda: False)():
            self.actualizar_ventana_informacion_completa()
            try:
                self.text_resumen_local.master.master.lift()
            except:
                pass
            return

        ventana_info = Toplevel(self.root)
        ventana_info.title(f"Detalles de Simulación ({self.estado_simulacion_instance.tiempo_actual_simulado.strftime('%H:%M:%S')})")
        ventana_info.geometry("500x500")
        frame_contenedor = Frame(ventana_info)
        frame_contenedor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = Scrollbar(frame_contenedor)
        self.text_resumen_local = Text(frame_contenedor, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Courier", 10))
        scrollbar.config(command=self.text_resumen_local.yview)
        self.text_resumen_local.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_resumen_local.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_resumen_local.insert(tk.END, self.generar_texto_resumen())
        self.text_resumen_local.config(state=tk.DISABLED)

    # -----------------------------
    # Guardado / Carga
    # -----------------------------
    def obtener_datos_para_guardar_globales(self):
        if self.estado_simulacion_instance is None:
            return None
        datos = {
            'tiempo_actual_simulado': self.estado_simulacion_instance.tiempo_actual_simulado,
            'estaciones': {e.nombre: {'clientes_esperando': e.clientes_esperando} for e in self.estaciones_objetos},
            'trenes_data': [{'id': t.id, 'nombre': t.nombre, 'energia': t.energia, 'velocidad_max': t.velocidad_max, 'capacidad': t.capacidad, 'pasajeros_actuales_list': t.pasajeros_actuales, 'posicion': t.posicion, 'via': t.via, 'direccion': t.direccion} for t in self.trenes_activos],
            'simulacion_iniciada': self.simulacion_iniciada
        }
        return datos

    def cargar_datos_globales(self):
        datos_cargados = cargar_datos(self.root)
        if not datos_cargados:
            return
        try:
            # tiempo
            if 'tiempo_actual_simulado' in datos_cargados and self.estado_simulacion_instance:
                t = datos_cargados['tiempo_actual_simulado']
                if isinstance(t, str):
                    try:
                        self.estado_simulacion_instance.tiempo_actual_simulado = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        # intentar asignar tal cual
                        self.estado_simulacion_instance.tiempo_actual_simulado = t
                else:
                    self.estado_simulacion_instance.tiempo_actual_simulado = t
                try:
                    self.estado_simulacion_instance.actualizar_display()
                except:
                    pass

            # estaciones
            if 'estaciones' in datos_cargados:
                ests = datos_cargados['estaciones']
                for e in self.estaciones_objetos:
                    if e.nombre in ests:
                        e.clientes_esperando = ests[e.nombre].get('clientes_esperando', [])

            # trenes
            if 'trenes_data' in datos_cargados:
                self.trenes_activos = []
                for td in datos_cargados['trenes_data']:
                    nuevo = Tren(id_tren=td['id'], nombre=td['nombre'], energia=td['energia'], velocidad_max=td['velocidad_max'], capacidad=td.get('capacidad', 236), via=td.get('via', 1))
                    nuevo.pasajeros_actuales = td.get('pasajeros_actuales_list', [])
                    nuevo.posicion = td.get('posicion', 0)
                    nuevo.direccion = td.get('direccion', 1)
                    idx = min(nuevo.posicion, NUM_ESTACIONES - 2)
                    distancia = DISTANCIAS_KM[idx]
                    nuevo.calcular_tiempo_hasta_siguiente(distancia)
                    self.trenes_activos.append(nuevo)

            self.simulacion_iniciada = datos_cargados.get('simulacion_iniciada', False)
            if self.simulacion_iniciada:
                self.iniciar_simulacion_ui()
            if self.canvas_vias:
                try:
                    self.canvas_vias.delete("all")
                    self.dibujar_vias_y_estaciones(self.canvas_vias)
                except:
                    pass

            self.actualizar_ventana_informacion_completa()
        except Exception as e:
            messagebox.showerror("Error de carga", f"Error al aplicar datos cargados: {e}")

    # -----------------------------
    # Funciones auxiliares / UI pequeñas
    # -----------------------------
    def salir_app(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de querer salir?"):
            self.root.destroy()

    def mostrar_info_estacion(self, estacion):
        try:
            messagebox.showinfo(f"Info Estacion: {estacion.nombre}", estacion.obtener_resumen())
        except Exception:
            messagebox.showinfo("Info Estacion", str(estacion))

    def mostrar_info_estaciones(self):
        info = "\n\n".join([e.obtener_resumen() for e in self.estaciones_objetos])
        messagebox.showinfo("Acerca de Estaciones", info)

    def mostrar_info_trenes(self):
        info = "\n\n".join([t.obtener_resumen() for t in self.trenes_activos])
        messagebox.showinfo("Acerca de Trenes", info if info else "No hay trenes activos para mostrar.")

    # -----------------------------
    # Generar poblacion (boton)
    # -----------------------------
    def generar_poblacion_ui(self):
        if not self.simulacion_iniciada:
            messagebox.showerror("Error", "Debes iniciar la simulación primero.")
            return

        # Para cada estación: generar entre 19% y 21% de su población flotante (tope por seguridad)
        resumen = ""
        MAX_GENERAR = 5000  # tope por estación para no colapsar (ajustable)

        for est in self.estaciones_objetos:
            min_c = int(est.poblacion_total * 0.19)
            max_c = int(est.poblacion_total * 0.21)
            cantidad = random.randint(min_c, max_c)

            # POR SEGURIDAD: cap
            if cantidad > MAX_GENERAR:
                cantidad_a_crear = MAX_GENERAR
            else:
                cantidad_a_crear = cantidad

            destinos = [e.nombre for e in self.estaciones_objetos if e.nombre != est.nombre]
            for i in range(cantidad_a_crear):
                destino = random.choice(destinos)
                c = Cliente(id=random.randint(1, 99999999), estacion_origen=est, destino=destino)
                est.clientes_esperando.append(c)

            resumen += f"{est.nombre}: ahora {len(est.clientes_esperando)} clientes esperando (se generaron {cantidad_a_crear}).\n"

        messagebox.showinfo("Población Generada/Actualizada", resumen)
        self.actualizar_ventana_informacion_completa()

    # -----------------------------
    # Ventana renombrar estaciones
    # -----------------------------
    def abrir_ventana_renombrar_estaciones(self):
        if not self.simulacion_iniciada:
            messagebox.showerror("Error", "Debes iniciar la simulación primero para usar esta función.")
            return
        ventana = Toplevel(self.root)
        ventana.title("Renombrar Estaciones")
        ventana.geometry("300x250")
        tk.Label(ventana, text="Selecciona estación:").pack(pady=5)
        variable = tk.StringVar(ventana)
        opciones = [e.nombre for e in self.estaciones_objetos]
        if opciones:
            variable.set(opciones[0])
        menu = tk.OptionMenu(ventana, variable, *opciones)
        menu.pack(pady=5)
        tk.Label(ventana, text="Nuevo nombre:").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.pack(pady=5)

        def aplicar_cambio():
            nombre_actual = variable.get()
            nuevo = entry_nombre.get().strip()
            if not nuevo:
                messagebox.showerror("Error de ingreso", "Debes escribir un nombre válido.")
                return
            if nuevo in [e.nombre for e in self.estaciones_objetos]:
                messagebox.showerror("Error de ingreso", f"La estación '{nuevo}' ya existe.")
                return
            for e in self.estaciones_objetos:
                if e.nombre == nombre_actual:
                    e.nombre = nuevo
            if self.canvas_vias:
                try:
                    self.canvas_vias.delete("all")
                    self.dibujar_vias_y_estaciones(self.canvas_vias)
                except:
                    pass
            messagebox.showinfo("Éxito", f"Nombre cambiado a: {nuevo}")
            self.actualizar_ventana_informacion_completa()
            ventana.destroy()

        tk.Button(ventana, text="Aplicar", command=aplicar_cambio).pack(pady=10)

    # -----------------------------
    # Eventos adicionales + aumentar velocidad
    # -----------------------------
    def abrir_menu_eventos_adicionales(self):
        if not self.simulacion_iniciada:
            messagebox.showerror("Error", "Debes iniciar la simulación primero para usar los eventos.")
            return
        menu_eventos_window = Toplevel(self.root)
        menu_eventos_window.title("Eventos Adicionales")
        Button(menu_eventos_window, text="Aumentar Velocidad de Tren", command=self.menu_aumentar_velocidad).pack(pady=10)

    def menu_aumentar_velocidad(self):
        if not self.trenes_activos:
            messagebox.showerror("Error", "No hay trenes activos.")
            return
        ventana = Toplevel(self.root)
        ventana.title("Aumentar Velocidad")
        for tren in self.trenes_activos:
            # Mostrar velocidad_actual si existe, sino velocidad_max
            vel_actual = getattr(tren, "velocidad_actual", getattr(tren, "velocidad_max", 0))
            Button(ventana, text=f"{tren.nombre} (Actual: {vel_actual} km/h)", command=lambda t=tren: self.aplicar_aumento_velocidad(t, ventana)).pack(pady=5)

    def aplicar_aumento_velocidad(self, tren, ventana):
        # Aumenta velocidad_actual sin cambiar velocidad_max
        nueva = getattr(tren, "velocidad_actual", None)
        if nueva is None:
            nueva = getattr(tren, "velocidad_max", 0)
        nueva = nueva + 20
        if nueva > tren.velocidad_max:
            nueva = tren.velocidad_max
        tren.velocidad_actual = nueva

        # Recalcular tiempo al siguiente tramo teniendo en cuenta dirección
        pos = int(tren.posicion)
        if getattr(tren, "direccion", 1) == 1:
            idx = min(pos, NUM_ESTACIONES - 2)
        else:
            idx = max(0, pos - 1)
        distancia = DISTANCIAS_KM[idx]
        tren.calcular_tiempo_hasta_siguiente(distancia)

        messagebox.showinfo("Velocidad Ampliada", f"La velocidad actual del tren {tren.nombre} es {tren.velocidad_actual} km/h (máx {tren.velocidad_max}).")
        ventana.destroy()
        self.actualizar_ventana_informacion_completa()

    # -----------------------------
    # Configuración principal de la interfaz (panel izquierdo)
    # -----------------------------
    def configurar_interfaz_principal(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        self.frame_control = Frame(self.root, bg='#f0f0f0', width=200, padx=10, pady=10, relief=tk.RAISED)
        self.frame_control.grid(row=0, column=0, sticky="nsew")
        self.frame_control.grid_propagate(False)

        # Estado de simulacion (reloj)
        try:
            self.estado_simulacion_instance = EstadoSimulacion(master=self.frame_control)
            self.estado_simulacion_instance.pack(pady=10, fill=tk.X)
        except Exception:
            self.estado_simulacion_instance = None

        self.btn_iniciar_simulacion_ref = Button(self.frame_control, text="Iniciar Simulación", font=("Helvetica", 12, "bold"), bg="green", fg="white", width=20, height=2, command=self.iniciar_simulacion_ui)
        self.btn_iniciar_simulacion_ref.pack(pady=10, fill=tk.X)

        self.btn_siguiente_turno_ref = Button(self.frame_control, text="Siguiente Turno", width=20, height=2, state=tk.DISABLED, command=self.mover_trenes_ui)
        self.btn_siguiente_turno_ref.pack(pady=10, fill=tk.X)

        Button(self.frame_control, text="Guardar Estado", width=20, command=lambda: guardar_datos(self.obtener_datos_para_guardar_globales(), self.root)).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Cargar Estado", width=20, command=self.cargar_datos_globales).pack(pady=5, fill=tk.X)
        Frame(self.frame_control, height=2, bg='gray').pack(fill='x', pady=10)
        Button(self.frame_control, text="Reiniciar Simulación", width=20, command=self.reiniciar_simulacion).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Eventos Adicionales", width=20, command=self.abrir_menu_eventos_adicionales).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Renombrar Estaciones", width=20, command=self.abrir_ventana_renombrar_estaciones).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Generar Población (Test)", width=20, command=self.generar_poblacion_ui).pack(pady=5, fill=tk.X)
        Frame(self.frame_control, height=2, bg='gray').pack(fill='x', pady=10)
        Button(self.frame_control, text="Acerca de Estaciones", width=20, command=self.mostrar_info_estaciones).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Acerca de Trenes", width=20, command=self.mostrar_info_trenes).pack(pady=5, fill=tk.X)
        Frame(self.frame_control, bg='#f0f0f0').pack(fill=tk.BOTH, expand=True)
        Button(self.frame_control, text="Salir", width=20, bg='red', fg='white', command=self.salir_app).pack(pady=10, padx=10, fill=tk.X)


# -- MAIN EXECUTION BLOCK (Fuera de la clase) -- #

def main():
    root = tk.Tk()
    app = SimulacionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
