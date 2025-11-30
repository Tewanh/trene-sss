# main.py
import tkinter as tk
from tkinter import messagebox, Canvas, Button, Frame, Toplevel
from Logic.Guardado import guardar_datos, cargar_datos
from Logic.EstadoDeSimulacion import EstadoSimulacion
from Models.Estaciones import Estacion
from Models.Trenes import Tren
from Models.Generador import GeneradorPorProporcion, GeneradorUniforme
from datetime import datetime, timedelta

# =====================================================================================
# VARIABLES GLOBALES
# =====================================================================================
app_ventana = None
estado_simulacion_instance = None
frame_control = None
frame_simulacion_view = None
canvas_vias = None
TRENES_ACTIVOS = []
# Coordenadas X fijas para las estaciones, dentro del rango de 800px de ancho
POSICIONES_X_ESTACIONES = [100, 300, 500, 700]
simulacion_iniciada = False
btn_siguiente_turno_ref = None

# =====================================================================================
# ESTACIONES Y DATOS DE SIMULACIÓN
# =====================================================================================
ESTACIONES_OBJETOS = [
    Estacion("Estación Puerto", "Región Metropolitana",
             "Principal nodo ferroviario del país",
             ["Alameda", "Cordillera"], 8242459),
    Estacion("Estación Alameda", "Región de O’Higgins",
             "Distancia desde Puerto: ~87 km",
             ["El Sol", "Estación Puerto"], 274407),
    Estacion("Estación El Sol", "Región del Maule",
             "Distancia desde Alameda: 200 km",
             ["Cordillera", "Alameda"], 242344),
    Estacion("Estación Cordillera", "Región de Ñuble",
             "Distancia desde El Sol: 180 km",
             ["El Sol", "Estación Puerto"], 204091)
]

DISTANCIAS_KM = [87.0, 200.0, 180.0, 180.0]
VELOCIDAD_TREN = 120.0

for i, est in enumerate(ESTACIONES_OBJETOS):
    g_pro = GeneradorPorProporcion(
        poblacion=est.poblacion_total,
        distancia_media_estaciones_km=DISTANCIAS_KM[i],
        velocidad_media_trenes_kmh=VELOCIDAD_TREN
    )
    est.generador = g_pro
    g_uniforme = GeneradorUniforme(
        poblacion=est.poblacion_total,
        distancia_media_estaciones_km=DISTANCIAS_KM[i],
        velocidad_media_trenes_kmh=VELOCIDAD_TREN
    )
    est.generador_uniforme = g_uniforme

# =====================================================================================
# FUNCIONES DE UI Y LÓGICA
# =====================================================================================

def abrir_ventana_renombrar_estaciones():
    ventana = Toplevel(app_ventana)
    ventana.title("Renombrar Estaciones")
    ventana.geometry("300x250")

    tk.Label(ventana, text="Selecciona estación:").pack(pady=5)
    variable = tk.StringVar(ventana)
    variable.set(ESTACIONES_OBJETOS.nombre) 
    opciones = [e.nombre for e in ESTACIONES_OBJETOS]
    menu = tk.OptionMenu(ventana, variable, *opciones)
    menu.pack(pady=5)

    tk.Label(ventana, text="Nuevo nombre:").pack(pady=5)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.pack(pady=5)

    def aplicar_cambio():
        nombre_actual = variable.get()
        nuevo = entry_nombre.get().strip()
        if not nuevo:
            messagebox.showerror("Error", "Debes escribir un nombre.")
            return

        for e in ESTACIONES_OBJETOS: 
            if e.nombre == nombre_actual:
                e.nombre = nuevo
        
        if canvas_vias:
            canvas_vias.delete("all")
            dibujar_vias_y_estaciones(canvas_vias)
        messagebox.showinfo("Éxito", f"Nombre cambiado a:\n{nuevo}")
        ventana.destroy()

    tk.Button(ventana, text="Aplicar", command=aplicar_cambio).pack(pady=10)

def mostrar_info_estaciones():
    info_total = ""
    for e in ESTACIONES_OBJETOS:
        resumen = e.obtener_resumen()
        if hasattr(e, "generador"):
            t = e.generador.tiempo_viaje_minutos()
            resumen += f"⏱ Tiempo estimado entre estaciones: {t:.1f} min\n"
        info_total += resumen + "\n"
    messagebox.showinfo("Acerca de Estaciones", info_total)

