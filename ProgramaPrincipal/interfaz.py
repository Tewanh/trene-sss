# main.py
import tkinter as tk
from tkinter import messagebox, Canvas, Button, Frame, Toplevel
# Importaciones desde las carpetas logic/ y Models/
from Logic.Guardado import guardar_datos, cargar_datos
from Logic.EstadoDeSimulacion import EstadoSimulacion
from Models.Estaciones import Estacion 
from Models.Trenes import Tren 
from datetime import datetime, timedelta

# Variables globales para simplificar el acceso
app_ventana = None
estado_simulacion_instance = None
frame_control = None 
frame_simulacion_view = None 
canvas_vias = None
TRENES_ACTIVOS = [] 
POSICIONES_X_ESTACIONES = [100, 300, 500, 700]
simulacion_iniciada = False # Bandera para controlar el estado de la simulación
btn_siguiente_turno_ref = None # Referencia al botón Siguiente Turno

# --- Datos y Objetos de las Estaciones ---
ESTACIONES_OBJETOS = [
    Estacion(nombre="Estación Central", region="Región Metropolitana", descripcion="Principal nodo ferroviario del país", conexiones=["Rancagua", "Chillán"], poblacion_total=8242459),
    Estacion(nombre="Rancagua", region="Región de O’Higgins", descripcion="Distancia desde Santiago: ~87 km", conexiones=["Talca", "Estación Central"], poblacion_total=274407),
    Estacion(nombre="Talca", region="Región del Maule", descripcion="Distancia desde Rancagua: ~200 km | Tiempo estimado: 2 h 30 min", conexiones=["Chillán", "Rancagua"], poblacion_total=242344),
    Estacion(nombre="Chillán", region="Región de Ñuble", descripcion="Distancia desde Talca: ~180 km", conexiones=["Talca", "Estación Central"], poblacion_total=204091)
]

# --- Funciones de Lógica de UI ---

def reiniciar_simulacion():
    """Reinicia el estado de la simulación a su punto inicial."""
    global simulacion_iniciada
    
    if messagebox.askokcancel("Reiniciar", "¿Está seguro de querer reiniciar la simulación? Se perderá el progreso actual."):
        # Volver al estado inicial:
        simulacion_iniciada = False
        # Destruir la vista actual de la simulación
        if frame_simulacion_view:
            frame_simulacion_view.destroy()
        # Restablecer el tiempo (usando el valor por defecto de la clase EstadoSimulacion)
        estado_simulacion_instance.tiempo_actual_simulado = datetime.strptime("2015-01-01 07:00:00", "%Y-%m-%d %H:%M:%S")
        estado_simulacion_instance.actualizar_display()
        # Habilitar el botón de Iniciar Simulación si estaba deshabilitado
        # (Actualmente se oculta, así que no hace falta habilitarlo)
        
        # Deshabilitar el botón Siguiente Turno nuevamente
        if btn_siguiente_turno_ref:
            btn_siguiente_turno_ref.config(state=tk.DISABLED)
        
        # Mostrar el botón Iniciar Simulación original (si usas pack_forget en main)
        for widget in app_ventana.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Iniciar Simulación":
                widget.pack(pady=20)


def abrir_menu_eventos():
    """Abre una ventana Toplevel con opciones de eventos."""
    menu_eventos_window = Toplevel(app_ventana)
    menu_eventos_window.title("Menú de Eventos")
    menu_eventos_window.geometry("250x100")
    
    tk.Label(menu_eventos_window, text="Opciones de Eventos:").pack(pady=10)
    
    # Botón para Reiniciar la simulación dentro de esta ventana
    Button(menu_eventos_window, text="Reiniciar Simulación", command=reiniciar_simulacion).pack(pady=10)


def mover_trenes_ui():
    """Llama a la lógica de movimiento y actualiza la UI, solo si la simulación está iniciada."""
    global TRENES_ACTIVOS, canvas_vias

    if not simulacion_iniciada:
        return # No hace nada si no se ha iniciado la simulación

    estado_simulacion_instance.avanzar_una_hora() 

    for tren in TRENES_ACTIVOS:
        tren.mover_siguiente_estacion()
        
        via_y = canvas_vias.winfo_height() / 2
        offset_y = -15 if tren.via == 1 else 15
        pos_y = via_y + offset_y

        pos_x = POSICIONES_X_ESTACIONES[tren.posicion]
        
        if tren.canvas_id:
            canvas_vias.coords(tren.canvas_id, pos_x - 10, pos_y - 5, pos_x + 10, pos_y + 5)


def dibujar_vias_y_estaciones(canvas: Canvas):
    """Dibuja un diseño básico de DOS vías, las estaciones y los trenes iniciales."""
    global TRENES_ACTIVOS, POSICIONES_X_ESTACIONES

    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    via_y_1 = (canvas_height / 2) - 15
    via_y_2 = (canvas_height / 2) + 15
    
    canvas.create_line(50, via_y_1, canvas_width - 50, via_y_1, fill="#555", width=3)
    canvas.create_line(50, via_y_2, canvas_width - 50, via_y_2, fill="#555", width=3)
    
    estaciones_nombres = [e.nombre for e in ESTACIONES_OBJETOS]
    
    for i, x in enumerate(POSICIONES_X_ESTACIONES):
        canvas.create_rectangle(x-15, via_y_1-5, x+15, via_y_2+5, fill="red", outline="black")
        canvas.create_text(x, via_y_2 + 30, text=estaciones_nombres[i], font=("Helvetica", 9, "bold"))

    TRENES_ACTIVOS = [
        Tren(id_tren=1, nombre="BMU", energia="Bimodal", velocidad_max=160, capacidad=236, via=1), 
        Tren(id_tren=2, nombre="EMU", energia="Eléctrico", velocidad_max=120, via=2) 
    ]

    for tren in TRENES_ACTIVOS:
        pos_x = POSICIONES_X_ESTACIONES[tren.posicion] 
        offset_y = -15 if tren.via == 1 else 15
        pos_y = canvas_height / 2 + offset_y

        tren.canvas_id = canvas.create_rectangle(pos_x - 10, pos_y - 5, pos_x + 10, pos_y + 5, 
                                                 fill="blue" if tren.via == 1 else "orange")
        canvas.create_text(pos_x, pos_y, text=tren.nombre, fill="white", font=("Helvetica", 6, "bold"))


