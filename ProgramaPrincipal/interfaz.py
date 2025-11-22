# -- Imports -- #
import tkinter as tk
from tkinter import messagebox, Menu, Canvas, Button, Frame, Label, NW
from Logic.Guardado import guardar_datos, cargar_datos
from Logic.EstadoDeSimulacion import EstadoSimulacion
from datetime import datetime, timedelta
import locale

# Variables globales
app_ventana = None
estado_simulacion_instance = None
simulacion_frame = None
lateral_frame = None
menu_archivo_contextual = None 
canvas_vias = None 
btn_siguiente_turno = None
frame_reloj_contenedor = None 

# --- Funciones de Lógica de UI ---

def dibujar_vias_y_estaciones(canvas: Canvas):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    via_y = canvas_height / 2
    canvas.create_line(50, via_y, canvas_width - 50, via_y, fill="#555", width=5)
    
    estaciones_nombres = ["Estación A", "Estación B", "Estación C", "Estación D"]
    posiciones_x = [100, 300, 500, 700]

    for i, x in enumerate(posiciones_x):
        if x < (canvas_width - 20) and x > 20: 
            canvas.create_rectangle(x-15, via_y-10, x+15, via_y+10, fill="red", outline="black")
            canvas.create_text(x, via_y + 25, text=estaciones_nombres[i], font=("Helvetica", 8))

def mostrar_eventos():
    """Muestra un menú contextual con opciones de eventos, incluyendo Reiniciar."""
    if menu_eventos_contextual:
        # Usamos un evento ficticio para posicionar el menú
        # Esto requiere que captures la posición del botón si quieres que aparezca justo debajo.
        # Para simplificar, lo mostramos en el centro de la ventana:
        pos_x = app_ventana.winfo_rootx() + app_ventana.winfo_width() // 2
        pos_y = app_ventana.winfo_rooty() + app_ventana.winfo_height() // 2
        menu_eventos_contextual.tk_popup(pos_x, pos_y, 0)
    else:
        messagebox.showinfo("Eventos", "No hay opciones de eventos disponibles.")


def reiniciar_simulacion():
    """Reinicia la simulación a la fecha y hora iniciales."""
    global estado_simulacion_instance
    if messagebox.askokcancel("Reiniciar Simulación", "¿Está seguro de que desea reiniciar la simulación a la fecha inicial?"):
        fecha_inicio_str = "2015-01-01 07:00:00"
        nueva_fecha = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")
        estado_simulacion_instance.tiempo_actual_simulado = nueva_fecha
        estado_simulacion_instance.actualizar_display()
        # Opcional: Ocultar la visualización del tren si es necesario
        if simulacion_frame.winfo_ismapped():
             simulacion_frame.grid_remove()
        messagebox.showinfo("Reiniciado", "La simulación ha sido reiniciada.")


def iniciar_simulacion_ui():
    """Configura la interfaz para mostrar la simulación y los controles."""
    global simulacion_frame, app_ventana, estado_simulacion_instance, canvas_vias, btn_siguiente_turno

    if simulacion_frame.winfo_ismapped():
        return

    app_ventana.geometry("800x500") 
    
    simulacion_frame.grid() 
    btn_siguiente_turno.grid(row=1, column=0, pady=10) 


# --- Funciones de Guardado y Carga (sin cambios) ---
def handle_guardar():
    datos = obtener_estado_actual()
    guardar_datos(datos, app_ventana)

