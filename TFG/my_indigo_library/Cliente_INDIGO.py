import os
import socket
import threading
import time
from xml.etree.ElementTree import Element, XMLPullParser
import astropy.io.fits as fits
import matplotlib.pyplot as pyplot
import numpy as numpy
import requests



class INDIGO_Element:
    """Clase que representa un elemento de una propiedad de dispositivo INDIGO.
    
    Un elemento es la unidad mínima de información dentro de una propiedad INDIGO.
    Por ejemplo, una propiedad de coordenadas puede tener elementos para 
    ascensión recta y declinación.
    
    Attributes:
        name (str): Nombre del elemento
        prop (INDIGO_Property): Referencia a la propiedad que contiene este elemento
        attributes (dict): Diccionario con todos los atributos del elemento -> [nombre, valor]
        value (str): Valor actual del elemento
    """
    
    def __init__(self, xml_property: Element, prop: "INDIGO_Property"): #Se usa entre comillas para hacer una anotaciones forward y que no te dé el error de que no está definida
        """Constructor de la clase INDIGO_Element.

        Args:
            xml_property (xml.etree.Element.Element): XML que representa el elemento
            prop (INDIGO_Property): Propiedad INDIGO donde se incluye el elemento
        """
        self.prop = prop
        self.name = xml_property.get("name")    #ó se puede conseguir también con xml_property.attrib['name']
        self.attributes = {}
        self.value = None
    
    def __str__(self) -> str:
        """Listado de los datos del elemento.
        
        Returns:
            str: Descripción de los valores del elemento.
        """
        return f"\n\t\tINDIGO_Element(name={self.name}, value={self.value}, attributes={self.attributes})"
    
    def __repr__(self) -> str:
        """Representación o descripción del elemento.
        
        Returns:
            str: Listado con los valore del elemento.
        """

        return self.__str__()
    
    def parse_elements(self, xml_property: Element):
        """Actualiza los atributos y valor del elemento desde XML pasado como parámetro.

        Args:
            xml_property (xml.etree.Element.Element): Elemento XML con los nuevos datos
        """
        self.attributes = {**self.attributes, **xml_property.attrib}
        self.value = xml_property.text
    
    def get_name(self) -> str | None:
        """Obtiene el nombre del elemento.

        Returns:
            str |None: Nombre del elemento
        """
        return self.name
    def get_value(self) -> str | None:
        """Obtiene el valor del elemento.

        Returns:
            str | None: Valor actual del elemento
        """
        return self.value
        
    def get_prop(self) -> "INDIGO_Property":
        """Obtiene la propiedad a la que pertenece el elemento.

        Returns:
            INDIGO_Property: Propiedad que contiene este elemento
        """
        return self.prop
    
    def get_from_attributtes(self, name: str) -> str:
        """Obtiene el valor de un atributo específico del elemento.
        
        Los atributos comunes incluyen:
        
        - label: Etiqueta descriptiva del elemento
        - format: Formato de presentación del elemento
        - min: Valor mínimo permitido
        - max: Valor máximo permitido
        - step: Incremento entre valores válidos
        - path: Ruta de imagen (solo para propiedades BLOB)
        - target: Valor objetivo del elemento

        Args:
            name (str): Nombre del atributo a obtener

        Returns:
            str: Valor del atributo solicitado
        """
        return self.attributes[name]
    
    def get_attributes(self) -> dict:
        """Obtiene todos los atributos del elemento.

        Returns:
            dict: Diccionario con todos los atributos del elemento
        """
        return self.attributes
        
     
            
