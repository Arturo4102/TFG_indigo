import tkinter as tk
from tkinter import filedialog

ventana = tk.Tk()
# ventana.withdraw() #Oculta la ventana principal
# file_path = tk.filedialog.askopenfilename()

# print(file_path)

# file_obj = filedialog.askopenfile(mode='r')
# if file_obj:
#     print(file_obj.read())
#     file_obj.close()

# MINUTO 6:19

def abrir_archivo():
    #Items que te salen abajo a la derecha para seleccionar qué tipos de archivos seleccionar
    file_path = filedialog.askopenfilename(filetypes=[('Archivos de texto (aquí es)', '*txt'), ('Todos los archivos de Python', '*.py*'), ('Todos los archivos', '*.*')]) 
    if file_path:
        with open(file_path, 'r') as file_obj:
            contenido = file_obj.read()
            text_widget.delete(1.0, tk.END) #Borramos todo
            text_widget.insert(tk.INSERT, contenido)

ventana.title('Visor de archivos de texto')

text_widget = tk.Text(ventana, wrap='word')
text_widget.pack(expand=True, fill='both')

abrir_button = tk.Button(ventana, text="Abrir archivo", command=abrir_archivo)
abrir_button.pack()


ventana.mainloop()