def handle_cargar():
    datos_cargados = cargar_datos(app_ventana)
    if datos_cargados and estado_simulacion_instance:
        try:
            fecha_cargada = datetime.strptime(datos_cargados["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
            estado_simulacion_instance.tiempo_actual_simulado = fecha_cargada
            estado_simulacion_instance.actualizar_display()
        except Exception as e:
            messagebox.showerror("Error de datos", f"No se pudieron aplicar los datos cargados: {e}")

def obtener_estado_actual():
    if estado_simulacion_instance:
        return {"tiempo_actual_simulado": estado_simulacion_instance.tiempo_actual_simulado.strftime("%Y-%m-%d %H:%M:%S")}
    return {"tiempo_actual_simulado": datetime(2015, 1, 1, 7, 0, 0).strftime("%Y-%m-%d %H:%M:%S")}


# --- Funciones Auxiliares de UI y Menús (sin cambios) ---

def mostrar_menu_archivo(event):
    if menu_archivo_contextual:
        menu_archivo_contextual.tk_popup(event.x_root, event.y_root, 0)
def mostrar_info_estaciones(): messagebox.showinfo("Acerca de Estaciones", "Información detallada sobre las estaciones del sistema ferroviario.")
def mostrar_info_trenes(): messagebox.showinfo("Acerca de Trenes", "Información detallada sobre los trenes y su funcionamiento.")
def salir_app(ventana):
  if messagebox.askokcancel("Salir", "¿Estas seguro de querer salir?"):
    ventana.destroy()


# -- MAIN -- #
def main():
  global app_ventana, estado_simulacion_instance, lateral_frame, menu_archivo_contextual, simulacion_frame, canvas_vias, btn_siguiente_turno, menu_eventos_contextual

  app_ventana = tk.Tk()
  app_ventana.title("Ferroviario")
  app_ventana.geometry("500x450")

  app_ventana.grid_columnconfigure(0, weight=1) 
  app_ventana.grid_columnconfigure(1, weight=3) 
  app_ventana.grid_rowconfigure(0, weight=1)

  # --- Frame Lateral (Botones de Control) ---
  lateral_frame = Frame(app_ventana, bg='#f0f0f0', padx=10, pady=10, bd=1, relief=tk.RAISED)
  lateral_frame.grid(row=0, column=0, sticky="nsew") 

  Label(lateral_frame, text="Panel de Control", font=("Helvetica", 10, "bold"), bg='#f0f0f0').pack(pady=10)

  # Botón "Archivo" (Menú contextual)
  btn_archivo = Button(lateral_frame, text="Archivo", command=None)
  btn_archivo.pack(fill=tk.X, pady=5)
  btn_archivo.bind("<Button-1>", mostrar_menu_archivo)

  menu_archivo_contextual = Menu(app_ventana, tearoff=0)
  menu_archivo_contextual.add_command(label="Guardar Estado", command=handle_guardar)
  menu_archivo_contextual.add_command(label="Cargar Estado", command=handle_cargar)
  menu_archivo_contextual.add_separator()
  menu_archivo_contextual.add_command(label="Salir de la App", command=lambda: salir_app(app_ventana))

  Button(lateral_frame, text="Iniciar Simulación", command=iniciar_simulacion_ui, font=("Helvetica", 10, "bold"), bg="green", fg="white").pack(fill=tk.X, pady=5)
  
  # Botón "Eventos" que ahora despliega un menú
  btn_eventos = Button(lateral_frame, text="Eventos", command=None)
  btn_eventos.pack(fill=tk.X, pady=5)
  btn_eventos.bind("<Button-1>", lambda event: menu_eventos_contextual.tk_popup(event.x_root, event.y_root, 0))

  # Menú contextual de Eventos
  menu_eventos_contextual = Menu(app_ventana, tearoff=0)
  menu_eventos_contextual.add_command(label="Mostrar Eventos del Día (Info)", command=mostrar_eventos)
  menu_eventos_contextual.add_separator()
  menu_eventos_contextual.add_command(label="Reiniciar Simulación", command=reiniciar_simulacion)


  Button(lateral_frame, text="Acerca de Estaciones", command=mostrar_info_estaciones).pack(fill=tk.X, pady=5)
  Button(lateral_frame, text="Acerca de Trenes", command=mostrar_info_trenes).pack(fill=tk.X, pady=5)
  
  # Creación del reloj con lateral_frame como maestro
  estado_simulacion_instance = EstadoSimulacion(master=lateral_frame)
  estado_simulacion_instance.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
  
  
  # --- Pre-creación del Frame de simulación ---
  simulacion_frame = Frame(app_ventana, bg='white', bd=2, relief=tk.GROOVE)
  simulacion_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

  simulacion_frame.grid_rowconfigure(0, weight=1) 
  simulacion_frame.grid_columnconfigure(0, weight=1)

  canvas_vias = Canvas(simulacion_frame, bg='white', highlightthickness=0)
  canvas_vias.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
  canvas_vias.bind("<Configure>", lambda event: dibujar_vias_y_estaciones(canvas_vias))

  # Botón de "Siguiente Turno"
  btn_siguiente_turno = Button(simulacion_frame, text="Siguiente Turno (+1 Hora)", 
                                  command=estado_simulacion_instance.avanzar_una_hora,
                                  font=("Helvetica", 12, "bold"))

  # Ocultamos el frame de simulación inicialmente
  simulacion_frame.grid_remove()

  # 2 Iniciar bucle inicial
  app_ventana.mainloop()

if __name__ == "__main__":
    main()

