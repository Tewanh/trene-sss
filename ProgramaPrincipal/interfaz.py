# ProgramaPrincipal/interfaz.py
import tkinter as tk
from tkinter import messagebox, Canvas, Button, Frame, Toplevel
# Importaciones desde las carpetas logic/ y Models/
from Logic.Guardado import guardar_datos, cargar_datos
from Logic.EstadoDeSimulacion import EstadoSimulacion
from Models.Estaciones import Estacion 
from Models.Trenes import Tren 
from datetime import datetime, timedelta
import random
# Se mantiene la importación para el otro botón de eventos adicionales
from Ui.eventos_ui import crear_ventana_eventos


# =====================================================================================
# VARIABLES GLOBALES
# =====================================================================================
app_ventana = None
estado_simulacion_instance = None
frame_control = None 
frame_simulacion_view = None 
canvas_vias = None
TRENES_ACTIVOS = [] 
POSICIONES_X_ESTACIONES = [100, 300, 500, 700]
simulacion_iniciada = False 
btn_siguiente_turno_ref = None 

# =====================================================================================
# ESTACIONES Y DATOS DE SIMULACIÓN
# =====================================================================================
ESTACIONES_OBJETOS = [
    Estacion(nombre="Estación Central", region="Región Metropolitana", descripcion="Principal nodo ferroviario del país", conexiones=["Rancagua", "Chillán"], poblacion_total=8242459),
    Estacion(nombre="Rancagua", region="Región de O’Higgins", descripcion="Distancia desde Santiago: ~87 km", conexiones=["Talca", "Estación Central"], poblacion_total=274407),
    Estacion(nombre="Talca", region="Región del Maule", descripcion="Distancia desde Rancagua: ~200 km | Tiempo estimado: 2 h 30 min", conexiones=["Chillán", "Rancagua"], poblacion_total=242344),
    Estacion(nombre="Chillán", region="Región de Ñuble", descripcion="Distancia desde Talca: ~180 km", conexiones=["Talca", "Estación Central"], poblacion_total=204091)
]

DISTANCIAS_KM = [87.0, 200.0, 180.0, 180.0]
VELOCIDAD_TREN = 120.0

# =====================================================================================
# FUNCIONES DE UI Y LÓGICA PRINCIPAL (Definidas primero para que puedan ser usadas como command)
# =====================================================================================

def dibujar_vias_y_estaciones(canvas: Canvas):
    """Dibuja un diseño básico de DOS vías, las estaciones y los trenes."""
    global TRENES_ACTIVOS, POSICIONES_X_ESTACIONES

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    if canvas_width < 10 or canvas_height < 10:
        return

    via_y_1 = (canvas_height / 2) - 15
    via_y_2 = (canvas_height / 2) + 15
    
    if not canvas.find_withtag("estacion"):
        canvas.create_line(50, via_y_1, canvas_width - 50, via_y_1, fill="#555", width=3, tags="via")
        canvas.create_line(50, via_y_2, canvas_width - 50, via_y_2, fill="#555", width=3, tags="via")
        
        estaciones_nombres = [e.nombre for e in ESTACIONES_OBJETOS]
        for i, x in enumerate(POSICIONES_X_ESTACIONES):
            canvas.create_rectangle(x-15, via_y_1-5, x+15, via_y_2+5, fill="red", outline="black", tags="estacion")
            canvas.create_text(x, via_y_2 + 30, text=estaciones_nombres[i], font=("Helvetica", 9, "bold"), tags="estacion_label")

    if not TRENES_ACTIVOS:
        TRENES_ACTIVOS.extend([
            Tren(id_tren=1, nombre="BMU", energia="Bimodal", velocidad_max=160, capacidad=236, via=1), 
            Tren(id_tren=2, nombre="EMU", energia="Eléctrico", velocidad_max=120, capacidad=236, via=2) 
        ])
        for tren in TRENES_ACTIVOS:
            distancia_al_siguiente = DISTANCIAS_KM[tren.posicion]
            tren.tiempo_restante_min = distancia_al_siguiente / tren.velocidad_max * 60

    for tren in TRENES_ACTIVOS:
        pos_x = POSICIONES_X_ESTACIONES[tren.posicion] 
        offset_y = -15 if tren.via == 1 else 15
        pos_y = canvas_height / 2 + offset_y

        if tren.canvas_id is None:
             tren.canvas_id = canvas.create_rectangle(
                pos_x-10, pos_y-5, pos_x+10, pos_y+5,
                fill="blue" if tren.via == 1 else "orange",
                tags=f"tren_{tren.id}" 
            )
             canvas.create_text(pos_x, pos_y, text=tren.nombre, fill="white",
                               font=("Helvetica", 6, "bold"), tags=f"tren_{tren.id}_text")
        else:
            canvas.coords(tren.canvas_id, pos_x - 10, pos_y - 5, pos_x + 10, pos_y + 5)
            canvas.coords(f"tren_{tren.id}_text", pos_x, pos_y)


