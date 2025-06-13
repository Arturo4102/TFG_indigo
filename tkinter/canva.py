import tkinter as tk

ventana = tk.Tk()
canvas = tk.Canvas(ventana, width=500, height=300, bg='lightblue')

rectangulo = canvas.create_rectangle(50, 50, 150, 100, fill='green', outline='black', width=2, tags='rectangulo')
canvas.move(rectangulo,50, 100)
canvas.create_oval(200, 50, 300, 150, fill="blue", outline="black", width=5)
canvas.create_polygon(350, 50, 400, 100, 450, 250, 500, 150, fill="purple", outline="white", width=2)
canvas.create_line(10, 250, 250, 250, fill="orange", width=5, dash=(10, 2), capstyle='round')
canvas.create_text(150, 50, text='Aprendiendo Canvas', fill = 'orange', font=('Courier', 12, 'italic bold'), justify='center')
canvas.pack()
    
objeto_seleccionado = None

def iniciar_arrastre(event):
    global objeto_seleccionado
    objeto_seleccionado = canvas.find_closest(event.x, event.y)
    
def terminar_arrastre(event):
    global objeto_seleccionado
    if objeto_seleccionado:
        x, y = event.x, event.y
        canvas.move(objeto_seleccionado, x-canvas.coords(objeto_seleccionado)[0], y - canvas.coords(objeto_seleccionado)[1])
        objeto_seleccionado = None
        
rectangulo = canvas.create_rectangle(100, 100, 200, 200, fill="red", tags="rectangulo")

canvas.tag_bind('rectangulo', '<ButtonPress-1>', iniciar_arrastre)
canvas.tag_bind('rectangulo', '<ButtonRelease-1>', terminar_arrastre)

ventana.mainloop()