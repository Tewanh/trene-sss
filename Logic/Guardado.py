import tkinter as tk
from tkinter import filedialog

class Guardado:

  def guardar_simulacion ():
   # 1. Abrir diálogo de guardado
    # asksaveasfilename devuelve la ruta completa del archivo
    ruta_archivo = filedialog.asksaveasfilename(
        defaultextension=".txt", # Extensión predeterminada
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    
    # Si el usuario cancela, ruta_archivo será una cadena vacía
    if not ruta_archivo:
        return

    # 2. Obtener el texto del widget de entrada
    contenido = texto_entrada.get("1.0", tk.END) # Para un widget Text

    # 3. Escribir el contenido en el archivo
    try:
        with open(ruta_archivo, 'w') as archivo:
            archivo.write(contenido)
        print(f"Archivo guardado en: {ruta_archivo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

# --- Widget de entrada de texto ---
# Se recomienda usar el widget Text para texto largo
texto_entrada = tk.Text(ventana, height=10, width=50)
texto_entrada.pack(pady=10)

# --- Botón para guardar ---
boton_guardar = tk.Button(ventana, text="Guardar", command=guardar_archivo)
boton_guardar.pack(pady=5)

ventana.mainloop()



  def cargar_simulacion ():