def mover_trenes_ui():
    """
    Llama a la lógica de movimiento, avanza el tiempo y actualiza la UI.
    Implementa la lógica de subida de pasajeros.
    """
    global TRENES_ACTIVOS, canvas_vias, simulacion_iniciada, btn_siguiente_turno_ref

    if not simulacion_iniciada:
        return 

    estado_simulacion_instance.avanzar_una_hora() # +60 minutos

    for tren in TRENES_ACTIVOS:
        tren.tiempo_restante_min -= 60
        
        if tren.tiempo_restante_min <= 0:
            tren.mover_siguiente_estacion()
            distancia_al_siguiente = DISTANCIAS_KM[tren.posicion]
            tren.tiempo_restante_min = distancia_al_siguiente / tren.velocidad_max * 60
            
            estacion_actual_obj = ESTACIONES_OBJETOS[tren.posicion]
            clientes_esperando = estacion_actual_obj.clientes_esperando
            
            capacidad_disponible = tren.capacidad - tren.pasajeros_actuales if tren.capacidad else 1000
            max_subir = min(len(clientes_esperando), capacidad_disponible)
            
            if max_subir > 0:
                cantidad_a_subir = random.randint(0, max_subir) 
                
                estacion_actual_obj.clientes_esperando = clientes_esperando[:-cantidad_a_subir]
                tren.pasajeros_actuales += cantidad_a_subir

    # REQUISITO 1: Recalcular la población flotante para el próximo turno (19%-21%)
    for estacion in ESTACIONES_OBJETOS:
        porcentaje = random.uniform(0.19, 0.21) 
        estacion.poblacion_flotante = int(estacion.poblacion_total * porcentaje)

    for estacion in ESTACIONES_OBJETOS:
        estacion.simular_generacion_clientes(minutos_turno=60) 

    if canvas_vias:
        dibujar_vias_y_estaciones(canvas_vias)


def iniciar_simulacion_ui():
    """Configura la interfaz para mostrar la simulación en el panel derecho e inicia la simulación."""
    global frame_simulacion_view, app_ventana, canvas_vias, simulacion_iniciada, btn_siguiente_turno_ref

    if simulacion_iniciada: return

    # Generar población inicial para que los trenes tengan clientes que recoger en el primer turno
    for estacion in ESTACIONES_OBJETOS:
        estacion.simular_generacion_clientes(minutos_turno=60)

    # REQUISITO 1 (inicial): Recalcular la población flotante inicial (19%-21%)
    for estacion in ESTACIONES_OBJETOS:
        porcentaje = random.uniform(0.19, 0.21) 
        estacion.poblacion_flotante = int(estacion.poblacion_total * porcentaje)

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

    canvas_vias.bind("<Configure>", lambda event: dibujar_vias_y_estaciones(canvas_vias))