def generar_poblacion_ui():
    resumen_total = ""
    for e in ESTACIONES_OBJETOS:
        if hasattr(e, "generador_uniforme"):
            clientes = e.generador_uniforme.generar_clientes(
                minutos=1, constructor=None 
            )
            e.clientes_esperando.extend(clientes) 
            resumen_total += f"{e.nombre}: {len(clientes)} clientes generados y añadidos a la espera.\n"
    messagebox.showinfo("Población Generada Uniformemente", resumen_total)

def dibujar_vias_y_estaciones(canvas: Canvas):
    global TRENES_ACTIVOS
    
    ancho = canvas.winfo_width()
    alto = canvas.winfo_height()
    
    if ancho < 10 or alto < 10:
        return

    via_y_1 = (alto / 2) - 15
    via_y_2 = (alto / 2) + 15

    if not TRENES_ACTIVOS:
        # Vías (Cubren todo el ancho para incluir todas las estaciones)
        canvas.create_line(50, via_y_1, ancho - 50, via_y_1, fill="#555", width=3)
        canvas.create_line(50, via_y_2, ancho - 50, via_y_2, fill="#555", width=3)

        # Estaciones
        for i, x in enumerate(POSICIONES_X_ESTACIONES):
            canvas.create_rectangle(x-15, via_y_1-5, x+15, via_y_2+5, fill="red", outline="black")
            canvas.create_text(x, via_y_2 + 30, text=ESTACIONES_OBJETOS[i].nombre,
                               font=("Helvetica", 9, "bold"))
        
        # Crear objetos Tren
        TRENES_ACTIVOS.extend([
            Tren(1, "BMU", "Bimodal", 160, capacidad=236, via=1),
            Tren(2, "EMU", "Eléctrico", 120, via=2)
        ])
        for tren in TRENES_ACTIVOS:
            tren.tiempo_restante_min = DISTANCIAS_KM[tren.posicion] / tren.velocidad_max * 60

    # Dibujar/Actualizar trenes en el canvas (se ejecuta siempre)
    for tren in TRENES_ACTIVOS:
        pos_x = POSICIONES_X_ESTACIONES[tren.posicion]
        # Calcula la posición Y exactamente sobre la vía
        pos_y = (via_y_1 + via_y_2) / 2 + (-10 if tren.via == 1 else 10)
        
        if tren.canvas_id is None:
             tren.canvas_id = canvas.create_rectangle(
                pos_x-10, pos_y-5, pos_x+10, pos_y+5,
                fill="blue" if tren.via == 1 else "orange",
                tags=f"tren_{tren.id}" 
            )
             canvas.create_text(pos_x, pos_y, text=tren.nombre, fill="white",
                               font=("Helvetica", 6, "bold"), tags=f"tren_{tren.id}_text")
        else:
            canvas.coords(tren.canvas_id, pos_x-10, pos_y-5, pos_x+10, pos_y+5)
            canvas.coords(f"tren_{tren.id}_text", pos_x, pos_y)


# =====================================================================================
# LÓGICA DE SIMULACIÓN
# =====================================================================================
def reiniciar_simulacion():
    global simulacion_iniciada, TRENES_ACTIVOS
    if messagebox.askokcancel("Reiniciar", "¿Desea reiniciar la simulación?"):
        simulacion_iniciada = False
        estado_simulacion_instance.tiempo_actual_simulado = datetime(2015, 1, 1, 7, 0, 0)
        estado_simulacion_instance.actualizar_display()
        TRENES_ACTIVOS = [] 
        if btn_siguiente_turno_ref:
            btn_siguiente_turno_ref.config(state=tk.DISABLED)
        iniciar_simulacion_ui()


def abrir_menu_eventos():
    menu_eventos_window = Toplevel(app_ventana)
    menu_eventos_window.title("Menú de Eventos")
    menu_eventos_window.geometry("250x100")
    tk.Label(menu_eventos_window, text="Opciones de Eventos:").pack(pady=10)
    Button(menu_eventos_window, text="Reiniciar Simulación", command=reiniciar_simulacion).pack(pady=10)


def mover_trenes_ui():
    global TRENES_ACTIVOS, canvas_vias
    if not simulacion_iniciada:
        return

    estado_simulacion_instance.avanzar_una_hora() # +60 minutos

    for tren in TRENES_ACTIVOS:
        tren.tiempo_restante_min -= 60
        if tren.tiempo_restante_min <= 0:
            tren.mover_siguiente_estacion()
            distancia_al_siguiente = DISTANCIAS_KM[tren.posicion]
            tren.tiempo_restante_min = distancia_al_siguiente / tren.velocidad_max * 60

    for estacion in ESTACIONES_OBJETOS:
        estacion.simular_generacion_clientes(minutos_turno=60) 

    if canvas_vias:
        dibujar_vias_y_estaciones(canvas_vias)


