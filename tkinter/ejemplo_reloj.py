import time
import tkinter as tk

ventana = tk.Tk()

ventana.title("Mi primera ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+250") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightblue") # Cambiar el fondo
frame= tk.Frame(ventana)
frame.configure(width=300, height=200, bg="red", bd=5) #bd es borde
frame.pack()
etiqueta = tk.Label(frame, text="Hola soy un label")
etiqueta.config(fg="yellow", bg="black", font=("Arial", 14, "italic"))
etiqueta.pack()

func = True
id_fun = None

def actualizar_hora(): #Función para actualizar la hora actual
    global id_fun
    etiqueta.config(text=time.strftime("%H:%M:%S"))
    id_fun = frame.after(1000, actualizar_hora)

def toggle_hora():
    global func, id_fun
    if func:
        if id_fun is not None:
            frame.after_cancel(id_fun)
            id_fun=None

        boton.config(text="Iniciar reloj")
    
    else:
        actualizar_hora()
        boton.config(text="Detener reloj")
        
    func = not func

boton = tk.Button(frame, text="Detener reloj", command=toggle_hora)
boton.config(fg="white", bg="black", font=("Arial", 12))
boton.pack()
actualizar_hora()

ventana.mainloop()
