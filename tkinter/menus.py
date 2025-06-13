from tkinter import *

ventana = Tk()

ventana.title("Mi ventana") # Título de la ventana creada 
ventana.geometry("600x600+450+250") # Tamaño estándar de mi ventana y posteriomente coordenadas donde sale
ventana.configure(bg="lightblue") # Cambiar el fondo

menuButton= Menubutton(ventana, text="Boton Menu")
menuButton.pack()

menu= Menu(menuButton)
def abrir_archivo():
    print("Archivo abierto")


menuButton.config(menu=menu)
menu.add_command(label="Abrir", command=abrir_archivo)
menu.add_command(label="Guardar")



barra_menu = Menu(ventana)
ventana.config(menu=barra_menu, pady=10)

archivo_menu = Menu(barra_menu)
barra_menu.add_cascade(label="Archivo Menu", menu=archivo_menu)
archivo_menu.add_command(label="Nuevo")
archivo_menu.add_command(label="Abrir")
archivo_menu.add_separator()
archivo_menu.add_command(label="Salir", command=ventana.destroy)
editar_menu = Menu(barra_menu)
barra_menu.add_cascade(label="Editar", menu=editar_menu)
editar_menu.add_command(label="Deshacer")
editar_menu.add_command(label="Rehacer")

#Menú que sale con el click
def mostrar_menu_contextual(event):
    menu_contextual.tk_popup(event.x_root, event.y_root)

menu_contextual = Menu(ventana, tearoff=0)
menu_contextual.add_command(label="Cortar")
menu_contextual.add_command(label="Copiar")
menu_contextual.add_command(label="Pegar")

entrada = Entry(ventana)
entrada.pack()

entrada.bind("<Button-3>", mostrar_menu_contextual)
ventana.mainloop()