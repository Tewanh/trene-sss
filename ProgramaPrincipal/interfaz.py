# -- Imports -- #
import tkinter as tk
from tkinter import messagebox
# Importar desde la carpeta 'logic'
from Logic.Guardado import guardar_datos, cargar_datos, crear_menu_archivo
from Logic.EstadoDeSimulacion import EstadoSimulacion
from datetime import datetime, timedelta

app_ventana = None
estado_simulacion_instance = None


# --- Funciones de Lógica de Guardado ---

def obtener_estado_actual():
    """Recopila los datos del estado actual de la simulación para guardar."""
    if estado_simulacion_instance:
        return {
            "tiempo_actual_simulado": estado_simulacion_instance.tiempo_actual_simulado.strftime("%Y-%m-%d %H:%M:%S"),
            
        }
    return {}

def cargar_estado():
    """Carga los datos guardados y actualiza la UI."""
    global estado_simulacion_instance, app_ventana
    
    datos_cargados = cargar_datos(app_ventana)
    
    if datos_cargados and estado_simulacion_instance:
        try:
            fecha_cargada = datetime.strptime(datos_cargados["tiempo_actual_simulado"], "%Y-%m-%d %H:%M:%S")
            
            
            diferencia = fecha_cargada - estado_simulacion_instance.tiempo_actual_simulado
            estado_simulacion_instance.avanzar_tiempo(diferencia)
            
            estado_simulacion_instance.tiempo_actual_simulado = fecha_cargada
            estado_simulacion_instance.actualizar_display()

            print(f"Estado cargado. Nuevo tiempo: {fecha_cargada}")
            
        except Exception as e:
            messagebox.showerror("Error de datos", f"No se pudieron aplicar los datos cargados: {e}")

# --- Funciones Auxiliares de UI ---

def mostrar_info():
  """Muestra una ventana de informacion."""
  messagebox.showinfo("Informacion", "Es un ejemplo")

def salir_app(ventana):
  """pregunta al usuario si quiere salir y cierra la app"""
  if messagebox.askokcancel("Salir", "¿Estas seguro de querer salir?"):
    ventana.destroy()

def mostrar_error():
  """Muestra un mensaje de  error simulado."""
  messagebox.showerror("Error", "¡Ha ocurrido un error inesperado!") 


# -- MAIN -- #
def main():
  global app_ventana, estado_simulacion_instance

  app_ventana = tk.Tk()
  app_ventana.title("Ferroviario")
  app_ventana.geometry("500x400") #Ancho x Alto ajustado para mostrar la UI de tiempo

  estado_simulacion_instance = EstadoSimulacion(master=app_ventana, fecha_inicio_str="2023-10-27 08:30:00")
  estado_simulacion_instance.pack(pady=20)
  
  btn_avanzar = tk.Button(app_ventana, text="Avanzar 1 Hora (Demo)", command=lambda: estado_simulacion_instance.avanzar_tiempo(timedelta(hours=1)))
  btn_avanzar.pack(pady=10)

  barra_menu = tk.Menu(app_ventana)
  app_ventana.config(menu=barra_menu)
  
  menu_ayuda = tk.Menu(barra_menu, tearoff=0)
  
  barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
  crear_menu_archivo(app_ventana, barra_menu, obtener_estado_actual)
  menu_archivo_creado = barra_menu.winfo_children()[0] 
  menu_archivo_creado.add_command(label="Cargar", command=cargar_estado)

  menu_ayuda.add_command(label="Acerca de...", command=mostrar_info)
  
  menu_archivo_creado.add_command(label="Salir", command=lambda: salir_app(app_ventana))

  app_ventana.mainloop()

if __name__ == "__main__":
    main()
