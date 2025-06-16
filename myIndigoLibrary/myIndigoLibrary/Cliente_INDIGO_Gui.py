import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
import os
import sys

try:
    from Cliente_INDIGO import INDIGOServer, INDIGODevice, INDIGOProperty, INDIGOElement
except ImportError:
    print("Error: No se pudo importar Cliente_INDIGO.py")
    sys.exit(1)
    # ~~~~~~~~~~~ Para la documentación sacar env_indigo de la carpeta ~~~~~~~~~~~ 
    # Esta parte se hace para la documentación con Sphinx, para que no dé errores, de normal comentar
    # if __name__ == "__main__":
    #     sys.exit(1)
    # else:
    #     # Para Sphinx, crear clases dummy
    #     class INDIGOServer: pass
    #     class INDIGODevice: pass  
    #     class INDIGOProperty: pass
    #     class INDIGOElement: pass
    


class INDIGOControlPanel:
    """Interfaz gráfica completa para el control de dispositivos INDIGO.
    
    Esta clase proporciona una interfaz gráfica de usuario completa para interactuar
    con servidores INDIGO, permitiendo la visualización y control de dispositivos
    astronómicos conectados al servidor.
    
    Attributes:
        root (tk.Tk): Ventana principal de la aplicación
        server (INDIGOServer): Instancia del servidor INDIGO conectado
        connected (bool): Estado de conexión al servidor
        auto_refresh (tk.BooleanVar): Variable para control de actualización automática
        refresh_interval (tk.IntVar): Intervalo de actualización en segundos
        notebook (ttk.Notebook): Widget de pestañas principal
        devices_tree (ttk.Treeview): Árbol de dispositivos
        properties_tree (ttk.Treeview): Árbol de propeidades
        control_widgets (dict): Diccionario de widgets de control dinámicos
        logs_text (scrolledtext.ScrolledText): Área de texto para logs
    """
    
    # Constantes para los estilos
    HEADER_STYLE = 'Header.TLabel'
    STATUS_STYLE = 'Status.TLabel'
    CONNECTED_STYLE = 'Connected.TLabel'
        
    def __init__(self):
        """Constructor de la clase INDIGOControlPanel.
        
        Inicializa la ventana principal, configura los estilos y crea
        todos los widgets de la interfaz gráfica.
        """
        self.root = tk.Tk()
        self.root.title("PYNDIGO- TFG Arturo")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Variables de estado
        self.server = None
        self.connected = False
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = tk.IntVar(value=2)
        
        # Configuramos el estilo
        self.setup_styles()
        
        # Creamos la interfaz
        self.create_widgets()
        
        # Iniciamos la actualización automática
        self.auto_update()
        
    def setup_styles(self):
        """Configura los estilos visuales de la interfaz.
        
        Define los estilos personalizados para los diferentes elementos
        de la interfaz, incluyendo colores, fuentes y tamaños.
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuramos los colores personalizados
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#ecf0f1')
        style.configure(self.HEADER_STYLE, font=('Arial', 12, 'bold'), foreground='#3498db')
        style.configure(self.STATUS_STYLE, font=('Arial', 10), foreground='#e74c3c')
        style.configure(self.CONNECTED_STYLE, font=('Arial', 10), foreground='#27ae60')
        
    def create_widgets(self):
        """Crea todos los widgets principales de la interfaz.
        
        Construye la estructura completa de la interfaz gráfica,
        incluyendo el frame principal, título, área de la conexión
        y el notebook en todas las pestañas a realizar.
        """
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="INDIGO Control Panel", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame de la conexión
        self.create_connection_frame(main_frame)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Pestañas de la interfaz
        self.create_devices_tab()
        self.create_properties_tab()
        self.create_control_tab()
        self.create_images_tab()
        self.create_logs_tab()
        self.create_settings_tab()
        
    def create_connection_frame(self, parent):
        """Crea el frame de conexión al servidor INDIGO.
        
        Construye la interfaz para configurar y establecer la conexión
        con el servidor INDIGO, incluyendo campos como el host, puerto
        y el nombre del cliente.

        Args:
            parent (ttk.Widget): Widget padre donde se creará el frame
        """
        conn_frame = ttk.LabelFrame(parent, text="Conexión al Servidor INDIGO", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para campos de entrada
        input_frame = ttk.Frame(conn_frame)
        input_frame.pack(fill=tk.X)
        
        # Campos de conexión
        ttk.Label(input_frame, text="Servidor:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_entry = ttk.Entry(input_frame, width=20)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(input_frame, text="Puerto:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.port_entry = ttk.Entry(input_frame, width=10)
        self.port_entry.insert(0, "7624")
        self.port_entry.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.name_entry = ttk.Entry(input_frame, width=15)
        self.name_entry.insert(0, "PYNDIGO_GUI")
        self.name_entry.grid(row=0, column=5, padx=(0, 20))
        
        # Botones de conexión
        self.connect_btn = ttk.Button(input_frame, text="Conectar", command=self.connect_server)
        self.connect_btn.grid(row=0, column=6, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(input_frame, text="Desconectar", command=self.disconnect_server, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=7)
        
        # Estado de conexión
        self.status_label = ttk.Label(conn_frame, text="[X] Desconectado", style=self.STATUS_STYLE)
        self.status_label.pack(pady=(10, 0))
        
    def create_devices_tab(self):
        """Crea la pestaña de visualización de dispositivos.
        
        Construye la interfaz para mostrar la lista de dispositivos
        conectados al servidor INDIGO, incluyendo información sobre 
        estos, como su estado, propiedades y última actualización.
        """
        devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(devices_frame, text="Dispositivos")
        
        # Frame superior con controles
        control_frame = ttk.Frame(devices_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="Actualizar", command=self.refresh_devices).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Exportar Lista", command=self.export_devices).pack(side=tk.LEFT)
        
        # Lista de dispositivos
        list_frame = ttk.Frame(devices_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview para dispositivos
        columns = ('Dispositivo', 'Tipo', 'Estado', 'Propiedades', 'Última Actualización')
        self.devices_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
         # Primera columna alineada a la izquierda, el resto va al centro
        self.devices_tree.heading('Dispositivo', text='Dispositivo', anchor="w")
        self.devices_tree.column('Dispositivo', width=200, anchor="w")
        
        for col in columns[1:]:  # Resto de columnas
            self.devices_tree.heading(col, text=col, anchor="center")
            self.devices_tree.column(col, width=200, anchor="center")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.devices_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.devices_tree.xview)
        self.devices_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack treeview y scrollbars
        self.devices_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para selección
        self.devices_tree.bind('<<TreeviewSelect>>', self.on_device_select)
        
    def create_properties_tab(self):
        """Crea la pestaña de visualización de propiedades.
        
        Construye la interfaz para mostrar las propiedades de los
        dispositivos seleccionados, incluyendo los detalles de cada
        propiedad y sus respectivos elementos.
        """
        props_frame = ttk.Frame(self.notebook)
        self.notebook.add(props_frame, text="Propiedades")
        
        # Frame superior con selector de dispositivo
        top_frame = ttk.Frame(props_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="Dispositivo seleccionado:", style=self.HEADER_STYLE).pack(side=tk.LEFT)
        # Combobox para seleccionar dispositivo
        self.device_selector_combo = ttk.Combobox(top_frame, width=30, state="readonly")
        self.device_selector_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.device_selector_combo.bind('<<ComboboxSelected>>', self.on_device_selector_change)
        
        # Frame principal con dos paneles
        main_props_frame = ttk.Frame(props_frame)
        main_props_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Panel izquierdo - Lista de propiedades
        left_frame = ttk.LabelFrame(main_props_frame, text="Lista de Propiedades", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview para propiedades
        prop_columns = ('Propiedad', 'Tipo', 'Estado', 'Permisos', 'Elementos')
        self.properties_tree = ttk.Treeview(left_frame, columns=prop_columns, show='headings', height=20)
        
        # Primera columna alineada a la izquierda, resto al centro
        self.properties_tree.heading('Propiedad', text='Propiedad', anchor="w")
        self.properties_tree.column('Propiedad', width=120, anchor="w")
        
        for col in prop_columns[1:]:  # Resto de columnas
            self.properties_tree.heading(col, text=col, anchor="center")
            self.properties_tree.column(col, width=120, anchor="center")
        
        prop_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.properties_tree.yview)
        self.properties_tree.configure(yscrollcommand=prop_scroll.set)
        
        self.properties_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prop_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Panel derecho - Detalles de la propiedad
        right_frame = ttk.LabelFrame(main_props_frame, text="Detalles de la Propiedad", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.property_details = scrolledtext.ScrolledText(right_frame, height=20, width=40)
        self.property_details.pack(fill=tk.BOTH, expand=True)
        
        # Bind para selección de propiedades
        self.properties_tree.bind('<<TreeviewSelect>>', self.on_property_select)
        
    def create_control_tab(self):
        """Crea la pestaña de control de dispositivos.
        
        Construye la interfaz para controlar las propiedades de los
        dispositivos, generando controles dinámicos según el tipo
        de propiedad seleccionada.
        """
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control")
        
        # Frame de selección
        select_frame = ttk.LabelFrame(control_frame, text="Selección de Propiedad", padding=10)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Comboboxes para selección
        ttk.Label(select_frame, text="Dispositivo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.device_combo = ttk.Combobox(select_frame, width=30, state="readonly")
        self.device_combo.grid(row=0, column=1, padx=(0, 20))
        self.device_combo.bind('<<ComboboxSelected>>', self.on_device_combo_change)
        
        ttk.Label(select_frame, text="Propiedad:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.property_combo = ttk.Combobox(select_frame, width=30, state="readonly")
        self.property_combo.grid(row=0, column=3, padx=(0, 20))
        self.property_combo.bind('<<ComboboxSelected>>', self.on_property_combo_change)
        
        # Frame de control dinámico
        self.control_content_frame = ttk.LabelFrame(control_frame, text="Controles", padding=10)
        self.control_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Label de instrucciones
        self.control_instructions = ttk.Label(self.control_content_frame, 
        text="Selecciona un dispositivo y propiedad para mostrar los controles")
        self.control_instructions.pack(pady=50)    
    
    def create_images_tab(self):
        """Crea la pestaña de gestión de imágenes.
        
        Construye la interfaz para gestionar archivos imágenes (archivos BLOB),
        incluyendo controles para habilitar sus propiedades,
        descargar imágenes y visualizar los archivos descargados.
        """
        images_frame = ttk.Frame(self.notebook)
        self.notebook.add(images_frame, text="Imágenes")
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(images_frame, text="Controles BLOB", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Estado del modo BLOB
        blob_status_frame = ttk.Frame(controls_frame)
        blob_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Añadimos información de estado
        self.blob_status_label = ttk.Label(controls_frame, text="")
        self.blob_status_label.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(blob_status_frame, text="Modo BLOB actual en el servidor:", style=self.HEADER_STYLE).pack(side=tk.LEFT)
        self.blob_mode_label = ttk.Label(blob_status_frame, text="NEVER")
        self.blob_mode_label.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(blob_status_frame, text="Cambiar Modo", command=self.toggle_blob_mode).pack(side=tk.RIGHT)
        
        # Selección de dispositivo/propiedad BLOB
        blob_select_frame = ttk.Frame(controls_frame)
        blob_select_frame.pack(fill=tk.X)
        
        ttk.Label(blob_select_frame, text="Dispositivo BLOB:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.blob_device_combo = ttk.Combobox(blob_select_frame, width=25, state="readonly")
        self.blob_device_combo.grid(row=0, column=1, padx=(0, 20))

        self.blob_device_combo.bind('<<ComboboxSelected>>', self.update_blob_properties)
    
        ttk.Label(blob_select_frame, text="Propiedad BLOB:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.blob_property_combo = ttk.Combobox(blob_select_frame, width=25, state="readonly")
        self.blob_property_combo.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Button(blob_select_frame, text="Habilitar BLOB en el dispositivo", command=self.enable_blob_property).grid(row=0, column=4)
        
        # Lista de imágenes descargadas
        images_list_frame = ttk.LabelFrame(images_frame, text="Imágenes Descargadas", padding=10)
        images_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Frame con lista y botones
        list_and_buttons = ttk.Frame(images_list_frame)
        list_and_buttons.pack(fill=tk.BOTH, expand=True)
        
        # Lista de archivos
        self.images_listbox = tk.Listbox(list_and_buttons, height=15)
        self.images_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        images_scroll = ttk.Scrollbar(list_and_buttons, orient=tk.VERTICAL, command=self.images_listbox.yview)
        self.images_listbox.configure(yscrollcommand=images_scroll.set)
        images_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de gestión de imágenes
        buttons_frame = ttk.Frame(images_list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Actualizar Lista", command=self.refresh_images_list).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Ver Imagen", command=self.view_selected_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Abrir Carpeta", command=self.open_images_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Eliminar", command=self.delete_selected_image).pack(side=tk.LEFT)
        
        # Actualizamos la lista inicial 
        # (de forma automática aunque si pulsamos Actualizar Lista se hace de forma manual)
        self.refresh_images_list()
            
    def create_logs_tab(self):
        """Crea la pestaña de logs y mensajes del sistema.
        
        Construye la interfaz para visualizar los logs de la aplicación,
        incluyendo mensajes de información, las advertencias y los errores,
        incluye como opciones limpiar y guardar los logs visualizados.
        """
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Frame de controles
        controls_frame = ttk.Frame(logs_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Limpiar Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Guardar Logs", command=self.save_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        # Checkbox para auto-scroll
        self.auto_scroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls_frame, text="Auto-scroll", variable=self.auto_scroll).pack(side=tk.LEFT, padx=(20, 0))
        
        # Área de logs
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=25, font=('Consolas', 10))
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configuramos colores de los tags
        self.logs_text.tag_configure("INFO", foreground="blue")
        self.logs_text.tag_configure("WARNING", foreground="orange")
        self.logs_text.tag_configure("ERROR", foreground="red")
        self.logs_text.tag_configure("SUCCESS", foreground="green")
        
    def create_settings_tab(self):
        """Crea la pestaña de configuración de la aplicación.
        
        Construye la interfaz para configurar opciones de la aplicación,
        incluyendo actualización automática, información del sistema
        y acciones de mantenimiento.
        """
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Configuración")
        
        # Frame de actualización automática
        auto_frame = ttk.LabelFrame(settings_frame, text="Actualización Automática", padding=10)
        auto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(auto_frame, text="Habilitar actualización automática", 
                       variable=self.auto_refresh).pack(anchor=tk.W)
        
        interval_frame = ttk.Frame(auto_frame)
        interval_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(interval_frame, text="Intervalo (segundos):").pack(side=tk.LEFT)
        ttk.Scale(interval_frame, from_=1, to=10, variable=self.refresh_interval, 
                 orient=tk.HORIZONTAL, length=200).pack(side=tk.LEFT, padx=(10, 0))
        
        interval_label = ttk.Label(interval_frame, textvariable=self.refresh_interval)
        interval_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame de información del sistema
        info_frame = ttk.LabelFrame(settings_frame, text="Información del Sistema", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        info_text = f"""
        INDIGO Control Panel
        Proyecto TFG - Arturo
        Python {sys.version.split()[0]}
        Directorio de trabajo: {os.getcwd()}
        Carpeta de imágenes: {os.path.join(os.getcwd(), 'images')}
                """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Frame de acciones
        actions_frame = ttk.LabelFrame(settings_frame, text="Acciones", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(actions_frame, text="Crear Carpeta de Imágenes", 
                  command=self.create_images_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Reiniciar Interfaz", 
                  command=self.restart_interface).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Salir", 
                  command=self.quit_application).pack(side=tk.LEFT)
        
    def log_message(self, message: str, level: str = "INFO"):
        """Añade un mensaje al log con timestamp y formato.

        Args:
            message (str): Mensaje a registrar en el log
            level (str): Nivel del mensaje (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.logs_text.insert(tk.END, formatted_message, level)
        
        if self.auto_scroll.get():
            self.logs_text.see(tk.END)
        
    def connect_server(self):
        """Establece la conexión con el servidor INDIGO.
        
        Obtiene los parámetros de conexión de la interfaz, crea una
        instancia del servidor INDIGO y establece la conexión.
        Actualiza el estado de la interfaz según el resultado.
        """
        try:
            host = self.host_entry.get().strip()
            port = int(self.port_entry.get().strip())
            name = self.name_entry.get().strip()
            
            if not host or not name:
                messagebox.showerror("Error", "Host y nombre son obligatorios")
                return
            
            self.log_message(f"Intentando conectar a {host}:{port}...")
            
            # Creamos el servidor y nos conectamos a él
            self.server = INDIGOServer(name, host, port)
            self.server.connect()
            
            # Actualizamos la UI
            self.connected = True
            self.status_label.config(text=f"[OK] Conectado a {host}:{port}", style=self.CONNECTED_STYLE)
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            
            self.log_message(f"Conectado exitosamente a {host}:{port}", "SUCCESS")
            
            # Esperamos un poco para que lleguen los nuevos datos de los dispositivos
            self.root.after(2000, self.refresh_all_data)
            self.root.after(2500, self.auto_register_blob_listeners)
        except Exception as e:
            self.log_message(f"Error de conexión: {str(e)}", "ERROR")
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor:\n{str(e)}")
        
    def disconnect_server(self):
        """Desconecta del servidor INDIGO.
        
        Cierra la conexión con el servidor, actualiza el estado
        de la interfaz y limpia todos los datos mostrados.
        """
        try:
            if self.server:
                self.server.disconnect()
                self.server = None
            
            self.connected = False
            self.status_label.config(text="[X] Desconectado", style=self.STATUS_STYLE)
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.DISABLED)
            
            # Limpiamos todos los datos
            self.clear_all_data()
            
            self.log_message("Desconectado del servidor", "INFO")
            
        except Exception as e:
            self.log_message(f"Error al desconectar: {str(e)}", "ERROR")
        
    def refresh_all_data(self):
        """Actualiza todos los datos de la interfaz.
        
        Refresca la información de dispositivos, propiedades,
        combos de selección y estado del modo BLOB.
        """
        if not self.connected or not self.server:
            return
        
        try:
            self.refresh_devices()
            self.refresh_combos()
            self.update_blob_mode_display()
            self.refresh_blob_combos()
            self.update_blob_properties()
            # Suscripción de los listeners para actualización en tiempo real
            if hasattr(self, 'server') and self.server:
                for device_name, device in self.server.get_devices().items():
                    for prop_name in device.get_properties().keys():
                        # Se evita registrar el mismo listener varias veces
                        self.server.add_device_property_listener(device_name, prop_name, self.on_property_update)
            # Registro automático de los listeners de tipo BLOB
            self.auto_register_blob_listeners()
        except Exception as e:
            self.log_message(f"Error actualizando datos: {str(e)}", "ERROR")
                    
    def refresh_devices(self):
        """Actualiza la lista de dispositivos en la pestaña correspondiente.
        
        Obtiene la lista de dispositivos del servidor y actualiza
        el TreeView con información sobre cada dispositivo.
        """
        if not self.connected or not self.server:
            return
        
        # Limpiamos la lista actual
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)
        
        # Añadimos los dispositivos
        devices = self.server.get_devices()
        for device_name, device in devices.items():
            properties_count = len(device.get_properties())
            last_update = "N/A"
            
            # Buscamos la última actualización
            latest_time = 0
            for prop in device.get_properties().values():
                if prop.last_update > latest_time:
                    latest_time = prop.last_update
            
            if latest_time > 0:
                last_update = datetime.fromtimestamp(latest_time).strftime("%H:%M:%S")
            
            self.devices_tree.insert('', tk.END, values=(
                device_name,
                "Dispositivo INDIGO",
                "Conectado" if properties_count > 0 else "Sin propiedades",
                properties_count,
                last_update
            ))
        
    def refresh_combos(self):
        """Actualiza los comboboxes de selección de dispositivos.
        
        Obtiene la lista de dispositivos disponibles y actualiza
        todos los comboboxes que permiten seleccionar estos dispositivos.
        """
        if not self.connected or not self.server:
            return
        
        devices = list(self.server.get_devices().keys())
        self.device_combo['values'] = devices
        self.device_selector_combo['values'] = devices
        
    def refresh_blob_combos(self):
        """Actualiza los comboboxes específicos para propiedades de tipo BLOB.
        
        Actualiza los comboboxes utilizados en la pestaña de imágenes
        para seleccionar dispositivos con propiedades de tipo BLOB.
        """
        if not self.connected or not self.server:
            return
        
        devices = list(self.server.get_devices().keys())
        self.blob_device_combo['values'] = devices
        
    def on_device_select(self, event):
        """Maneja la selección de un dispositivo en la lista.

        Args:
            event (tk.Event): Evento de selección del TreeView
        """
        selection = self.devices_tree.selection()
        if not selection:
            return
        
        item = self.devices_tree.item(selection[0])
        device_name = item['values'][0]
        
        # Actualizamos el selector de dispositivos en la pestaña de propiedades
        self.device_selector_combo.set(device_name)
        self.refresh_properties(device_name)
        
    def on_device_selector_change(self, event):
        """Maneja el cambio en el selector de dispositivos.

        Args:
            event (tk.Event): Evento de cambio en el combobox
        """
        device_name = self.device_selector_combo.get()
        if device_name:
            self.refresh_properties(device_name)
        
    def refresh_properties(self, device_name: str):
        """Actualiza la lista de propiedades para un dispositivo específico.

        Args:
            device_name (str): Nombre del dispositivo cuyas propiedades se van a mostrar
        """
        if not hasattr(self, 'properties_tree'):
            return
        selected = self.properties_tree.selection()
        self.properties_tree.delete(*self.properties_tree.get_children())
        device = self.server.get_device_by_name(device_name) if self.server else None
        if device:
            for prop in device.get_properties().values():
                self.properties_tree.insert(
                    "", "end", values=(
                        prop.get_name(),
                        prop.get_type(),
                        prop.get_from_attributes('state') or "N/A",
                        prop.get_from_attributes('perm') or "N/A",
                        len(prop.get_elements()),
                    )
                )
        # Restauramos la selección
        if selected:
            self.properties_tree.selection_set(selected)
        
    def on_property_select(self, event):
        """Maneja la selección de una propiedad en la lista.

        Args:
            event (tk.Event): Evento de selección del TreeView
        """
        selection = self.properties_tree.selection()
        if not selection:
            return
        
        item = self.properties_tree.item(selection[0])
        prop_name = item['values'][0]
        device_name = self.device_selector_combo.get()
        
        if not device_name:
            return
        
        self.show_property_details(device_name, prop_name)
        
    def on_property_update(self, prop):
        """Listener para cambios en propiedades INDIGO."""
        # Se refresca solo la propiedad seleccionada en la pestaña de propiedades
        try:
            selected_device = self.device_selector_combo.get() if hasattr(self, 'device_selector_combo') else None
            selected_prop = None
            if hasattr(self, 'properties_tree') and self.properties_tree.selection():
                item = self.properties_tree.item(self.properties_tree.selection()[0])
                selected_prop = item['values'][0]
            if selected_device and selected_prop and prop.get_name() == selected_prop and prop.get_device().get_name() == selected_device:
                self.root.after(0, lambda: self.show_property_details(selected_device, selected_prop))
            # Se refresca la lista de propiedades si es necesario
            if selected_device:
                self.root.after(0, lambda: self.refresh_properties(selected_device))
            # Se refresca controles si la propiedad está seleccionada en la pestaña de control
            if hasattr(self, 'device_combo') and hasattr(self, 'property_combo'):
                device_name = self.device_combo.get()
                prop_name = self.property_combo.get()
                if prop.get_name() == prop_name and prop.get_device().get_name() == device_name:
                    self.root.after(0, self.create_property_controls)
        except Exception as e:
            self.log_message(f"Error actualizando los valores de las propiedades: {str(e)}", "ERROR")

                
                
    def show_property_details(self, device_name: str, prop_name: str):
        """Muestra los detalles completos de una propiedad seleccionada.

        Args:
            device_name (str): Nombre del dispositivo
            prop_name (str): Nombre de la propiedad
        """
        if not self.connected or not self.server:
            return
        
        try:
            prop = self.server.get_prop_of_device(device_name, prop_name)
            if not prop:
                return
            prop_type = prop.get_type()
            if not prop_type:
                self.log_message(f"Tipo de propiedad desconocido para {prop_name}", "WARNING")
                return
                
            elements = prop.get_elements()
            if not elements:
                self.log_message(f"No hay elementos en la propiedad {prop_name}", "WARNING")
                return
            details = "="*10 + "DETALLES DE PROPIEDAD\n"+ "="*10 + "\n\n"
            details += f"Nombre: {prop.get_name()}\n"
            details += f"Tipo: {prop.get_type()}\n"
            details += f"Dispositivo: {device_name}\n"
            details += f"Última actualización: {datetime.fromtimestamp(prop.last_update).strftime('%H:%M:%S') if prop.last_update > 0 else 'N/A'}\n\n"
            
            details += "="*10 + "ATRIBUTOS\n"+ "="*10 + "\n\n"
            for attr_name, attr_value in prop.get_attributes().items():
                details += f"{attr_name}: {attr_value}\n"
            
            details += "="*10 + "ELEMENTOS\n"+ "="*10 + "\n\n"

            for elem_name, element in prop.get_elements().items():
                details += f"* {elem_name}: {element.get_value() or 'N/A'}\n"
                for attr_name, attr_value in element.get_attributes().items():
                    details += f"  - {attr_name}: {attr_value}\n"
                details += "\n"
            
            self.property_details.delete(1.0, tk.END)
            self.property_details.insert(1.0, details)
            
        except Exception as e:
            self.log_message(f"Error mostrando detalles: {str(e)}", "ERROR")
        
    def on_device_combo_change(self, event):
        """Maneja el cambio en el combo de dispositivos del control.

        Args:
            event (tk.Event): Evento de cambio en el combobox
        """
        device_name = self.device_combo.get()
        if not device_name or not self.connected or not self.server:
            return
        
        # Actualizamos los combobox de las propiedades
        device = self.server.get_device_by_name(device_name)
        if device:
            properties = list(device.get_properties().keys())
            self.property_combo['values'] = properties
            self.property_combo.set('')
        
        # Limpiamos los controles de los widgets
        self.clear_control_widgets()
        
    def on_property_combo_change(self, event):
        """Maneja el cambio en el combo de propiedades del control.

        Args:
            event (tk.Event): Evento de cambio en el combobox
        """
        self.create_property_controls()
        
    def create_property_controls(self):
        """Crea controles dinámicos para la propiedad seleccionada.
        
        Genera automáticamente los controles apropiados según el tipo
        de la propiedad (Switch, Number, Text, Light, BLOB).
        """
        device_name = self.device_combo.get()
        prop_name = self.property_combo.get()
        
        if not device_name or not prop_name or not self.connected or not self.server:
            return
        
        self.clear_control_widgets()
        
        try:
            prop = self.server.get_prop_of_device(device_name, prop_name)
            if not prop:
                return
            
            prop_type = prop.get_type()
            elements = prop.get_elements()
            
            # Frame para los controles
            controls_frame = ttk.Frame(self.control_content_frame)
            controls_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_label = ttk.Label(controls_frame, 
                                  text=f"Controles para {prop_name} ({prop_type})", 
                                  style=self.HEADER_STYLE)
            title_label.pack(pady=(0, 20))
            
            # Creamos los controles según el tipo de la propiedad
            self.control_widgets = {}
            
            if prop_type == "Switch":
                self.create_switch_controls(controls_frame, elements)
            elif prop_type == "Number":
                self.create_number_controls(controls_frame, elements)
            elif prop_type == "Text":
                self.create_text_controls(controls_frame, prop, elements)
            elif prop_type == "Light": # Como la propiedad GPS_STATUS (No hay muchas)
                self.create_light_display(controls_frame, elements)
            elif prop_type == "BLOB":
                self.create_blob_controls(controls_frame, elements)
            
            # Botón de envío (excepto para Light y BLOB)
            if prop_type not in ["Light", "BLOB"]:
                send_btn = ttk.Button(controls_frame, text="Enviar Valores", 
                                    command=lambda: self.send_property_values(prop))
                send_btn.pack(pady=(20, 0))
            
        except Exception as e:
            self.log_message(f"Error creando controles: {str(e)}", "ERROR")
        
    def create_switch_controls(self, parent, elements: dict):
        """Crea controles para propiedades de tipo Switch.

        Args:
            parent (ttk.Widget): Widget padre donde crear los controles
            elements (dict): Diccionario de elementos de la propiedad
        """
        self.control_widgets = {}
        element_names = list(elements.keys())
        rule = None
        # Se intenta obtener la regla (OneOfMany, AtMostOne, etc.)
        for elem in elements.values():
            rule = elem.get_prop().get_from_attributes('rule')
            break

        if rule == "OneOfMany" and len(element_names) == 2:
            # Se usa un radiobutton para el tipo switch
            self.switch_var = tk.StringVar()
            # Se selecciona el que está On
            for name, elem in elements.items():
                if elem.get_value() == "On":
                    self.switch_var.set(name)
            for name in element_names:
                rb = ttk.Radiobutton(parent, text=name, variable=self.switch_var, value=name)
                rb.pack(anchor=tk.W)
            self.control_widgets["__switch__"] = self.switch_var
        else:
            # Para otros casos, usa checkboxes
            for name, elem in elements.items():
                var = tk.BooleanVar(value=(elem.get_value() == "On"))
                cb = ttk.Checkbutton(parent, text=name, variable=var)
                cb.pack(anchor=tk.W)
                self.control_widgets[name] = var
        
    def create_number_controls(self, parent, elements: dict):
        """Crea controles para propiedades de tipo Number.

        Args:
            parent (ttk.Widget): Widget padre donde crear los controles
            elements (dict): Diccionario de elementos de la propiedad
        """
        self.control_widgets = {}
        
        for elem_name, element in elements.items():
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{elem_name}:", width=20).pack(side=tk.LEFT)
            
            # Obtiene rango si está disponible
            try:
                min_val = float(element.get_from_attributes("min"))
                max_val = float(element.get_from_attributes("max"))
                current_val = float(element.get_value() or "0")
                
                # Scale widget
                var = tk.DoubleVar(value=current_val)
                scale = ttk.Scale(frame, from_=min_val, to=max_val, 
                                variable=var, orient=tk.HORIZONTAL, length=200)
                scale.pack(side=tk.LEFT, padx=(10, 0))
                
                # Entry para valor exacto
                entry = ttk.Entry(frame, textvariable=var, width=10)
                entry.pack(side=tk.LEFT, padx=(10, 0))
                
                # Labels de rango
                ttk.Label(frame, text=f"[{min_val} - {max_val}]").pack(side=tk.LEFT, padx=(10, 0))
                
            except (ValueError, TypeError, AttributeError):
                # Entry simple si no hay rango
                var = tk.StringVar(value=element.get_value() or "")
                entry = ttk.Entry(frame, textvariable=var, width=20)
                entry.pack(side=tk.LEFT, padx=(10, 0))
            
            self.control_widgets[elem_name] = var
        
    def create_text_controls(self, parent, prop: "INDIGOProperty", elements: dict):
        """Crea controles para propiedades de tipo Text.

        Args:
            parent (ttk.Widget): Widget padre donde crear los controles
            prop (INDIGOProperty): Propiedad INDIGO
            elements (dict): Diccionario de elementos de la propiedad
        """
        perm = prop.get_from_attributes('perm')
        
        if perm == "ro":
            ttk.Label(parent, text="[!] Propiedad de solo lectura", 
                     foreground="orange").pack(pady=(0, 10))
        
        self.control_widgets = {}
        
        for elem_name, element in elements.items():
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{elem_name}:", width=20).pack(side=tk.LEFT)
            
            var = tk.StringVar(value=element.get_value() or "")
            entry = ttk.Entry(frame, textvariable=var, width=40, 
                            state="readonly" if perm == "ro" else "normal")
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
            self.control_widgets[elem_name] = var
        
    def create_light_display(self, parent, elements: dict):
        """Crea display para propiedades de tipo Light.

        Args:
            parent (ttk.Widget): Widget padre donde crear los controles
            elements (dict): Diccionario de elementos de la propiedad
        """
        ttk.Label(parent, text="Estados de luces (solo lectura)").pack(pady=(0, 10))
        
        for elem_name, element in elements.items():
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=2)
            
            state = element.get_value() or "Unknown"
            color = {"Ok": "green", "Idle": "blue", "Busy": "orange", 
                    "Alert": "red"}.get(state, "gray")
            
            ttk.Label(frame, text=f"[*] {elem_name}: {state}", 
                     foreground=color).pack(side=tk.LEFT)
        
    def create_blob_controls(self, parent, elements: dict):
        """Crea controles para propiedades de tipo BLOB.

        Args:
            parent (ttk.Widget): Widget padre donde crear los controles
            elements (dict): Diccionario de elementos de la propiedad
        """
        ttk.Label(parent, text="Propiedades BLOB - Gestión de archivos").pack(pady=(0, 10))
        
        for elem_name, element in elements.items():
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{elem_name}:").pack(side=tk.LEFT)
            
            path = element.get_value() or ""
            if path:
                ttk.Button(frame, text="Descargar", 
                          command=lambda p=path: self.download_blob(p)).pack(side=tk.LEFT, padx=(10, 0))
                ttk.Label(frame, text=path).pack(side=tk.LEFT, padx=(10, 0))
            else:
                ttk.Label(frame, text="Sin archivo disponible").pack(side=tk.LEFT, padx=(10, 0))
        
    def send_property_values(self, prop: "INDIGOProperty"):
        """Envía los valores de una propiedad al servidor.

        Args:
            prop (INDIGOProperty): Propiedad cuyos valores se van a enviar
        """
        try:
            values = {}
            prop_type = prop.get_type()
            rule = prop.attributes.get('rule', None)
            elements = prop.get_elements()

            if prop_type == "Switch" and rule == "OneOfMany" and len(elements) == 2 and "__switch__" in self.control_widgets:
                selected = self.control_widgets["__switch__"].get()
                for name in elements:
                    values[name] = "On" if name == selected else "Off"
            else:
                for elem_name, widget_var in self.control_widgets.items():
                    if isinstance(widget_var, tk.StringVar):
                        values[elem_name] = widget_var.get()
                    elif isinstance(widget_var, tk.BooleanVar):
                        values[elem_name] = "On" if widget_var.get() else "Off"
                    elif isinstance(widget_var, tk.DoubleVar):
                        values[elem_name] = str(widget_var.get())

            prop.send_values_to_server(values)
            self.log_message(f"Valores enviados para {prop.get_name()}", "SUCCESS")

        except Exception as e:
            self.log_message(f"Error enviando valores: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error enviando valores:\n{str(e)}")
        
    def clear_control_widgets(self):
        """Limpia todos los widgets de control dinámicos."""
        for widget in self.control_content_frame.winfo_children():
            if widget != self.control_instructions:
                widget.destroy()
        
        self.control_instructions.pack(pady=50)
        
    def toggle_blob_mode(self):
        """Alterna el modo BLOB del servidor entre NEVER y URL."""
        if not self.connected or not self.server:
            return
        
        try:
            self.server.switch_blob_mode()
            self.update_blob_mode_display()
            self.log_message(f"Modo BLOB cambiado a: {self.server.get_blob_mode()}", "INFO")
            
        except Exception as e:
            self.log_message(f"Error cambiando modo BLOB: {str(e)}", "ERROR")
        
    def update_blob_mode_display(self):
        """Actualiza la visualización del modo BLOB actual."""
        if self.connected and self.server:
            mode = self.server.get_blob_mode()
            self.blob_mode_label.config(text=mode)
        
    def update_blob_properties(self, *args):
        """Actualiza la lista de propiedades BLOB disponibles."""
        if not self.connected or not self.server:
            return
                
        device_name = self.blob_device_combo.get()
        if device_name:
            device = self.server.get_device_by_name(device_name)
            if device:
                # Verificamos interfaz BLOB/CCD
                info_prop = device.get_property_by_name("INFO")
                if info_prop:
                    device_interface = info_prop.get_element("DEVICE_INTERFACE")
                    if device_interface:
                        interface_value = device_interface.get_value()
                        # Verificamos si es un dispositivo CCD (interfaz 2)
                        if interface_value and "2" in interface_value:
                            blob_properties = []
                            for prop_name, prop in device.get_properties().items():
                                if prop.get_type() == "BLOB":
                                    blob_properties.append(prop_name)
                            
                            self.blob_property_combo['values'] = blob_properties
                            if blob_properties:
                                self.blob_property_combo.set(blob_properties[0])
                        else:
                            self.log_message(f"El dispositivo {device_name} no es un CCD", "INFO")
                            self.blob_property_combo['values'] = []
                            self.blob_property_combo.set('')
                                
    def _update_blob_list(self, device):
        """Actualiza la lista de propiedades BLOB después de conectar."""
        blob_properties = []
        for prop_name, prop in device.get_properties().items():
            if isinstance(prop, INDIGOProperty) and prop.get_type() == "BLOB":
                    blob_properties.append(prop_name)
        
        self.blob_property_combo['values'] = blob_properties
        if blob_properties:
            self.blob_property_combo.set(blob_properties[0])
                        
    def enable_blob_property(self):
        """Habilita una propiedad BLOB específica."""
        if not self.server:
            self.log_message("No hay conexión al servidor", "ERROR")
            return

        device_name = self.blob_device_combo.get()
        property_name = self.blob_property_combo.get()
        
        if not device_name or not property_name:
            self.log_message("Selecciona dispositivo y propiedad BLOB", "WARNING")
            return
        
        try:
            if not self.server:
                raise ConnectionError("No hay conexión al servidor")
            if not self.server:
                raise ConnectionError("No hay conexión al servidor")
            device = self.server.get_device_by_name(device_name)
            if device:
                # Verificamos el estado de conexión
                connection_prop = device.get_property_by_name("CONNECTION")
                if connection_prop:
                    current_state = connection_prop.get_element("CONNECTED").get_value()
                    if current_state != "On":
                        self.log_message(f"Conectando dispositivo {device_name}...", "INFO")
                        connection_prop.send_values_to_server({"CONNECTED": "On"})
                        # Esperamos a que se conecte antes de habilitar BLOB
                        self.root.after(2000, lambda: self._enable_blob_after_connect(device_name, property_name))
                    else:
                        self._enable_blob_after_connect(device_name, property_name)
        except Exception as e:
            self.log_message(f"Error habilitando BLOB: {str(e)}", "ERROR")
        
    def _enable_blob_after_connect(self, device_name: str, property_name: str):
        """Habilita una propiedad BLOB después de que el dispositivo está conectado.
        
        Args:
            device_name (str): Nombre del dispositivo
            property_name (str): Nombre de la propiedad BLOB
        """
        try:
            if not self.server:
                self.log_message("No hay conexión al servidor", "ERROR")
                return
            self.server.send_blob_message(device_name, property_name)
            self.log_message(f"Esperando BLOB en {device_name}.{property_name}", "INFO")

            # Listener para descargar la imagen automáticamente cuando llegue el BLOB
            def blob_listener(prop):
                for elem in prop.get_elements().values():
                    # El path puede estar en atributos o como valor
                    path = elem.get_from_attributes("path") if "path" in elem.get_attributes() else elem.get_value()
                    self.log_message(f"Listener BLOB detectado path: {path}", "INFO")
                    if path and path.endswith(".fits"):
                        if self.server is not None:
                            self.download_blob(path)
            self.server.add_device_property_listener(device_name, property_name, blob_listener)
            self.log_message(f"BLOB habilitado para {device_name}.{property_name}", "SUCCESS")
        except Exception as e:
            self.log_message(f"Error habilitando BLOB: {str(e)}", "ERROR")
            
    def auto_register_blob_listeners(self):
        """Registra listeners para todas las propiedades BLOB de todos los dispositivos conectados."""
        if not self.connected or not self.server:
            return
        for device_name, device in self.server.get_devices().items():
            for prop_name, prop in device.get_properties().items():
                if prop.get_type() == "BLOB":
                    # Se evita registrar el mismo listener varias veces
                    def blob_listener(prop, device_name=device_name, prop_name=prop_name):
                        for elem in prop.get_elements().values():
                            path = elem.get_from_attributes("path") if "path" in elem.get_attributes() else elem.get_value()
                            self.log_message(f"[AUTO] Listener BLOB detectado path: {path}", "INFO")
                            if path and path.endswith(".fits"):
                                if self.server is not None:
                                    self.download_blob(path)
                    self.server.add_device_property_listener(device_name, prop_name, blob_listener)
                    
    def download_blob(self, path: str):
        """Descarga un archivo BLOB desde el servidor."""
        if not self.connected or not self.server:
            self.log_message("No hay conexión al servidor", "ERROR")
            return

        if not path:
            self.log_message("Ruta de BLOB no válida", "ERROR")
            return

        self.log_message(f"Intentando descargar imagen: {path}", "INFO")
        try:
            result = self.server.download_image(path)
            if result:
                self.log_message(f"Imagen descargada correctamente: {path}", "SUCCESS")
                self.refresh_images_list()
            else:
                self.log_message(f"Error al descargar la imagen: {path}", "ERROR")
                messagebox.showerror("Error", f"No se pudo descargar la imagen:\n{path}")
        except Exception as e:
            self.log_message(f"Error descargando imagen: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error descargando imagen:\n{str(e)}")
            
        
    def refresh_images_list(self):
        """Actualiza la lista de imágenes descargadas en la carpeta local."""
        self.images_listbox.delete(0, tk.END)
        
        images_dir = os.path.join(os.getcwd(), "images")
        
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.fits', '.fit', '.fts')):
                    self.images_listbox.insert(tk.END, filename)
        
    def view_selected_image(self):
        """Visualiza la imagen FITS seleccionada usando matplotlib."""
        selection = self.images_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una imagen")
            return
        
        filename = self.images_listbox.get(selection[0])
        filepath = os.path.join(os.getcwd(), "images", filename)
        
        try:
            import matplotlib.pyplot as plt
            from astropy.io import fits
            import numpy as np
            
            # Abrimos el archivo FITS
            hdul = fits.open(filepath)
            img_data = hdul[0].data
            hdul.close()
                
            plt.figure(figsize=(10, 8))
            plt.imshow(img_data, vmin=float(np.min(img_data)), 
                        vmax=float(np.mean(img_data)*2), origin="lower")
            plt.title(f"Imagen: {filename}")
            plt.colorbar()
            plt.show()
            
            self.log_message(f"Imagen mostrada: {filename}", "INFO")
            
        except Exception as e:
            self.log_message(f"Error mostrando imagen: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error mostrando imagen:\n{str(e)}")
        
    def open_images_folder(self):
        """Abre la carpeta de imágenes en el explorador del sistema."""
        images_dir = os.path.join(os.getcwd(), "images")
        
        try:
            if os.name == 'nt':  # Para Windows
                os.startfile(images_dir)
            elif os.name == 'posix':  # Para Linux/Mac
                os.system(f'xdg-open "{images_dir}"')
            
        except Exception as e:
            self.log_message(f"Error abriendo carpeta: {str(e)}", "ERROR")
        
    def delete_selected_image(self):
        """Elimina la imagen seleccionada del disco."""
        selection = self.images_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una imagen")
            return
        
        filename = self.images_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar {filename}?"):
            try:
                filepath = os.path.join(os.getcwd(), "images", filename)
                os.remove(filepath)
                self.refresh_images_list()
                self.log_message(f"Imagen eliminada: {filename}", "INFO")
                
            except Exception as e:
                self.log_message(f"Error eliminando imagen: {str(e)}", "ERROR")
        
    def export_devices(self):
        """Exporta la lista de dispositivos y sus propiedades a un archivo de texto."""
        if not self.connected or not self.server:
            messagebox.showwarning("Advertencia", "No hay conexión al servidor")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("LISTA DE DISPOSITIVOS INDIGO\n")
                    f.write("="*50 + "\n\n")
                    
                    devices = self.server.get_devices()
                    for device_name, device in devices.items():
                        f.write(f"Dispositivo: {device_name}\n")
                        f.write(f"Propiedades: {len(device.get_properties())}\n")
                        
                        for prop_name, prop in device.get_properties().items():
                            f.write(f"  - {prop_name} ({prop.get_type()})\n")
                        
                        f.write("\n")
                
                self.log_message(f"Lista exportada a: {filename}", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"Error exportando: {str(e)}", "ERROR")
        
    def clear_logs(self):
        """Limpia todo el contenido del área de logs."""
        self.logs_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Guarda el contenido actual de los logs en un archivo."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Archivos de log", "*.log"), ("Archivos de texto", "*.txt")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                
                self.log_message(f"Logs guardados en: {filename}", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"Error guardando logs: {str(e)}", "ERROR")
        
    def create_images_folder(self):
        """Crea la carpeta de imágenes si no existe."""
        images_dir = os.path.join(os.getcwd(), "images")
        
        try:
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                self.log_message("Carpeta de imágenes creada", "SUCCESS")
            else:
                self.log_message("La carpeta de imágenes ya existe", "INFO")
                
        except Exception as e:
            self.log_message(f"Error creando carpeta: {str(e)}", "ERROR")
        
    def restart_interface(self):
        """Reinicia la interfaz gráfica cerrando y volviendo a abrir."""
        if messagebox.askyesno("Confirmar", "¿Reiniciar la interfaz?"):
            if self.connected:
                self.disconnect_server()
            self.root.quit()
        
    def quit_application(self):
        """Cierra completamente la aplicación."""
        if messagebox.askyesno("Confirmar", "¿Salir de la aplicación?"):
            try:
                if self.connected:
                    self.disconnect_server()
                # Limpiamos los recursos
                self.clear_all_data()
                # Cerramos los logs pendientes
                self.log_message("Cerrando aplicación...", "INFO")
                self.root.quit()
            except Exception as e:
                print(f"Error cerrando aplicación: {e}")
                
        
    def clear_all_data(self):
        """Limpia todos los datos mostrados en la interfaz."""
        # Limpiamos las listas
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)
        
        for item in self.properties_tree.get_children():
            self.properties_tree.delete(item)
        
        # Limpiamos los combos
        self.device_combo['values'] = []
        self.property_combo['values'] = []
        self.blob_device_combo['values'] = []
        self.blob_property_combo['values'] = []
        self.device_selector_combo['values'] = []
        
        # Limpiamos las selecciones
        self.device_combo.set('')
        self.property_combo.set('')
        self.blob_device_combo.set('')
        self.blob_property_combo.set('')
        self.device_selector_combo.set('')
        
        # Limpiamos los detalles
        self.property_details.delete(1.0, tk.END)
        
        # Limpiamos los controles
        self.clear_control_widgets()
    
    
    def auto_update(self):
        """Ejecuta la actualización automática de datos si está habilitada.
        
        Se ejecuta periódicamente según el intervalo configurado
        para mantener la interfaz actualizada con los datos del servidor.
        """
        if self.auto_refresh.get() and self.connected:
            self.refresh_all_data()
        
        # Programamos siguiente actualización
        interval = self.refresh_interval.get() * 1000  # Convertir a milisegundos
        self.root.after(interval, self.auto_update)
        
    def run(self):
        """Inicia la aplicación y entra en el bucle principal de eventos.
        
        Registra el inicio de la aplicación en los logs y ejecuta
        el bucle principal de tkinter.
        """
        self.log_message("INDIGO Control Panel iniciado", "SUCCESS")
        self.log_message("Proyecto TFG - Arturo", "INFO")
        self.root.mainloop()


def main():
    """Función principal de la aplicación.
    
    Crea una instancia del panel de control INDIGO y la ejecuta,
    manejando cualquier excepción que pueda ocurrir durante el inicio.
    """
    try:
        app = INDIGOControlPanel()
        import signal
        def graceful_exit(signum, frame):
            print("\nCerrando GUI y conexión INDIGO de forma segura...")
            app.quit_application()
            sys.exit(0)
        signal.signal(signal.SIGINT, graceful_exit)
        app.run()
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()