import tkinter as tk

ventana = tk.Tk()

ventana.title("Mi ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+250") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightblue") # Cambiar el fondo
frame= tk.Frame(ventana)
frame.configure(width=300, height=200, bg="red", bd=5) #bd es borde
frame.pack()

variable_control = tk.BooleanVar()

def cambiar_color():
    if variable_control.get():
        ventana.config(bg="lightyellow")
    else:
        ventana.config(bg="lightgreen")


def habilitar():
    if variable_control.get():
        boton.config(state="normal")
    else:
        boton.config(state="disabled")
        

# opcion1 = tk.Radiobutton(frame, text="Opción 1", variable=variable_control, value=False, command=cambiar_color)
opcion2 = tk.Checkbutton(frame, text="Opción 2", variable=variable_control,command=habilitar)
boton=tk.Button(frame, text="Botón", state="disabled")
boton.pack()
# opcion1.pack()
opcion2.pack()

def mostrar_seleccion():
    print(f"Opción seleccionada: {variable_control.get()}")


# boton = tk.Button(frame, text="Mostrar selección", command=mostrar_seleccion)
# boton.pack()
ventana.mainloop()