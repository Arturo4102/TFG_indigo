import tkinter as tk

ventana = tk.Tk()

ventana.title("Mi ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+250") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightblue") # Cambiar el fondo
frame= tk.Frame(ventana)
frame.configure(width=300, height=200, bg="red", bd=5) #bd es borde
frame.pack()

label1 = tk.Label(frame, text="Celda 1,1", bg="blue", bd=5)
label2 = tk.Label(frame, text="Celda 1,2", bg="blue", bd=5)
label3 = tk.Label(frame, text="Celda 2,1", bg="blue", bd=5)
label4 = tk.Label(frame, text="Celda 2,2", bg="blue", bd=5)
label1.grid(row=0, column=0, padx=10, pady=10)
label2.grid(row=0, column=1, padx=10, pady=10)
label3.grid(row=1, column=0, padx=10, pady=10)
label4.grid(row=1, column=1, padx=10, pady=10)


#Con pack los pone uno debajo del otro (tanto vertical como horizontalmente)

frame2= tk.Frame(ventana)
frame2.configure(width=300, height=200, bg="green", bd=5) 
frame2.pack(pady=10)
boton1 = tk.Button(frame2, text="Botón 1")
boton2 = tk.Button(frame2, text="Botón 2")
boton3 = tk.Button(frame2, text="Botón 3")
boton1.pack(side="left", padx=5)
boton2.pack(side="left", padx=5)
boton3.pack(side="left", padx=5)


frame3= tk.Frame(ventana)
frame3.configure(width=300, height=200, bg="orange", bd=5) 
frame3.pack(pady=10)
boton1 = tk.Button(frame3, text="Botón 1")
boton2 = tk.Button(frame3, text="Botón 2")
boton3 = tk.Button(frame3, text="Botón 3")
boton1.pack(side="right", padx=5)
boton2.pack(side="right", padx=5)
boton3.pack(side="right", padx=5)

# Con place, se coloca en las coordenadas absolutas del contenedor
frame4= tk.Frame(ventana)
frame4.configure(width=200, height=200, bg="brown", bd=5) 
frame4.pack()

label1 = tk.Label(frame4, text="Label 1", bg="gray", bd=5)
label2 = tk.Label(frame4, text="Label 2", bg="gray", bd=5)

label1.place(relx=0.25,rely=0.25)
label2.place(relx=0.5,rely=0.5)


ventana.mainloop()