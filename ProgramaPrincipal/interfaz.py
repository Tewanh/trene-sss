# ProgramaPrincipal/interfaz.py — integración final con GeneradorPeak
import tkinter as tk
from tkinter import messagebox, Canvas, Button, Frame, Toplevel, Menu, Scrollbar, Text
from datetime import datetime, timedelta
import random

# Importaciones de los módulos
from Logic.Guardado import guardar_datos, cargar_datos
from Logic.EstadoDeSimulacion import EstadoSimulacion
from Models.Estaciones import Estacion 
from Models.Trenes import Tren
from Models.Clientes import Cliente 
from Models.Generador import GeneradorPeak

# Constantes de datos de simulación
ESTACIONES_DATA = [
    {"nombre": "Estacion Central", "region": "Region Metropolitana", "descripcion": "Principal nodo ferroviario del pais", "conexiones": ["Rancagua", "Chillan"], "poblacion_total": 8242459},
    {"nombre": "Rancagua", "region": "Region de O'Higgins", "descripcion": "Distancia desde Santiago: ~87 km", "conexiones": ["Talca", "Estacion Central"], "poblacion_total": 274407},
    {"nombre": "Talca", "region": "Region del Maule", "descripcion": "Distancia desde Rancagua: ~200 km | Tiempo estimado: 2 h 30 min", "conexiones": ["Chillan", "Rancagua"], "poblacion_total": 242344},
    {"nombre": "Chillan", "region": "Region de Nuble", "descripcion": "Distancia desde Talca: ~180 km", "conexiones": ["Talca", "Estacion Central"], "poblacion_total": 204091}
]
DISTANCIAS_KM = [87.0, 200.0, 180.0] 
NUM_ESTACIONES = len(ESTACIONES_DATA)

# Definimos las posiciones X para 4 estaciones en el canvas
POSICIONES_X_ESTACIONES = [100, 300, 500, 700]


