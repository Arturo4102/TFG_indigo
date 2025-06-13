import tkinter as tk

ventana = tk.Tk()
ventana.title("Mi primera ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+250") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightblue") # Cambiar el fondo

frame=tk.Frame(ventana)
frame.configure(width=400, height=400,bg='lightgreen',bd=5,padx=10,pady=10)
frame.pack()
etiqueta = tk.Label(frame, text="Hola soy un label")
etiqueta.config(text="Nuevo texto", fg="yellow", bg="black", font=("Arial", 14, "italic"))
etiqueta.pack()

ventana.mainloop()
