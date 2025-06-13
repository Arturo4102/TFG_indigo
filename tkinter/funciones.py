import time
import tkinter as tk
from turtle import onclick
def on_click(event):
    print("Botón presionado")

def on_key_press(event):
    print(f"Tecla {event.char} presionada")

#Nos traemos el texto que hay en event.widget
def on_click_widget(event):
    print(f"{event.widget['text']} presionado")
    
ventana = tk.Tk()

ventana.title("Mi ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+350") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightyellow") # Cambiar el fondo
frame= tk.Frame(ventana)
frame.configure(width=300, height=200, bg="red", bd=5) #bd es borde
frame.pack()

boton = tk.Button(frame, text="Haz click aquí")
boton.config(fg="white", bg="black", font=("Arial", 12))
boton.pack()

botones = [tk.Button(ventana,text=f"Botón {i}") for i in range(3)]
boton.config(fg="black", bg="orange", font=("Arial", 12))

for button in botones:
    button.pack()
    button.bind("<Button-1>", on_click_widget)
#~~~~~~~~~~~~ FUNCIONES ~~~~~~~~~~~~~~~~~~~
boton.bind("<Button-3>", on_click) #Button-1 (izq), Button-2 (rueda), Button-3(derecha)
ventana.bind("<KeyPress>", on_key_press)

ventana.mainloop()