class INDIGO_Property:
    """Clase que representa una propiedad de un dispositivo INDIGO.
    
    Una propiedad agrupa elementos relacionados y define su comportamiento,
    tipo y restricciones. Los tipos de propiedades incluyen Text, Number,
    Switch, Light y BLOB.
    
    Attributes:
        name (str): Nombre de la propiedad
        device (INDIGO_Device): Dispositivo al que pertenece la propiedad
        type (str): Tipo de propiedad (Text, Number, Switch, Light, BLOB)
        attributes (dict): Atributos específicos de la propiedad
        elements (dict): Diccionario de elementos (elementos de la clase INDIGO_Element) que componen la propiedad
        lastUpdate (float): Timestamp de la última actualización
    """
    
    def __init__(self, xml_property: Element, device: "INDIGO_Device"):
        """Constructor de la clase INDIGO_Property.

        Args:
            xml_property (xml.etree.ElementTree.Element): Elemento XML que representa la propiedad 
            device (INDIGO_Device): Dispositivo INDIGO donde se incluye la propiedad
        """
        self.device = device
        self.name = xml_property.get("name")
        self.attributes = {}
        self.elements = {}
        self.last_update = 0
        self.type = None
        
        # Determinar el tipo de propiedad basado en el tag del XML
        list_names = {"Text", "Number", "Switch", "Light", "BLOB"}
        
        for name in list_names:
            if name in xml_property.tag:
                self.type = name
                break
            
            
    def __str__(self) -> str:
        """Listado de los datos de la propiedad.
        
        Returns:
            str: Descripción de los elementos de la propiedad
        """
        
        elements_str = "\n    ".join([str(elem) for elem in self.elements.values()])
        return (f"\nINDIGO_Property("
                f"\n  name={self.name}"
                f"\n  type={self.type}"
                f"\n  attributes={self.attributes}"
                f"\n  elements=[\n    {elements_str}\n  ]"
                f"\n  lastUpdate={self.last_update}"
                f")")

    def __repr__(self) -> str:        
        """Representación o descripción de la propiedad.
        
        Returns:
            str: Listado con los elementos de la propiedad
        """
        
        return self.__str__()
    
    def parse_properties(self, xml_properties: Element):
        """Actualiza la propiedad y sus elementos con el XML pasado.

        Args:
            xml_properties (xml.etree.ElementTree.Element): Elemento XML con los datos de la propiedad
        """
        
        self.last_update = time.time()
        self.attributes = {**self.attributes,**xml_properties.attrib} #Unimos los atributos de la propiedad junto con los elementos xml
        
        for elem in xml_properties.findall("./"):
            name_elem = elem.get('name')
            if name_elem not in self.elements:
                self.elements[name_elem] = INDIGO_Element(elem, self)
            self.elements[name_elem].parse_elements(elem)

    def get_name(self) -> str | None:
        """Obtiene el nombre de la propiedad.

        Returns:
            str | None: Nombre de la propiedad
        """
        return self.name
    
    def get_element(self, name: str) -> INDIGO_Element:
        """Obtiene un elemento específico por su nombre.

        Args:
            name (str): Nombre del elemento a buscar

        Returns:
            INDIGO_Element: Instancia del elemento solicitado
        """
        return self.elements[name]
    
    def get_elements(self) -> dict:
        """Obtiene todos los elementos de la propiedad.

        Returns:
            dict: Diccionario con todos los elementos de la propiedad
        """
        return self.elements
    
    def get_type(self) -> str | None:
        """Obtiene el tipo de la propiedad.

        Returns:
            str | None: Tipo de la propiedad (Text, Number, Switch, Light, BLOB)
        """
        return self.type
    
    def get_from_attributes(self, name: str) -> str:
        """Obtiene el valor de un atributo específico de la propiedad.
        
        Los atributos comunes incluyen:
        
        - group: Grupo al que pertenece la propiedad
        - label: Etiqueta descriptiva de la propiedad
        - perm: Permisos (rw=lectura/escritura, ro=solo lectura)
        - state: Estado actual de la propiedad
        - rule: Regla de validación (OneOfMany, AtMostOne, etc.)
        - timeout: Tiempo límite para operaciones
        - timestamp: Marca temporal de la última actualización
        - message: Mensaje descriptivo o de error

        Args:
            name (str): Nombre del atributo a obtener
            
        Returns:
            str: Valor del atributo o mensaje de error si no existe
        """
        if (name.lower() in self.attributes):
            return self.attributes[name]
        
        return "No existe este atributo en esta propiedad."
    
    def get_attributes(self) -> dict:
        """Obtiene todos los atributos de la propiedad.

        Returns:
            dict: Diccionario con todos los atributos de la propiedad
        """
        return self.attributes 
    
    def get_device(self) -> "INDIGO_Device":
        """Obtiene el dispositivo que contiene esta propiedad.

        Returns:
            INDIGO_Device: Dispositivo INDIGO que contiene esta propiedad
        """
        return self.device
    
    def send_values_to_server(self, values: dict):
        """Envía nuevos valores de los elementos al servidor INDIGO.

        Args:
            values (dict): Diccionario con nombres de elementos como claves 
                          y sus nuevos valores como valores -> [name, INDIGO_Element]
        """
        server : INDIGO_Server = self.device.get_server()
        message = f"<new{self.type}Vector device={self.device.get_name()} name='{self.name}'>\n"
        
        match self.type:
            case "BLOB":
                for name, value in values.items():
                    server.download_image(value)
        
            case "Switch":
                switches_on = 0
                for ele_name, ele_value in values.items():
                    if ele_value == "On":
                        switches_on+=1
                    message += f"   <one{self.type} name='{ele_name}' target='{ele_value}'>{ele_value}</one{self.type}>\n"
            
                rule = self.get_from_attributes('rule')
                if rule == "OneOfMany" and switches_on != 1:
                        raise RuntimeError("\nError: Sólo se puede seleccionar un único elemento Switch\n")
                elif rule == "AtMostOne" and  switches_on > 1:
                    raise RuntimeError("\nError: Sólo se puede seleccionar uno o ningún elemento Switch")
        
            case "Text":
                if self.get_from_attributes('perm') == "ro":
                    raise PermissionError("Error: Este elemento sólo se puede leer, no se puede escribir")
                else:
                    for ele_name, ele_value in values.items():
                        message += f"   <one{self.type} name='{ele_name}' target='{ele_value}'>{ele_value}</one{self.type}>\n"
            
            case "Number":
                for ele_name, ele_value in values.items():
                    element = self.get_element(ele_name)
                    
                    if(float(ele_value) < float(element.get_from_attributtes("min")) or float(ele_value) > float(element.get_from_attributtes("max"))):
                        raise ValueError("Error: El valor está fuera del rango permitido")    
                    message += f"   <one{self.type} name='{ele_name}' target='{ele_value}'>{ele_value}</one{self.type}>\n"

        message += f"</new{self.type}Vector>\n"
        
        server.send_values(message)
    
    