def iniciar_simulacion_ui():
    global frame_simulacion_view, app_ventana, canvas_vias, simulacion_iniciada, btn_siguiente_turno_ref

    simulacion_iniciada = True 

    for widget in frame_control.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget("text") == "Iniciar Simulación":
            widget.pack_forget()

    if btn_siguiente_turno_ref:
        btn_siguiente_turno_ref.config(state=tk.NORMAL)

    if frame_simulacion_view:
        frame_simulacion_view.destroy()
    
    app_ventana.geometry("800x500")
    
    frame_simulacion_view = Frame(app_ventana, bg='white', padx=10, pady=10)
    frame_simulacion_view.grid(row=0, column=1, sticky="nsew")
    
    canvas_vias = Canvas(frame_simulacion_view, bg='white', highlightthickness=0) 
    canvas_vias.pack(fill=tk.BOTH, expand=True)

    canvas_vias.bind("<Configure>", lambda e: dibujar_vias_y_estaciones(canvas_vias))
    

def cargar_estado():
    datos = cargar_datos(app_ventana)
    if datos and "tiempo_actual_simulado" in datos:
        fecha = datetime.strptime(datos["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
        estado_simulacion_instance.tiempo_actual_simulado = fecha
        estado_simulacion_instance.actualizar_display()
        if not simulacion_iniciada:
             iniciar_simulacion_ui()


def mostrar_info_trenes(): 
    info = "\n\n".join([t.obtener_resumen() for t in TRENES_ACTIVOS])
    messagebox.showinfo("Acerca de Trenes", info if info else "No hay trenes activos para mostrar.")

def salir_app(ventana):
  if messagebox.askokcancel("Salir", "¿Estas seguro de querer salir?"):
    ventana.destroy()


# -- MAIN -- #
def main():
  global app_ventana, estado_simulacion_instance, frame_control, btn_siguiente_turno_ref

  app_ventana = tk.Tk()
  app_ventana.title("Ferroviario")
  app_ventana.geometry("800x450") 

  app_ventana.grid_rowconfigure(0, weight=1)
  app_ventana.grid_columnconfigure(0, weight=0) 
  app_ventana.grid_columnconfigure(1, weight=1) 

  frame_control = Frame(app_ventana, bg='#f0f0f0', width=200, padx=10, pady=10, relief=tk.RAISED)
  frame_control.grid(row=0, column=0, sticky="nsew")
  frame_control.grid_propagate(False) 

  estado_simulacion_instance = EstadoSimulacion(master=frame_control) 
  estado_simulacion_instance.pack(pady=10, fill=tk.X)

  Button(frame_control, text="Iniciar Simulación", command=iniciar_simulacion_ui, 
         font=("Helvetica", 12, "bold"), bg="green", fg="white", width=20, height=2).pack(pady=10)
  
  btn_siguiente_turno_ref = Button(frame_control, text="Siguiente Turno", command=mover_trenes_ui, 
                                   width=20, height=2, state=tk.DISABLED)
  btn_siguiente_turno_ref.pack(pady=10)

  Button(frame_control, text="Guardar Estado", 
         command=lambda: guardar_datos({"tiempo_actual_simulado": estado_simulacion_instance.tiempo_actual_simulado.strftime("%Y-%m-%d %H:%M:%S")}, app_ventana), 
         width=20).pack(pady=5)
  Button(frame_control, text="Cargar Estado", command=cargar_estado, width=20).pack(pady=5)
  
  Frame(frame_control, height=2, bg='gray').pack(fill='x', pady=10)

  Button(frame_control, text="Eventos / Reiniciar", command=abrir_menu_eventos, width=20).pack(pady=5)
  Button(frame_control, text="Renombrar Estaciones", command=abrir_ventana_renombrar_estaciones, width=20).pack(pady=5)
  Button(frame_control, text="Generar Población (Test)", command=generar_poblacion_ui, width=20).pack(pady=5) 
  
  Frame(frame_control, height=2, bg='gray').pack(fill='x', pady=10)

  Button(frame_control, text="Acerca de Estaciones", command=mostrar_info_estaciones, width=20).pack(pady=5)
  Button(frame_control, text="Acerca de Trenes", command=mostrar_info_trenes, width=20).pack(pady=5) 

  Button(frame_control, text="Salir", command=lambda: salir_app(app_ventana), width=20, bg='red', fg='white').pack(pady=20, side=tk.BOTTOM)
  
  iniciar_simulacion_ui()  

  app_ventana.mainloop()

if __name__ == "__main__":
    main()