def iniciar_simulacion_ui():
    """Configura la interfaz para mostrar la simulación en el panel derecho e inicia la simulación."""
    global frame_simulacion_view, app_ventana, canvas_vias, simulacion_iniciada, btn_siguiente_turno_ref

    simulacion_iniciada = True # Cambiamos la bandera a True

    # Ocultamos el botón de Iniciar Simulación que está en frame_control
    for widget in frame_control.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget("text") == "Iniciar Simulación":
            widget.pack_forget()

    # Habilitamos el botón Siguiente Turno
    if btn_siguiente_turno_ref:
        btn_siguiente_turno_ref.config(state=tk.NORMAL)

    if frame_simulacion_view:
        frame_simulacion_view.destroy()
    
    app_ventana.geometry("800x500")
    
    frame_simulacion_view = Frame(app_ventana, bg='white', padx=10, pady=10)
    frame_simulacion_view.grid(row=0, column=1, sticky="nsew")
    
    canvas_vias = Canvas(frame_simulacion_view, bg='white', highlightthickness=0)
    canvas_vias.pack(fill=tk.BOTH, expand=True)

    canvas_vias.bind("<Configure>", lambda event: dibujar_vias_y_estaciones(canvas_vias))


# --- Funciones Auxiliares (Guardado/Info/Salir) ---
def obtener_estado_actual():
    if estado_simulacion_instance:
        return {"tiempo_actual_simulado": estado_simulacion_instance.tiempo_actual_simulado.strftime("%Y-%m-%d %H:%M:%S")}
    return {}

def cargar_estado():
    # La carga de estado es independiente de si la simulación está iniciada o no
    global estado_simulacion_instance, app_ventana
    datos_cargados = cargar_datos(app_ventana)
    if datos_cargados and estado_simulacion_instance:
        try:
            fecha_cargada = datetime.strptime(datos_cargados["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
            estado_simulacion_instance.tiempo_actual_simulado = fecha_cargada
            estado_simulacion_instance.actualizar_display()
            print(f"Estado cargado. Nuevo tiempo: {fecha_cargada}")
            # Si se carga un estado, se podría considerar iniciar la simulación automáticamente aquí
            if not simulacion_iniciada:
                iniciar_simulacion_ui() 
        except Exception as e:
            messagebox.showerror("Error de datos", f"No se pudieron aplicar los datos cargados: {e}")

def mostrar_info_estaciones(): 
    info = "\n\n".join([e.obtener_resumen() for e in ESTACIONES_OBJETOS])
    messagebox.showinfo("Acerca de Estaciones", info)

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
  app_ventana.geometry("400x450") 

  app_ventana.grid_rowconfigure(0, weight=1)
  app_ventana.grid_columnconfigure(0, weight=0) 
  app_ventana.grid_columnconfigure(1, weight=1) 

  frame_control = Frame(app_ventana, bg='#f0f0f0', width=200, padx=10, pady=10, relief=tk.RAISED)
  frame_control.grid(row=0, column=0, sticky="nsew")
  frame_control.grid_propagate(False) 

  # --- Widgets en el Frame de Control Izquierdo ---

  estado_simulacion_instance = EstadoSimulacion(master=frame_control) 
  estado_simulacion_instance.pack(pady=10, fill=tk.X)

  Button(frame_control, text="Iniciar Simulación", command=iniciar_simulacion_ui, 
         font=("Helvetica", 12, "bold"), bg="green", fg="white", width=20, height=2).pack(pady=10)
  
  # Botón "Siguiente Turno": Inicia deshabilitado (DISABLED)
  btn_siguiente_turno_ref = Button(frame_control, text="Siguiente Turno (+1 Hora)", command=mover_trenes_ui, 
                                   width=20, height=2, state=tk.DISABLED)
  btn_siguiente_turno_ref.pack(pady=10)


  # Botones "Guardar" / "Cargar"
  Button(frame_control, text="Guardar Estado", command=lambda: guardar_datos(obtener_estado_actual(), app_ventana), width=20).pack(pady=5)
  Button(frame_control, text="Cargar Estado", command=cargar_estado, width=20).pack(pady=5)
  
  Frame(frame_control, height=2, bg='gray').pack(fill='x', pady=10)

  # Botón de Eventos (abre una ventana con la opción de Reiniciar)
  Button(frame_control, text="Eventos", command=abrir_menu_eventos, width=20).pack(pady=5)

  # Botones de Ayuda
  Button(frame_control, text="Acerca de Estaciones", command=mostrar_info_estaciones, width=20).pack(pady=5)
  Button(frame_control, text="Acerca de Trenes", command=mostrar_info_trenes, width=20).pack(pady=5) 

  # Botón Salir
  Button(frame_control, text="Salir", command=lambda: salir_app(app_ventana), width=20, bg='red', fg='white').pack(pady=20, side=tk.BOTTOM)
  
  app_ventana.mainloop()

if __name__ == "__main__":
    main()


