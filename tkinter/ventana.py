import tkinter as tk
from tkinter import PhotoImage
ventana = tk.Tk()
ventana.title("Mi primera ventana") # Título de la ventana creada 
ventana.geometry("600x800+300+300") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.minsize(400, 400) # Tamaño mínimo de la ventana
ventana.maxsize(800, 1200) # Tamaño máximo de mi ventana
# ventana.iconbitmap('icon.ico') # Poner un icono en la ventana
icono = PhotoImage(file="icons/logo.png")
ventana.iconphoto(True,icono)

# ventana.iconbitmap()
ventana.configure(bg="lightblue") # Cambiar el fondo
ventana.resizable(False, True) # Redimensionar la pestaña o no



ventana.mainloop()
