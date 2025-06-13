import tkinter as tk
ventana = tk.Tk()

# texto = tk.Text(ventana)

# scrollbar_v = tk.Scrollbar(ventana)
# scrollbar_v.pack(side="right", fill="y")

# scrollbar_v.config(command=texto.yview)
# texto.config(yscrollcommand=scrollbar_v.set)
# texto.pack(side="left", fill="both", expand=True)


scrollbar_h = tk.Scrollbar(ventana, orient=tk.HORIZONTAL)
scrollbar_h.pack(fill="x")

ventana.mainloop()