class SimulacionApp:
    def __init__(self, root):        
        self.root = root
        self.root.title("Simulador de Trenes - Proyecto Final")
        self.root.geometry("800x600")

        # Estado de simulacion (se inicializa en configurar_interfaz_principal)
        self.estado_simulacion_instance = None

        # Modelos en memoria
        self.trenes_activos = []
        self.estaciones_objetos = []
        self.simulacion_iniciada = False
        
        # Referencias UI
        self.frame_control = None
        self.frame_simulacion_view = None
        self.canvas_vias = None
        self.btn_siguiente_turno_ref = None
        self.btn_iniciar_simulacion_ref = None 
        self.text_resumen_local = None 

        # Cargar modelos
        self.inicializar_estaciones()

        # Integrar GeneradorPeak (opcion 1: sustituir generacion por defecto)
        total_poblacion = sum(e.poblacion_total for e in self.estaciones_objetos) if self.estaciones_objetos else 1
        self.generador_peak = GeneradorPeak(
            poblacion=total_poblacion,
            tasa_base_por_minuto=0.004,
            factor_peak=3.0
        )

        # Configurar la interfaz (crea EstadoDeSimulacion dentro)
        self.configurar_interfaz_principal()

    def inicializar_estaciones(self):
        # Crea las instancias de Estacion a partir de los datos y normaliza nombres.
        self.estaciones_objetos = []
        for data in ESTACIONES_DATA:
            estacion = Estacion(
                nombre=data['nombre'],
                region=data['region'],
                descripcion=data['descripcion'],
                conexiones=data['conexiones'],
                poblacion_total=data['poblacion_total']
            )
            # Normalizar nombres (metodo en Estacion)
            if hasattr(estacion, "normalizar_nombres"):
                estacion.normalizar_nombres() 
            self.estaciones_objetos.append(estacion)

    def normalizar_nombres_estaciones(self):
        # Helper si en algun momento hay que normalizar toda la lista.
        for e in self.estaciones_objetos:
            e.nombre = e.nombre.strip()
            e.conexiones = [c.strip() for c in e.conexiones]

    # --- Funciones de Logica de Simulacion ---

    def inicializar_trenes_activos(self):
        if not self.trenes_activos:
            self.trenes_activos.extend([
                Tren(id_tren=1, nombre="BMU", energia="Bimodal", velocidad_max=160, capacidad=236, via=1), 
                Tren(id_tren=2, nombre="EMU", energia="Electrico", velocidad_max=120, capacidad=236, via=2) 
            ])
            for tren in self.trenes_activos:
                distancia_al_siguiente = DISTANCIAS_KM[0]
                tren.calcular_tiempo_hasta_siguiente(distancia_al_siguiente)

    def manejar_pasajeros_estacion(self, tren: Tren, estacion: Estacion):
        # Logica de subida y bajada de pasajeros para un tren y estacion especificos.
        bajaron = 0
        subieron = 0
        
        # Normalizar nombre de estacion para comparar
        nombre_estacion_norm = estacion.nombre.strip().lower()

        # 1. Desembarque (comparacion robusta)
        pasajeros_restantes = []
        for p in tren.pasajeros_actuales:
            if isinstance(p, Cliente):
                destino_norm = (getattr(p, 'destino', '') or '').strip().lower()
                if destino_norm == nombre_estacion_norm:
                    bajaron += 1
                    continue
            pasajeros_restantes.append(p)
        tren.pasajeros_actuales = pasajeros_restantes

        # 2. Embarque (subir si la direccion coincide)
        esperando_en_anden = estacion.clientes_esperando
        pasajeros_embarcados = []
        espacio_disponible = min( random.randint(1, 236), max(0, tren.capacidad - len(tren.pasajeros_actuales))
)

        # Precalcular nombres normalizados para mapa
        nombres_estaciones_norm = [e.nombre.strip().lower() for e in self.estaciones_objetos]
        try:
            idx_actual_tren = int(tren.posicion)
        except Exception:
            idx_actual_tren = 0

        for cliente in list(esperando_en_anden):
            if espacio_disponible <= 0:
                break

            destino_cliente_norm = (getattr(cliente, 'destino', '') or '').strip().lower()
            if not destino_cliente_norm:
                continue

            if destino_cliente_norm not in nombres_estaciones_norm:
                continue

            idx_destino = nombres_estaciones_norm.index(destino_cliente_norm)
            destino_esta_adelante_en_mapa = idx_destino > idx_actual_tren
            tren_se_mueve_adelante = getattr(tren, 'direccion', 1) == 1

            if destino_esta_adelante_en_mapa == tren_se_mueve_adelante:
                pasajeros_embarcados.append(cliente)
                try:
                    esperando_en_anden.remove(cliente)
                except ValueError:
                    pass
                espacio_disponible -= 1
                subieron += 1

        tren.pasajeros_actuales.extend(pasajeros_embarcados)
        return bajaron, subieron


    def mover_trenes_ui(self):
        # Avanza la simulacion el minimo tiempo necesario y mueve trenes.
        # Generacion de pasajeros ahora con GeneradorPeak (opcion 1).
        if not self.simulacion_iniciada or not self.trenes_activos:
            return 
        
        tiempos_restantes = [t.tiempo_restante_min for t in self.trenes_activos if t.tiempo_restante_min > 0.01]
        
        if not tiempos_restantes:
            min_delta_minutes = 1 
        else:
            min_delta_minutes = min(tiempos_restantes)
            min_delta_minutes = max(1, round(min_delta_minutes)) 

        # Avanzar el reloj de la simulacion
        if self.estado_simulacion_instance:
            self.estado_simulacion_instance.avanzar_tiempo(timedelta(minutes=min_delta_minutes))

        llegadas_reportadas = []

        for tren in self.trenes_activos:
            tren.tiempo_restante_min -= min_delta_minutes
            
            if tren.tiempo_restante_min <= 0:
                # Mover tren a siguiente estacion
                tren.mover_siguiente_estacion(NUM_ESTACIONES)
                
                estacion_llegada = self.estaciones_objetos[tren.posicion]
                bajaron, subieron = self.manejar_pasajeros_estacion(tren, estacion_llegada) 
                
                llegadas_reportadas.append(
                    f"{tren.nombre} llego a {estacion_llegada.nombre}. Bajan {bajaron} pasajeros, Suben {subieron} subieron. (Total a bordo: {len(tren.pasajeros_actuales)})"
                )
                
                # Calcular tiempo al siguiente tramo
                idx_distancia = min(tren.posicion, NUM_ESTACIONES - 2)
                distancia_al_siguiente = DISTANCIAS_KM[idx_distancia]
                tren.calcular_tiempo_hasta_siguiente(distancia_al_siguiente)
                
        # Generacion de clientes con GeneradorPeak por estacion
        for estacion in self.estaciones_objetos:
            nuevos = estacion.generador.generar_clientes(
                minutos=min_delta_minutes,
                constructor=lambda _, tiempo, e=estacion: Cliente(
                    id_cliente=random.randint(1, 9999999),  # ID único
                    estacion_origen=e.nombre,               # Origen correcto
                    estacion_destino=random.choice([        # Destino correcto
                        est.nombre for est in self.estaciones_objetos
                        if est.nombre != e.nombre
                   ]),
                    tiempo_creacion=tiempo                  # Fecha correcta
    )
)

            if nuevos:
                estacion.clientes_esperando.extend(nuevos)

        # Refrescar UI
        if self.canvas_vias:
            try:
                self.dibujar_vias_y_estaciones(self.canvas_vias)
            except Exception:
                # Falla en dibujado no debe romper la simulacion
                pass
        
        if llegadas_reportadas:
            messagebox.showinfo("Llegada de Tren", "\n".join(llegadas_reportadas))

        if self.text_resumen_local and getattr(self.text_resumen_local, 'winfo_exists', lambda: False)():
            self.actualizar_ventana_informacion_completa()


    # --- Funciones de UI/Visualizacion ---

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
            rect = canvas.create_rectangle(x - 15, via_y_1 - 5, x + 15, via_y_2 + 5, fill="red", outline="black", tags="estacion_clickable")
            canvas.tag_bind(rect, "<Button-1>", lambda e, est=self.estaciones_objetos[i]: self.mostrar_info_estacion(est))
            canvas.create_text(x, via_y_2 + 30, text=self.estaciones_objetos[i].nombre, font=("Helvetica", 9, "bold"), tags="estacion_label")

        canvas.delete("tren")
        canvas.delete("tren_text")
                
        for tren in self.trenes_activos:
            pos_x = POSICIONES_X_ESTACIONES[tren.posicion]
            offset_y = -15 if tren.via == 1 else 15
            pos_y = canvas_height / 2 + offset_y
            canvas.create_rectangle(pos_x-10, pos_y-5, pos_x+10, pos_y+5, fill="blue" if tren.via == 1 else "orange", tags=("tren", f"tren_{tren.id}"))
            canvas.create_text(pos_x, pos_y, text=tren.nombre, fill="white", font=("Helvetica", 6, "bold"), tags=("tren_text", f"tren_{tren.id}_text"))

    def iniciar_simulacion_ui(self):
        if self.simulacion_iniciada: return

        self.inicializar_trenes_activos() 
        self.simulacion_iniciada = True 
        if self.btn_iniciar_simulacion_ref: 
            try:
                self.btn_iniciar_simulacion_ref.pack_forget()
            except Exception:
                pass
        if self.btn_siguiente_turno_ref:
            try:
                self.btn_siguiente_turno_ref.config(state=tk.NORMAL)
            except Exception:
                pass

        self.root.geometry("800x600")
        if self.frame_simulacion_view: 
            try:
                self.frame_simulacion_view.destroy()
            except Exception:
                pass

        self.frame_simulacion_view = Frame(self.root, bg='white', padx=10, pady=10)
        self.root.grid_columnconfigure(1, weight=1) 
        self.frame_simulacion_view.grid(row=0, column=1, sticky="nsew") 
        self.canvas_vias = Canvas(self.frame_simulacion_view, bg='white', highlightthickness=0)
        self.canvas_vias.pack(fill=tk.BOTH, expand=True)
        self.canvas_vias.bind("<Configure>", lambda event: self.dibujar_vias_y_estaciones(self.canvas_vias))
        self.mostrar_ventana_informacion_completa()

    def reiniciar_simulacion(self):
        if messagebox.askokcancel("Reiniciar", "¿Estás seguro de querer reiniciar la simulación a la fecha y hora original y vaciar todos los trenes y estaciones?"):
            fecha_reinicio = datetime(2015, 1, 1, 7, 0, 0)
            if self.estado_simulacion_instance:
                self.estado_simulacion_instance.tiempo_actual_simulado = fecha_reinicio
                try:
                    self.estado_simulacion_instance.actualizar_display()
                except Exception:
                    pass
            for estacion in self.estaciones_objetos: estacion.clientes_esperando = []
            self.trenes_activos = []
            self.inicializar_trenes_activos() 
            if self.simulacion_iniciada:
                if self.canvas_vias:
                    try:
                        self.canvas_vias.delete("all")
                        self.dibujar_vias_y_estaciones(self.canvas_vias)
                    except Exception:
                        pass
                if self.btn_siguiente_turno_ref:
                    try:
                        self.btn_siguiente_turno_ref.config(state=tk.DISABLED)
                    except Exception:
                        pass
                if self.frame_simulacion_view:
                    try:
                        self.frame_simulacion_view.destroy()
                    except Exception:
                        pass
                if self.btn_iniciar_simulacion_ref:
                    try:
                        self.btn_iniciar_simulacion_ref.pack(pady=10, fill=tk.X)
                    except Exception:
                        pass
                messagebox.showinfo("Reinicio Exitoso", "La simulacion ha vuelto a su estado original.")
            self.simulacion_iniciada = False 
            if self.text_resumen_local and getattr(self.text_resumen_local, 'winfo_exists', lambda: False)():
                try:
                    self.text_resumen_local.master.master.destroy()
                except Exception:
                    pass
                self.text_resumen_local = None

    def generar_texto_resumen(self):
        resumen_texto = "--- Estado Actual de la Simulacion ---\n\n"
        for estacion in self.estaciones_objetos: resumen_texto += estacion.obtener_resumen() + "\n" 
        for tren in self.trenes_activos: resumen_texto += tren.obtener_resumen() + "\n"
        return resumen_texto
    
    def actualizar_ventana_informacion_completa(self):
        if self.text_resumen_local and getattr(self.text_resumen_local, 'winfo_exists', lambda: False)():
            self.text_resumen_local.config(state=tk.NORMAL)
            self.text_resumen_local.delete(1.0, tk.END)
            self.text_resumen_local.insert(tk.END, self.generar_texto_resumen())
            self.text_resumen_local.config(state=tk.DISABLED)
            try:
                ventana_info = self.text_resumen_local.master.master
                ventana_info.title(f"Detalles de Simulacion ({self.estado_simulacion_instance.tiempo_actual_simulado.strftime('%H:%M:%S')})")
            except Exception:
                pass
        
    def mostrar_ventana_informacion_completa(self):
        if self.estado_simulacion_instance is None or not self.trenes_activos:
            messagebox.showerror("Error", "La simulacion debe estar iniciada y con trenes activos para ver detalles.")
            return
        if self.text_resumen_local and getattr(self.text_resumen_local, 'winfo_exists', lambda: False)():
            self.actualizar_ventana_informacion_completa()
            try:
                self.text_resumen_local.master.master.lift()
            except Exception:
                pass
            return
        ventana_info = Toplevel(self.root)
        ventana_info.title(f"Detalles de Simulacion ({self.estado_simulacion_instance.tiempo_actual_simulado.strftime('%H:%M:%S')})")
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


    # --- Funciones de Guardado y Carga ---
    
    def obtener_datos_para_guardar_globales(self):
         if self.estado_simulacion_instance is None: return None
         datos = {
            'tiempo_actual_simulado': self.estado_simulacion_instance.tiempo_actual_simulado,
            'estaciones': {e.nombre: {'clientes_esperando': e.clientes_esperando} for e in self.estaciones_objetos}, 
            'trenes_data': [{'id': t.id, 'nombre': t.nombre, 'energia': t.energia, 'velocidad_max': t.velocidad_max, 'capacidad': t.capacidad, 'pasajeros_actuales_list': t.pasajeros_actuales, 'posicion': t.posicion, 'via': t.via, 'direccion': t.direccion} for t in self.trenes_activos],
            'simulacion_iniciada': self.simulacion_iniciada
        }
         return datos

    def cargar_datos_globales(self):
        datos_cargados = cargar_datos(self.root) 
        if datos_cargados:
            try:
                self.estado_simulacion_instance.tiempo_actual_simulado = datos_cargados['tiempo_actual_simulado']
                self.estado_simulacion_instance.actualizar_display()
                # Cargar estaciones (matching por nombre exacto; si pueden diferir por espacios, normalizamos)
                if 'estaciones' in datos_cargados:
                    cargadas = datos_cargados['estaciones']
                    cargadas_norm = {k.strip(): v for k, v in cargadas.items()}
                    for estacion_obj in self.estaciones_objetos:
                        nombre_estacion = estacion_obj.nombre.strip()
                        if nombre_estacion in cargadas_norm:
                            estacion_obj.clientes_esperando = cargadas_norm[nombre_estacion]['clientes_esperando']
                if 'trenes_data' in datos_cargados:
                    self.trenes_activos = [] 
                    for t_data in datos_cargados['trenes_data']:
                        nuevo_tren = Tren(id_tren=t_data['id'], nombre=t_data['nombre'], energia=t_data['energia'], velocidad_max=t_data['velocidad_max'], capacidad=t_data['capacidad'], via=t_data['via'])
                        nuevo_tren.pasajeros_actuales = t_data['pasajeros_actuales_list']
                        nuevo_tren.posicion = t_data['posicion']
                        nuevo_tren.direccion = t_data.get('direccion', 1) 
                        idx_distancia = min(nuevo_tren.posicion, NUM_ESTACIONES - 2)
                        distancia_al_siguiente = DISTANCIAS_KM[idx_distancia]
                        nuevo_tren.calcular_tiempo_hasta_siguiente(distancia_al_siguiente)
                        self.trenes_activos.append(nuevo_tren)
                self.simulacion_iniciada = datos_cargados.get('simulacion_iniciada', False)
                if self.simulacion_iniciada and not self.frame_simulacion_view: self.iniciar_simulacion_ui() 
                if self.canvas_vias: self.canvas_vias.delete("all"); self.dibujar_vias_y_estaciones(self.canvas_vias)
                print(f"Simulacion completamente actualizada a: {self.estado_simulacion_instance.tiempo_actual_simulado}")
                self.actualizar_ventana_informacion_completa()
            except Exception as e:
                messagebox.showerror("Error de carga", f"Error al aplicar los datos cargados a los modelos: {e}")

    # --- Funciones Auxiliares ---
    
    def salir_app(self):
        if messagebox.askokcancel("Salir", "¿Estas seguro de querer salir?"): self.root.destroy()
    
    def mostrar_info_estacion(self, estacion):
        messagebox.showinfo(f"Info Estacion: {estacion.nombre}", estacion.obtener_resumen())
            
    def mostrar_info_estaciones(self): 
        info = "\n\n".join([e.obtener_resumen() for e in self.estaciones_objetos]) 
        messagebox.showinfo("Acerca de Estaciones", info)
        
    def mostrar_info_trenes(self): 
        info = "\n\n".join([t.obtener_resumen() for t in self.trenes_activos])
        messagebox.showinfo("Acerca de Trenes", info if info else "No hay trenes activos para mostrar.")
        
    def generar_poblacion_ui(self):
        if not self.simulacion_iniciada: messagebox.showerror("Error", "Debes iniciar la simulacion primero."); return
        resumen_total = ""
        for e in self.estaciones_objetos: 
            nuevos = e.generador.generar_clientes(
                minutos=60,
                constructor=lambda _, tiempo, est=e: Cliente(
                    None,
                    tiempo,
                    est.nombre,
                    destino=random.choice([es.nombre for es in self.estaciones_objetos if es.nombre != est.nombre])
                )
            )
            e.clientes_esperando.extend(nuevos)
            resumen_total += f"{e.nombre}: {len(e.clientes_esperando)} clientes esperando ahora.\n"
        messagebox.showinfo("Poblacion Generada/Actualizada", resumen_total)
        self.actualizar_ventana_informacion_completa()

    def abrir_ventana_renombrar_estaciones(self):
        if not self.simulacion_iniciada: messagebox.showerror("Error", "Debes iniciar la simulacion primero para usar esta funcion."); return
        ventana = Toplevel(self.root)
        ventana.title("Renombrar Estaciones")
        ventana.geometry("300x250")
        tk.Label(ventana, text="Selecciona estacion:").pack(pady=5)
        variable = tk.StringVar(ventana)
        opciones = [e.nombre for e in self.estaciones_objetos]
        if opciones: variable.set(opciones)
        menu = tk.OptionMenu(ventana, variable, *opciones)
        menu.pack(pady=5)
        tk.Label(ventana, text="Nuevo nombre:").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.pack(pady=5)
        def aplicar_cambio():
            nombre_actual = variable.get()
            nuevo = entry_nombre.get().strip()
            if not nuevo: messagebox.showerror("Error de ingreso", "Debes escribir un nombre valido."); return
            if nuevo in [e.nombre for e in self.estaciones_objetos]: messagebox.showerror("Error de ingreso", f"La estacion '{nuevo}' ya existe."); return
            for e in self.estaciones_objetos:
                if e.nombre == nombre_actual: e.nombre = nuevo
            if self.canvas_vias: self.canvas_vias.delete("all"); self.dibujar_vias_y_estaciones(self.canvas_vias) 
            messagebox.showinfo("Exito", f"Nombre cambiado a:\n{nuevo}")
            self.actualizar_ventana_informacion_completa()
            ventana.destroy()
        tk.Button(ventana, text="Aplicar", command=aplicar_cambio).pack(pady=10)
        
    def abrir_menu_eventos_adicionales(self):
        if not self.simulacion_iniciada:
            messagebox.showerror("Error", "Debes iniciar la simulacion primero para usar los eventos.")
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
            Button(ventana, text=f"{tren.nombre} (Actual: {tren.velocidad_max} km/h)", command=lambda t=tren: self.aplicar_aumento_velocidad(t, ventana)).pack(pady=5)
        
    def aplicar_aumento_velocidad(self, tren, ventana):
        tren.velocidad_max += 20
        messagebox.showinfo("Velocidad Ampliada", f"La nueva velocidad del tren {tren.nombre} es {tren.velocidad_max} km/h")
        idx_distancia = min(tren.posicion, NUM_ESTACIONES - 2)
        distancia_al_siguiente = DISTANCIAS_KM[idx_distancia]
        tren.calcular_tiempo_hasta_siguiente(distancia_al_siguiente)
        self.actualizar_ventana_informacion_completa()
        ventana.destroy()


    # --- Configuracion Principal de la Interfaz ---
    def configurar_interfaz_principal(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0) 
        self.root.grid_columnconfigure(1, weight=1) 
        self.frame_control = Frame(self.root, bg='#f0f0f0', width=200, padx=10, pady=10, relief=tk.RAISED)
        self.frame_control.grid(row=0, column=0, sticky="nsew")
        self.frame_control.grid_propagate(False)
        # Creamos EstadoDeSimulacion dentro del panel (tu clase maneja la fecha/hora)
        try:
            self.estado_simulacion_instance = EstadoSimulacion(master=self.frame_control)
            self.estado_simulacion_instance.pack(pady=10, fill=tk.X)
        except Exception:
            # En caso de fallo con la clase de estado, la dejamos como None pero no rompemos la UI
            self.estado_simulacion_instance = None

        self.btn_iniciar_simulacion_ref = Button(self.frame_control, text="Iniciar Simulacion", font=("Helvetica", 12, "bold"), bg="green", fg="white", width=20, height=2, command=self.iniciar_simulacion_ui)
        self.btn_iniciar_simulacion_ref.pack(pady=10, fill=tk.X)
        self.btn_siguiente_turno_ref = Button(self.frame_control, text="Siguiente Turno", width=20, height=2, state=tk.DISABLED, command=self.mover_trenes_ui)
        self.btn_siguiente_turno_ref.pack(pady=10, fill=tk.X)
        Button(self.frame_control, text="Guardar Estado", width=20, command=lambda: guardar_datos(self.obtener_datos_para_guardar_globales(), self.root)).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Cargar Estado", width=20, command=self.cargar_datos_globales).pack(pady=5, fill=tk.X)
        Frame(self.frame_control, height=2, bg='gray').pack(fill='x', pady=10)
        Button(self.frame_control, text="Reiniciar Simulacion", width=20, command=self.reiniciar_simulacion).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Eventos Adicionales", width=20, command=self.abrir_menu_eventos_adicionales).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Renombrar Estaciones", width=20, command=self.abrir_ventana_renombrar_estaciones).pack(pady=5, fill=tk.X)
        Button(self.frame_control, text="Generar Poblacion (Test)", width=20, command=self.generar_poblacion_ui).pack(pady=5, fill=tk.X) 
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
