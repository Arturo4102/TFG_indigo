import tkinter as tk

ventana = tk.Tk()

texto= tk.StringVar(value="Hola, mundo!")
print(texto.get())
texto.set("Nuevo texto")
print(texto.get())

entrada = tk.Entry(ventana, textvariable=texto)
entrada.pack()

etiqueta = tk.Label(ventana)
etiqueta.pack()

def actualizar_etiqueta(*args):
    etiqueta.config(text=texto.get())
    
texto.trace("w", actualizar_etiqueta)

entero=tk.IntVar(value=42)

print(entero.get())
opcion1=tk.Radiobutton(ventana, text="Opción 1", variable=entero, value=1)
opcion1.pack()
opcion2=tk.Radiobutton(ventana, text="Opción 2", variable=entero, value=2)
opcion2.pack()

def actualizar(*args):
    print(entero.get())
entero.trace("w", actualizar)

# casilla = tk.Checkbutton(ventana, text="Aceptar", variable=entero,onvalue=1, offvalue=0)
# casilla.pack()

# def actualizar(*args):
#     print(entero.get())

# entero.trace("w", actualizar)

decimal = tk.DoubleVar(value=1.14)
control_deslizante = tk.Scale(ventana, variable=decimal, from_=0, to=10, resolution=0.01, orient=tk.HORIZONTAL)
control_deslizante.pack()


booleano = tk.BooleanVar(value=True)

casilla = tk.Checkbutton(ventana, text="Aceptar", variable = booleano)
casilla.pack()
def actualizar(*args):
    print(booleano.get())

booleano.trace("w", actualizar)
ventana.mainloop()

