from tkinter import *
from PIL import Image, ImageTk

ventana = Tk()
ventana.title("Images")
imagen = PhotoImage(file="logo.png")
# imagen = PhotoImage(file="imagen.gif")
label = Label(ventana, image = imagen)
# label.pack()
boton = Button(ventana, image = imagen)
# boton.pack()

imagen_pil = Image.open("tux.jpg")
imagen_redimensionada = imagen_pil.resize((100,100))
imagen_rotada = imagen_redimensionada.rotate(90)
imagen_tk = ImageTk.PhotoImage(imagen_rotada)

boton = Button(ventana, image = imagen_tk)
boton.pack()

ventana.mainloop()