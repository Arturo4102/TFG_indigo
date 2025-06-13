from tkinter import *

ventana = Tk()
ventana.title("Ventana Principal")
ventana.geometry("600x400")


# ventanaTopLevel = Toplevel(ventana)
# ventanaTopLevel.title("Ventana Top Level")
# ventanaTopLevel.geometry("300x200+50+50")
ids_ventana=[]

def abrir_ventana_toplevel():
    global ids_ventana    
    ventanaTopLevel = Toplevel(ventana)
    ids_ventana.append(ventanaTopLevel)
    ventanaTopLevel.title("Ventana Top Level")
    ventanaTopLevel.geometry("300x200+50+50")
    label = Label(ventanaTopLevel, text="Ventana Top Level")
    label.pack(pady=20)
    boton_cerrar.config(state='normal' if ids_ventana else 'disabled')

boton_abrir = Button(ventana, text="Abrir Ventana Top Level", command=abrir_ventana_toplevel)
boton_abrir.pack()

def cerrar_ventana_toplevel():    
    global ids_ventana
    ventana=ids_ventana.pop()
    ventana.destroy()
    boton_cerrar.config(state='normal' if ids_ventana else 'disabled')

boton_cerrar = Button(ventana, text="Cerrar Ventana Top Level", state="disabled",command=cerrar_ventana_toplevel)
boton_cerrar.pack()
ventana.mainloop()