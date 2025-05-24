import tkinter as tk
from tkinter import ttk

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1000
FRAME_WIDTH = WINDOW_WIDTH // 4

#Ventana básica
ventana = tk.Tk()
ventana.title("Ventana básica INDIGO")
ventana.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

#Contenedor principal
paned = ttk.PanedWindow(ventana, orient=tk.HORIZONTAL)  
paned.pack(fill=tk.BOTH, expand=True)  

# Frame izquierdo (navbar)
left_frame = ttk.Frame(paned)
left_frame.configure(height=WINDOW_HEIGHT, width=FRAME_WIDTH)
left_frame['style'] = 'Background.TFrame'
paned.add(left_frame, weight=1)


# Logo y nombre del sistema
logo = tk.Label(left_frame, text="🔭", font=("Arial", 48))
logo.pack(pady=(30, 10))
system_name = tk.Label(left_frame, text="INDIGO\nObservatory", font=("Arial", 18, "bold"), justify="center")
system_name.pack(pady=(0, 30))

# Treeview de dispositivos
tree_label = ttk.Label(left_frame, text="Dispositivos conectados:", font=("Arial", 12, "bold"))
tree_label.pack(pady=(0, 5))
tree = ttk.Treeview(left_frame, selectmode="browse")
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Añadir dispositivos de ejemplo
cam1 = tree.insert("", "end", text="Cámara CCD", open=True)
tree.insert(cam1, "end", text="Temperatura", values=("12.3°C",))
tree.insert(cam1, "end", text="Estado", values=("Enfriando",))
tree.insert("", "end", text="Montura EQ6", values=("Conectada",))
tree.insert("", "end", text="Rueda de filtros", values=("Desconectada",))

# Botón de recarga
reload_button = ttk.Button(left_frame, text="🔄 Recargar lista")
reload_button.pack(pady=20)


# Frame derecho
right_frame = ttk.Frame(paned)
right_frame.configure(
    height=WINDOW_HEIGHT,
    width=3*FRAME_WIDTH,
)
right_frame['style'] = 'Background.TFrame' 
paned.add(right_frame, weight=3)

# Título del panel derecho
panel_title = tk.Label(right_frame, text="Panel de Control de Dispositivo", font=("Arial", 20, "bold"),)
panel_title.pack(pady=(30, 10))


# Terminal de mensajes
info_frame = tk.Frame(right_frame, bg="white", bd=2, relief="groove")
info_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=False)

info_label = tk.Label(info_frame, text="Seleccione un dispositivo para ver detalles.", font=("Arial", 14), bg="white")
info_label.pack(padx=20, pady=20)

# Botones de acciones de ejemplo
actions_frame = tk.Frame(right_frame)
actions_frame.pack(pady=30)

btn1 = ttk.Button(actions_frame, text="Conectar")
btn1.grid(row=0, column=0, padx=10)
btn2 = ttk.Button(actions_frame, text="Desconectar")
btn2.grid(row=0, column=1, padx=10)
btn3 = ttk.Button(actions_frame, text="Configurar")
btn3.grid(row=0, column=2, padx=10)

# Crear estilos personalizados para los frames
style = ttk.Style()
style.configure('Background.TFrame', background='lightgray')


ventana.mainloop()