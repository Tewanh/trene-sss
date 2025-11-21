# -- Imports -- #
import tkinter as tk
from tkinter import messagebox, Toplevel, Button
from datetime import datetime, timedelta
# Importamos la clase Estacion desde Models
from Models.Estaciones import Estacion 
# Importamos desde las carpetas logic y ui
from Logic.EstadoDeSimulacion import EstadoSimulacion
from Ui.eventos_ui import crear_ventana_eventos 

# Variables globales para simplificar el acceso en este ejemplo
app_ventana = None
estado_simulacion_instance = None
btn_avanzar_hora = None
btn_iniciar_sim = None
estaciones_list = [] # Lista global para almacenar las instancias de las estaciones

# --- Funciones de Lógica de Estado ---
# (obtener_estado_actual y aplicar_estado_cargado permanecen sin cambios)

def obtener_estado_actual():
    if estado_simulacion_instance:
        return {
            "tiempo_actual_simulado": estado_simulacion_instance.tiempo_actual_simulado.strftime("%Y-%m-%d %H:%M:%S"),
        }
    return {}

def aplicar_estado_cargado(datos_cargados):
    global estado_simulacion_instance
    if datos_cargados and estado_simulacion_instance:
        try:
            fecha_cargada = datetime.strptime(datos_cargados["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
            estado_simulacion_instance.tiempo_actual_simulado = fecha_cargada
            estado_simulacion_instance.actualizar_display()
            print(f"Estado aplicado. Nuevo tiempo: {fecha_cargada}")
        except Exception as e:
            messagebox.showerror("Error de datos", f"No se pudieron aplicar los datos: {e}")

# --- Funciones Auxiliares de UI ---

def mostrar_info_estaciones():
    """
    Recopila los datos de todas las estaciones y los muestra en un messagebox.
    """
    if not estaciones_list:
        messagebox.showinfo("Estaciones", "No hay datos de estaciones cargados.")
        return

    info_completa = "Datos de las Estaciones:\n\n"
    for estacion in estaciones_list:
        info_completa += estacion.obtener_resumen() + "\n"
    
    # Usamos un widget Toplevel con Text si el mensaje es demasiado largo para un messagebox estándar
    if len(info_completa) > 1000:
        ventana_info = Toplevel(app_ventana)
        ventana_info.title("Datos de Estaciones")
        text_widget = tk.Text(ventana_info, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, info_completa)
        text_widget.config(state=tk.DISABLED) # Hacer el texto de solo lectura
        text_widget.pack(expand=True, fill=tk.BOTH)
        Button(ventana_info, text="Cerrar", command=ventana_info.destroy).pack(pady=5)
    else:
        messagebox.showinfo("Estaciones", info_completa)


def mostrar_info_trenes():
    messagebox.showinfo("Acerca de Trenes", "Información detallada sobre los trenes y su funcionamiento.")

def mostrar_info_poblacion():
    messagebox.showinfo("Acerca de Población", "Información detallada sobre la población y su interacción con el sistema.")

def abrir_ventana_acerca_de():
    ventana_acerca = Toplevel(app_ventana)
    ventana_acerca.title("Acerca de...")
    ventana_acerca.geometry("300x180")
    tk.Label(ventana_acerca, text="¿Qué desea saber?").pack(pady=10)
    Button(ventana_acerca, text="Estaciones", command=mostrar_info_estaciones, width=15).pack(pady=5)
    Button(ventana_acerca, text="Trenes", command=mostrar_info_trenes, width=15).pack(pady=5)
    Button(ventana_acerca, text="Población", command=mostrar_info_poblacion, width=15).pack(pady=5)

def manejar_boton_eventos():
    crear_ventana_eventos(app_ventana, obtener_estado_actual, aplicar_estado_cargado)

def iniciar_simulacion():
    global btn_avanzar_hora, estado_simulacion_instance, btn_iniciar_sim
    if btn_avanzar_hora is None:
        estado_simulacion_instance.pack(pady=20) 
        btn_avanzar_hora = tk.Button(app_ventana, text="Siguiente Hora >>", 
                                     command=lambda: estado_simulacion_instance.avanzar_tiempo(timedelta(hours=1)))
        btn_avanzar_hora.pack(pady=10)
        btn_iniciar_sim.config(state=tk.DISABLED)

def inicializar_estaciones():
    """Crea las instancias de las estaciones al iniciar la app."""
    global estaciones_list
    # Usamos None para hora_inicio/final ya que la clase las espera
    estaciones_list.append(Estacion(nombre="Estación Central (Santiago)", region="Región Metropolitana", descripcion="Principal nodo ferroviario del país", conexiones=["Rancagua", "Chillán"], poblacion_total=8242459))
    estaciones_list.append(Estacion(nombre="Rancagua", region="Región de O’Higgins", descripcion="Distancia desde Santiago: ~87 km", conexiones=["Talca", "Estación Central"], poblacion_total=274407))
    estaciones_list.append(Estacion(nombre="Talca", region="Región del Maule", descripcion="Distancia desde Rancagua: ~200 km", conexiones=["Chillán", "Rancagua"], poblacion_total=242344))
    estaciones_list.append(Estacion(nombre="Chillán", region="Región de Ñuble", descripcion="Distancia desde Talca: ~180 km", conexiones=["Talca", "Estación Central"], poblacion_total=204091))


# -- MAIN -- #
def main():
    global app_ventana, estado_simulacion_instance, btn_iniciar_sim

    app_ventana = tk.Tk()
    app_ventana.title("Ferroviario")
    app_ventana.geometry("500x350") 

    # 1. Inicializar los datos de las estaciones
    inicializar_estaciones()

    # 2. Inicializar el estado de simulación
    estado_simulacion_instance = EstadoSimulacion(master=app_ventana)
    estado_simulacion_instance.pack_forget() 

    # 3. Crear los 3 botones principales

    btn_iniciar_sim = tk.Button(app_ventana, text="Iniciar Simulación", font=("Helvetica", 14, "bold"),
                                command=iniciar_simulacion)
    btn_iniciar_sim.pack(pady=20)

    btn_eventos = tk.Button(app_ventana, text="Eventos", command=manejar_boton_eventos)
    btn_eventos.pack(pady=10)

    btn_acerca_de = tk.Button(app_ventana, text="Acerca de", command=abrir_ventana_acerca_de)
    btn_acerca_de.pack(pady=10)
    
    app_ventana.mainloop()

if __name__ == "__main__":
    main()
