from tkinter import *
from tkinter import ttk
ventana = Tk()
ventana.title("Ejemplo lista")
#Widget Listbox
listbox = Listbox(ventana, width=30, height=10, font=("Arial", 12), fg="white", bg="black",
                    # selectmode=MULTIPLE                  
                  )


listbox.insert(END, "Elemento 1")
listbox.insert(2, "Elemento 2")
listbox.insert(1, "Elemento 3")
listbox.insert(END, "Elemento 4")
# listbox.delete(2)

def on_seleccionar(event):
    indice = listbox.curselection()
    elemento=listbox.get(indice)
    print(f"Seleccionado: {elemento}")

def on_clic(event):
    print(f"Hecho un clic")

def on_double_clic(event):
    print(f"Hecho un doble clic")

# listbox.bind("<<ListboxSelect>>", on_seleccionar)
listbox.bind("<Button-1>", on_clic)
listbox.bind("<Double-Button-1>", on_double_clic)

listbox.pack()


#Widget Combobox

combobox = ttk.Combobox(ventana,width=30, height=10, font=("Arial", 12), foreground="blue", background="white",)
combobox.pack()

elementos = ["Elemento 1","Elemento 2","Elemento 3","Elemento 4"]
combobox["values"] = elementos
elementos[1] = "Elemento modificado"
elementos.remove("Elemento 1")
combobox["values"] = elementos #Si se borra, modifica, añade... hay que actualizar el combobox

def on_seleccionar(event):
    valor = combobox.get()
    print(f"Seleccionado: {valor}")

combobox.bind("<<ComboboxSelected>>", on_seleccionar)

def on_clic_com(event):
    print(f"Hecho un clic en combobox")

def on_double_clic_com(event):
    print(f"Hecho un doble clic en combobox")

combobox.bind("<Button-1>", on_clic_com)
combobox.bind("<Double-Button-1>", on_double_clic_com)


ventana.mainloop()