class INDIGO_Device:
    """Clase que representa un dispositivo registrado en el servidor INDIGO.
    
    Un dispositivo INDIGO puede ser cualquier instrumento astronómico como
    monturas, cámaras, ruedas de filtros, enfocadores, etc. Cada dispositivo
    contiene múltiples propiedades que definen su estado y configuración.
    
    Attributes:
        name (str): Nombre único del dispositivo
        server (INDIGO_Server): Referencia al servidor INDIGO donde está registrado
        properties (dict): Diccionario de propiedades del dispositivo
    """
    
    def __init__(self, name: str, server: "INDIGO_Server"):
        """Constructor de la clase INDIGO_Device.

        Args:
            name (str): Nombre del dispositivo
            server (INDIGO_Server): Instancia del servidor INDIGO
        """
        self.name=name
        self.server = server
        self.properties={}
        
    def __str__(self) -> str:
        """Listado de los datos del dispositivo.
        
        Returns:
            str: Descripción de los elementos del dispositivo.
        """
        
        properties_str = "\n    ".join([str(prop) for prop in self.properties.values()])
        return (f"\nINDIGO_Device("
            f"\n  name={self.name}"
            f"\n  server={self.get_server().get_name() if hasattr(self.server, 'get_name') else str(self.server)}"
            f"\n  properties=[\n    {properties_str}\n  ]"
            f")")

    def __repr__(self) -> str:
        """Representación o descripción del dispositivo.
        
        Returns:
            str: Listado con los elementos del dispositivo.
        """
        return self.__str__()
  
    def get_server(self) -> "INDIGO_Server":
        """Obtiene el servidor INDIGO asociado al dispositivo.

        Returns:
            INDIGO_Server: Instancia del servidor INDIGO
        """
        return self.server
    
    def get_properties(self) -> dict:
        """Obtiene todas las propiedades del dispositivo.

        Returns:
            dict: Diccionario de propiedades -> [nombre, INDIGO_Property]
        """
        return self.properties
    
    def get_property_by_name(self, property_name: str) -> INDIGO_Property:
        """Obtiene una propiedad específica por su nombre.

        Args:
            property_name (str): Nombre de la propiedad

        Returns:
            INDIGO_Property: Propiedad solicitada
        """
        return self.properties[property_name]
    
    def get_name(self) -> str:
        """Obtiene el nombre del dispositivo.

        Returns:
            str: Nombre del dispositivo
        """
        return self.name
    
    def parse_property(self, prop: Element):
        """Añade o actualiza una propiedad del dispositivo.

        Args:
            prop (ElementTree): Elemento XML que representa la propiedad
        """
        name_prop = prop.get('name')
        
        if name_prop not in self.properties:
            self.properties[name_prop] = INDIGO_Property(prop, self)

        self.properties[name_prop].parse_properties(prop)
        
    def delete_property(self, prop: INDIGO_Property):
        """Elimina una propiedad específica o todas las propiedades.

        Args:
            prop (ElementTree): Elemento XML con información de la propiedad a eliminar
        """
        if "name" in prop.get_attributes():
            name_prop = prop.get_from_attributes("name")
            if name_prop in self.properties[name_prop]:
                del self.properties[name_prop]
        
        else:
            # Si no se especifica la propiedad, se eliminan todas las propiedades del dispositivo
            self.properties.clear()
            