def reiniciar_simulacion():
    """Reinicia el estado de la simulación a su punto inicial."""
    global simulacion_iniciada, TRENES_ACTIVOS
    
    if messagebox.askokcancel("Reiniciar", "¿Está seguro de querer reiniciar la simulación? Se perderá el progreso actual."):
        simulacion_iniciada = False
        estado_simulacion_instance.tiempo_actual_simulado = datetime.strptime("2015-01-01 07:00:00", "%Y-%m-%d %H:%M:%S")
        estado_simulacion_instance.actualizar_display()
        TRENES_ACTIVOS = [] # Limpiamos la lista de trenes para que se regeneren al iniciar UI

        if btn_siguiente_turno_ref:
            btn_siguiente_turno_ref.config(state=tk.DISABLED)
        
        # Ocultar la vista de simulación
        if frame_simulacion_view:
            frame_simulacion_view.destroy()

        # Mostrar el botón Iniciar Simulación original
        for widget in frame_control.winfo_children():
             if isinstance(widget, tk.Button) and widget.cget("text") == "Iniciar Simulación":
                widget.pack(pady=10)

# =====================================================================================
# FUNCIONES AUXILIARES (Guardado/Info/Salir/Eventos Adicionales)
# =====================================================================================

def obtener_estado_actual():
    """Devuelve un diccionario con el estado actual de la simulación para guardar."""
    if estado_simulacion_instance:
        return {"tiempo_actual_simulado": estado_simulacion_instance.tiempo_actual_simulado.strftime("%Y-%m-%d %H:%M:%S")}
    return {}

