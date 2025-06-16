from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.scrolledtext import ScrolledText

ventana = Tk()
#Sin scroll
texto = Text(ventana, width=40, height=10, wrap="word", bg="lightgray", padx=10, pady=10, font=("Helvetica", 12)) 
texto.tag_configure("resaltado", background="yellow", foreground="black")
# 1.0 se refiere a la primera línea, 2.0 la segunda línea...
texto.insert("1.0", "Editor de texto\n\n")
texto.insert("end", "Este es un texto resaltado", "resaltado")
contenido  = texto.get("1.0", "end")
print(contenido)
# texto.delete("2.0", "end")
texto.pack()

#Con scroll
texto_scroll=ScrolledText(ventana, width=40, height=10, wrap="word", bg="lightgray", padx=10, pady=10, font=("Helvetica", 12)) 
texto_scroll.pack(expand=True, fill="both") #Que se expanda todo el cuadro de texto (con fill=both es que no se expanda sólo el marco sino también el cuadro de texto)

#Botones edición
def copiar():
    texto.event_generate("<<Copy>>")
def cortar():
    texto.event_generate("<<Cut>>")
def pegar():
    texto.event_generate("<<Paste>>")    


boton_copiar = Button(ventana, text="Copiar", command=copiar)
boton_cortar = Button(ventana, text="Cortar", command=cortar)
boton_pegar = Button(ventana, text="Pegar", command=pegar)
boton_copiar.pack()
boton_cortar.pack()
boton_pegar.pack()

#editor
def abrir_archivo():
    archivo = askopenfilename()
    if archivo:
        texto_scroll.delete(1.0, "end")
        with open(archivo, "w") as file:
            texto_scroll.insert(1.0 ,file.read())

def guardar_archivo():
    archivo = asksaveasfilename()
    if archivo:
        with open(archivo, "w") as file:
            file.write(texto_scroll.get(1.0, "end"))

boton_abrir = Button(ventana, text="Abrir", command=abrir_archivo)
boton_abrir.pack(side="left")
boton_guardar = Button(ventana, text="Guardar", command=guardar_archivo)
boton_guardar.pack(side="left")
ventana.mainloop()