class INDIGO_Server:
    """"Clase que gestiona la conexión y comunicación con un servidor INDIGO.
    
    Esta clase maneja la conexión (que es sobre TCP/IP) con el servidor INDIGO, 
    el intercambio de mensajes en formato XML, la gestión de dispositivos y 
    la implantación de listeners para eventos que afecten al servidor.
    
    Attributes:
        name (str): Nombre identificativo del servidor.
        host (str): Dirección IP o hostname del servidor.
        port (int): Puerto de conexión (por defecto 7624).
        sock (socket.socket): Socket de conexión TCP.
        endReading (bool): Flag para controlar el bucle de lectura.
        thread (threading.Thread): Hilo para lectura asíncrona de mensajes.
        devices (dict): Diccionario de dispositivos conectados.
        wait (int): Tiempo de espera para operaciones.
        blobMode (str): Modo de manejo de datos BLOB (NEVER/URL).
        devicePropertyListeners (dict): Listeners para propiedades de dispositivos.
        serverListeners (dict): Listeners para eventos del servidor.
    """        
    def __init__(self, name: str, host: str, port: int):
        """
        Initicializa la conexión con el servidor INDIGO.
        
        Args:
            name (str): Nombre identificativo de la instancia del servidor.
            host (str): Dirección IP o hostname del servidor INDIGO.
            port (int, optional): Puerto del servidor INDIGO. Por defecto 7624.
        """
        self.name = name
        self.host = host
        self.port = port
        self.sock = None
        self.end_reading = False
        self.thread = None
        self.devices = {}
        self.wait = 1
        self.blob_mode = "NEVER"
        self.device_property_listeners = {}
        self.server_listeners = {}
    
    def __str__(self) -> str:
        """Listado de los datos del servidor.
        
        Returns:
            str: Descripción de los elementos del servidor.
        """
        
        devices_str = "\\n    ".join([str(device) for device in self.devices.values()])
        return (f"\\nINDIGO_Server("
                f"\\n  name={self.name}"
                f"\\n  host={self.host}"
                f"\\n  port={self.port}"
                f"\\n  blobMode={self.blob_mode}"
                f"\\n  devices=[\\n    {devices_str}\\n  ]"
                f")")

    def __repr__(self) -> str:
        """Representación o descripción del servidor.
        
        Returns:
            str: Listado con los elementos del servidor.
        """
        return self.__str__()
                
    def connect(self):
        """Establece la conexión con el servidor INDIGO.
        
        Crea un socket TCP, inicia el hilo de lectura de mensajes y
        solicita la lista inicial de propiedades del servidor
        (primer mensaje de descubrimiento que se hace siempre getProperties).
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(0.01)
            
            if self.sock is not None:
                self.thread = threading.Thread(target=self.read_messages, daemon = True)
                self.thread.start()
            else:
                raise ConnectionError("Error: No se pudo establecer la conexión")
            
            self.send_get_properties()
        
        except Exception as e:
            raise ConnectionError(f"Error conectando al servidor: {str(e)}")
        
    def add_server_listener(self, listener_function):
        """Añade un listener para eventos del servidor.

        Args:
            listener_function (callable): Función a ejecutar cuando ocurra un evento del servidor
        """
        name = self.name
        if name not in self.server_listeners:
            self.server_listeners[name]=[]
            
        self.server_listeners[name].append(listener_function)
    
    
    def add_device_property_listener(self, device_name: str, property_name:str, listener_function):
        """Añade un listener para cambios en una propiedad específica.

        Args:
            device_name (str): Nombre del dispositivo
            property_name (str): Nombre de la propiedad
            listener_function (callable): Función a ejecutar cuando cambie la propiedad
        """
        name = device_name + '@' + property_name
         
        if name not in self.device_property_listeners:
            self.device_property_listeners[name]=[]
            
        self.device_property_listeners[name].append(listener_function)

    def switch_blob_mode(self):
        """Función que alterna el valor del modo BLOB del servidor de 'Never' a 'URL' (de la imagen a descargar)."""
        self.blob_mode = "URL" if self.blob_mode == "NEVER" else "NEVER"    
    
    def send_blob_message(self, device: str, property: str):
        """Manda un mensaje al servidor para cambiar el BLOBMode de una propiedad en específico dentro de un dispositivo registrado.

        Args:
            device (str): Nombre del dispositivo donde se encuentra la propiedad 
            property (str): Nombre de la propiedad a cambiar el valor
        """
        if self.blob_mode == "URL":
            prop_dev = self.get_prop_of_device(device, property)
            if(prop_dev is not None):
                prop: INDIGO_Property = prop_dev
                if prop.get_type() == "BLOB":
                    self.send_values(f"<enableBLOB device='{device}' name='{property}'>{self.blob_mode}</enableBLOB>")
            else:
                raise ConnectionError("Error: Esta propiedad no es de tipo BLOB")
        else:
            raise ConnectionError("Error: Se está intentando enviar un mensaje BLOB con BLOB del servidor general en NEVER")
        
    
    def read_messages(self):
        """Lee mensajes del servidor de forma continua en un hilo independiente del hilo principal.
        
        Utiliza un parser XML para procesar los mensajes entrantes y
        ejecuta los listeners correspondientes cuando se detectan cambios.
        """
        parser = XMLPullParser(['end'])
        # Inicializar el parser con una raíz
        parser.feed("<xml>\n")

        while not self.end_reading and self.is_connected():
            msg= ""

            try:
                # Verificar que el socket existe antes de usar recv
                if self.sock is not None:
                    msg= self.sock.recv(500000).decode("UTF-8")
            except Exception:
                pass

            if msg != "":
                parser.feed(msg)
                for event_data in parser.read_events():
                    # event_data puede ser una tupla de diferentes tamaños
                    if len(event_data) == 1:
                        elem = event_data
                        # Verificar que elem no es None y tiene el método get
                        if elem.tag in ["defTextVector", "defNumberVector", "defSwitchVector", 
                                "defLightVector", "defBLOBVector", 
                                "setTextVector", "setNumberVector", "setSwitchVector", 
                                "setLightVector", "setBLOBVector"]:
                                # Verificar que elem.get('device') no es None
                                device_name = elem.get('device')
                                if device_name is not None:
                                    dev = self.get_device_by_name(device_name)
                                    dev.parse_property(elem)
                                    # Verificar que elem.get('name') no es None
                                    prop_name = elem.get('name')
                                    if prop_name is not None:
                                        prop = dev.get_property_by_name(prop_name)
                                        if prop.get_name() is not None: 
                                        name = device_name + "@" + prop_name

                                        if name is not None and name in self.device_property_listeners:
                                            for listener in self.device_property_listeners[name]:
                                                listener(prop)
                                
                        elif elem.tag == "delProperty":
                            device_name = elem.get('device')
                            if device_name is None:
                                continue
                            self.get_device_by_name(device_name).delete_property(elem)
                        
                        elif elem.tag == "message":
                            self.parse_message(elem)
                        
        
        if self.is_connected() and self.name in self.server_listeners: 
                for listener in self.server_listeners[self.name]:
                    listener()                
                
    def parse_message(self, xml_message: Element):
        """Procesa un mensaje XML recibido del servidor.

        Args:
            xml_message (ElementTree): Mensaje XML del servidor
        """
        device_name = xml_message.get('device')
        if device_name is not None:
            device = self.get_device_by_name(device_name)
            if device_name not in self.devices:
                self.devices[device_name] = INDIGO_Device(device_name, device.get_server())
                self.devices[device_name].parse_property(xml_message)
        
    def get_device_by_name(self, device_name: str) -> INDIGO_Device:
        """Obtiene un dispositivo buscando por su nombre,
            en caso de que no exista, lo crea.

        Args:
            device_name (str): Nombre del dispositivo

        Returns:
            INDIGO_Device: Instancia del dispositivo
        """
        
        if device_name not in self.devices:
            self.devices[device_name] = INDIGO_Device(device_name,self)
            
        return self.devices[device_name]

    def get_blob_mode(self) -> str:
        """Obtiene el modo BLOB actual.

        Returns:
            str: Modo BLOB actual (URL o NEVER)
        """
        return self.blob_mode
    
    def get_devices(self) -> dict:
        """Obtiene todos los dispositivos registrados en el servidor.

        Returns:
            dict: Diccionario de dispositivos -> [nombre, INDIGO_Device]
        """
        return self.devices
    
    def get_name(self) -> str:
        """Obtiene el nombre del servidor.

        Returns:
            str: Nombre del servidor
        """
        return self.name
    
    def get_host(self) -> str:
        """Obtiene la dirección IP o hostname del servidor.

        Returns:
            str: Dirección IP o hostname del servidor
        """
        return str(self.host)

    def get_port(self) -> int:
        """Obtiene el puerto del servidor.

        Returns:
            int: Puerto del servidor
        """
        return self.port 
    
    def send_get_properties(self):
        """Solicita al servidor la lista de todas propiedades (y sus dispositivos) que hay en el servidor 
        (Primer mensaje que se manda al conectarse al servidor).
        """
        self.send_values("<getProperties version='2.0' />")
        
        
    def send_values(self, message: str):
        """Envía un mensaje al servidor INDIGO.

        Args:
            message (str): Mensaje XML a enviar al servidor
        """
        message = message.encode("ASCII")
        if self.sock:
            self.sock.sendall(message)
        
        
    def is_connected(self) -> bool:
        """Verifica si la conexión con el servidor está activa.

        Returns:
            bool: True si está conectado, False en caso contrario
        """
        if self.sock is None:
            return False
        try:
            # Intenta recibir datos sin bloquear
            data = self.sock.recv(16, socket.MSG_PEEK)
            return len(data) != 0
        except (socket.timeout, BlockingIOError):
            return True  # No hay datos, pero el socket está abierto
        except OSError:
            return False  # El socket está cerrado o la conexión se perdió
        
        
    def get_prop_of_device(self, device_name: str, property_name: str) -> INDIGO_Property | None:
        """Obtiene una propiedad específica de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo
            property_name (str): Nombre de la propiedad

        Returns:
            INDIGO_Property | None: Propiedad solicitada o None si no existe
        """
        if(device_name in self.devices):
            dev : INDIGO_Device = self.devices[device_name]
            return dev.get_property_by_name(property_name)
        return None
        
    def disconnect(self):
        """Cierra la conexión con el servidor INDIGO de manera limpia."""
        if self.sock is not None:
            self.end_reading = True
            if self.sock:
                self.sock.close()
                self.sock = None
            if self.thread:
                self.thread.join(timeout=2.0)

    def download_image(self, path: str):
        """Descarga una imagen FITS desde el servidor y la muestra.
        
        Construye la URL completa, descarga la imagen en la carpeta 'images'
        y la muestra usando matplotlib.

        Args:
            path (str): Ruta relativa de la imagen en el servidor
        """
        if path:
            url = "http://" + self.get_host() + ":" + str(self.get_port()) + path
            print("La url construida es: ", url)
            name_image = path.split("/")[-1]            
            download_path = os.getcwd() + "/images"
            
            if not (os.path.exists(download_path)):
                os.mkdir(download_path)
            
            #Descargamos la imagen en la carpeta images
            download_path += "/" + name_image
            #Descargamos la información que haya en la url
            request = requests.get(url) 
            with open(download_path, "wb") as file:
                file.write(request.content)
            
            #Pintamos la imagen descargada
            img = fits.open(download_path)
            img_data = img[0].data
            
            pyplot.imshow(img_data, vmin= numpy.min(img_data), vmax=numpy.mean(img_data)*2, origin="lower")            
            pyplot.show()
            
