import tkinter as tk

ventana = tk.Tk()

ventana.title("Mi primera ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+250") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightblue") # Cambiar el fondo


frame= tk.Frame(ventana)
frame.configure(width=300, height=200, bg="red", bd=5) #bd es borde
frame.pack()

frame2= tk.Frame(frame)
frame2.configure(width=100, height=50, bg="green", bd=5) #bd es borde
frame2.pack()

boton = tk.Button(frame, text="Hola")
boton.pack()


labelframe = tk.LabelFrame(ventana, text="Grupo de widgets", bg="yellow", padx=10, pady=10)
labelframe.configure(width=300,height=200)
labelframe.pack()

ventana.mainloop()
