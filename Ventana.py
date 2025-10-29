# -- Imports -- #
import tkinter as tk
from tkinter import messagebox

# -- MAIN -- #
def main():
  #1 Ventana principal
  ventana = tk.Tk()
  ventana.title("Ferroviario")
  ventana.geometry("400x300") #Ancho x Alto

  #3 Crear la barra de menu principal
  barra_menu = tk.Menu(ventana)
  ventana.config(menu=barra_menu)
  
  #4 Crear menus desplegables
  menu_archivo = tk.Menu(barra_menu)
  menu_ayuda = tk.Menu(barra_menu)
  
  #5 Agregar menus desplegables a la barra de menu
  barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
  barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
  
  #6 Agregar la "LOGICA" a los botones
  #Menu Archivo
  menu_archivo.add_command(label="Mostrar Error", command=lambda: mostrar_error(ventana))
  menu_archivo.add_command(label="Salir", command=lambda: salir_app(ventana))
  #Menu Ayuda
  menu_ayuda.add_command(label="Acerca de...", command=mostrar_info)
  
  #2 Iniciar bucle inicial
  ventana.mainloop()

  # LOGICA #
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
  

if _name_ = "_main_":
  main()