def cargar_estado():
    """Maneja la carga de datos desde archivo y actualiza la UI."""
    global estado_simulacion_instance, app_ventana, simulacion_iniciada
    datos_cargados = cargar_datos(app_ventana) # cargar_datos ya maneja excepciones y UI
    if datos_cargados and estado_simulacion_instance:
        try:
            fecha_cargada = datetime.strptime(datos_cargados["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
            estado_simulacion_instance.tiempo_actual_simulado = fecha_cargada
            estado_simulacion_instance.actualizar_display()
            
            if not simulacion_iniciada:
                iniciar_simulacion_ui() 
        except ValueError:
            messagebox.showerror("Error de datos", "El formato de fecha en el archivo cargado es incorrecto.")
        except Exception as e:
            messagebox.showerror("Error de datos", f"No se pudieron aplicar los datos cargados: {e}")

def aplicar_estado_desde_guardado(datos_cargados):
    """Callback usado por eventos_ui.py para aplicar un estado cargado o reiniciado."""
    if datos_cargados and "tiempo_actual_simulado" in datos_cargados:
        try:
            fecha = datetime.strptime(datos_cargados["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
            estado_simulacion_instance.tiempo_actual_simulado = fecha
            estado_simulacion_instance.actualizar_display()
            if not simulacion_iniciada:
                 iniciar_simulacion_ui()
        except ValueError:
            messagebox.showerror("Error de Carga", "El formato de fecha en el archivo es incorrecto.")

def mostrar_info_estaciones(): 
    info = "\n\n".join([e.obtener_resumen() for e in ESTACIONES_OBJETOS])
    messagebox.showinfo("Acerca de Estaciones", info)

def mostrar_info_trenes(): 
    info = "\n\n".join([t.obtener_resumen() for t in TRENES_ACTIVOS])
    messagebox.showinfo("Acerca de Trenes", info if info else "No hay trenes activos para mostrar.")

def salir_app(ventana):
  if messagebox.askokcancel("Salir", "¿Estas seguro de querer salir?"):
    ventana.destroy()

def abrir_ventana_renombrar_estaciones():
    ventana = Toplevel(app_ventana)
    ventana.title("Renombrar Estaciones")
    ventana.geometry("300x250")
    tk.Label(ventana, text="Selecciona estación:").pack(pady=5)
    variable = tk.StringVar(ventana)
    opciones = [e.nombre for e in ESTACIONES_OBJETOS]
    if opciones:
        variable.set(opciones[0]) # Inicializar con el primer nombre
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

        if nuevo in [e.nombre for e in ESTACIONES_OBJETOS]:
             messagebox.showerror("Error de ingreso", f"La estación '{nuevo}' ya existe.")
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

def generar_poblacion_ui():
    if not simulacion_iniciada:
        messagebox.showerror("Error", "Debes iniciar la simulación primero.")
        return
        
    resumen_total = ""
    for e in ESTACIONES_OBJETOS:
        clientes = e.generador.generar_clientes(
            minutos=60, constructor=None 
        )
        e.clientes_esperando.extend(clientes) 
        resumen_total += f"{e.nombre}: {len(clientes)} clientes generados y añadidos a la espera.\n"
    messagebox.showinfo("Población Generada", resumen_total)


def abrir_menu_eventos_adicionales():
    if not simulacion_iniciada:
        messagebox.showerror("Error", "Debes iniciar la simulación primero para usar los eventos.")
        return
        
    menu_eventos_window = Toplevel(app_ventana)
    menu_eventos_window.title("Eventos Adicionales")
    menu_eventos_window.geometry("250x100")
    tk.Label(menu_eventos_window, text="Opciones de Eventos:").pack(pady=10)
    Button(
        menu_eventos_window,
        text="Aumentar Velocidad de Tren",
        command=menu_aumentar_velocidad
    ).pack(pady=10)

def menu_aumentar_velocidad():
    if not TRENES_ACTIVOS:
        messagebox.showerror("Error", "No hay trenes activos.")
        return
    ventana = Toplevel(app_ventana)
    ventana.title("Aumentar Velocidad")
    ventana.geometry("300x200")
    tk.Label(ventana, text="Selecciona un tren para aumentar su velocidad:").pack(pady=10)
    for tren in TRENES_ACTIVOS:
        Button(
            ventana,
            text=f"{tren.nombre} (Actual: {tren.velocidad_max} km/h)",
            command=lambda t=tren: aplicar_aumento_velocidad(t, ventana) 
        ).pack(pady=5)

def aplicar_aumento_velocidad(tren, ventana):
    tren.velocidad_max += 20
    messagebox.showinfo(
        "Velocidad Aumentada",
        f"La nueva velocidad del tren {tren.nombre} es {tren.velocidad_max} km/h"
    )
    distancia_al_siguiente = DISTANCIAS_KM[tren.posicion]
    try:
        tren.tiempo_restante_min = distancia_al_siguiente / tren.velocidad_max * 60
    except ZeroDivisionError:
        tren.tiempo_restante_min = 0

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

  estado_simulacion_instance = EstadoSimulacion(master=frame_control) 
  estado_simulacion_instance.pack(pady=10, fill=tk.X)

  Button(frame_control, text="Iniciar Simulación", command=iniciar_simulacion_ui, 
         font=("Helvetica", 12, "bold"), bg="green", fg="white", width=20, height=2).pack(pady=10)
  
  btn_siguiente_turno_ref = Button(frame_control, text="Siguiente Turno (+1 Hora)", command=mover_trenes_ui, 
                                   width=20, height=2, state=tk.DISABLED)
  btn_siguiente_turno_ref.pack(pady=10)

  Button(frame_control, text="Guardar Estado", command=lambda: guardar_datos(obtener_estado_actual(), app_ventana), width=20).pack(pady=5)
  Button(frame_control, text="Cargar Estado", command=cargar_estado, width=20).pack(pady=5)
  
  Frame(frame_control, height=2, bg='gray').pack(fill='x', pady=10)

  Button(frame_control, text="Reiniciar Simulación", command=reiniciar_simulacion, 
         width=20).pack(pady=5)

  Button(frame_control, text="Eventos Adicionales", command=abrir_menu_eventos_adicionales, width=20).pack(pady=5)

  Button(frame_control, text="Renombrar Estaciones", command=abrir_ventana_renombrar_estaciones, width=20).pack(pady=5)
  Button(frame_control, text="Generar Población (Test)", command=generar_poblacion_ui, width=20).pack(pady=5) 
  
  Frame(frame_control, height=2, bg='gray').pack(fill='x', pady=10)

  Button(frame_control, text="Acerca de Estaciones", command=mostrar_info_estaciones, width=20).pack(pady=5)
  Button(frame_control, text="Acerca de Trenes", command=mostrar_info_trenes, width=20).pack(pady=5) 

  Button(frame_control, text="Salir", command=lambda: salir_app(app_ventana), width=20, bg='red', fg='white').pack(pady=20, side=tk.BOTTOM)
  
  app_ventana.mainloop()

if __name__ == "__main__":
    main()
