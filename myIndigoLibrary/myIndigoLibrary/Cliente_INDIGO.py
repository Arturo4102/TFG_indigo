import os
import socket
import threading
import time
from xml.etree.ElementTree import Element, XMLPullParser
import astropy.io.fits as fits
import matplotlib.pyplot as pyplot
import numpy as numpy
import requests

class INDIGOElement:
    """Representa un elemento de una propiedad de dispositivo INDIGO.
    
    Un elemento es la unidad mínima de información dentro de una propiedad INDIGO.
    Por ejemplo, una propiedad de coordenadas puede tener elementos para 
    ascensión recta y declinación.
    
    Attributes:
        name (str): Nombre del elemento
        prop (INDIGOProperty): Referencia a la propiedad que contiene este elemento
        attributes (dict): Diccionario con todos los atributos del elemento -> [nombre, valor]
        value (str): Valor actual del elemento
    """
    
    def __init__(self, xml_property: Element, prop: "INDIGOProperty"): #Se usa entre comillas para hacer una anotaciones forward y que no te dé el error de que no está definida
        """Constructor de la clase INDIGOElement.

        Args:
            xml_property (xml.etree.Element.Element): XML que representa el elemento
            prop (INDIGOProperty): Propiedad INDIGO donde se incluye el elemento
        """
        self.prop = prop
        self.name = xml_property.get("name")
        self.attributes = {}
        self.value = None
    
    def __str__(self) -> str:
        """Listado de los datos del elemento.
        
        Returns:
            str: Descripción de los valores del elemento.
        """
        return f"\n\t\tINDIGOElement(name={self.name}, value={self.value}, attributes={self.attributes})"
    
    def __repr__(self) -> str:
        """Representación o descripción actualizada del elemento.
        
        Returns:
            str: Listado con los valore del elemento.
        """
        prop = self.get_prop()
        prop.device.get_server().refresh(device_name=prop.device.get_name(), property_name=prop.get_name())
        return self.__str__()
    
    def parse_elements(self, xml_property: Element):
        """Actualiza los atributos y valor del elemento desde el XML.

        Args:
            xml_property (xml.etree.Element.Element): Elemento XML con los nuevos datos
        """
        self.attributes = {**self.attributes, **xml_property.attrib}
        self.value = xml_property.text
    
    def get_name(self) -> str | None:
        """Obtiene el nombre del elemento.

        Returns:
            str or None: Nombre del elemento
        """
        return self.name
    def get_value(self) -> str | None:
        """Obtiene el valor del elemento.

        Returns:
            str or None: Valor actual del elemento
        """
        return self.value
        
    def get_prop(self) -> "INDIGOProperty":
        """Obtiene la propiedad a la que pertenece el elemento.

        Returns:
            INDIGOProperty: Propiedad que contiene este elemento
        """
        return self.prop
    
    def get_from_attributes(self, name: str) -> str:
        """Obtiene el valor de un atributo específico del elemento.
        
        Entre los atributos que nos encontramos tenemos:
        - name: Nombre del elemento (ejemplo: name='WIDTH')
        - label: Etiqueta descriptiva (ejemplo: label='Horizontal resolution')
        - format: Formato de presentación (ejemplo: format='%g')
        - min: Valor mínimo permitido (ejemplo: min='0')
        - max: Valor máximo permitido (ejemplo: max='1600')
        - step: Incremento entre valores válidos (ejemplo: step='1')
        - target: Valor objetivo del elemento (ejemplo: target='0')
        - path: Ruta de imagen o archivo BLOB (ejemplo: path='/blob/0x5a999035ff38.fits')

        Args:
            name (str): Nombre del atributo a obtener

        Returns:
            str: Valor del atributo solicitado
        
        Raises:
            KeyError: Si el atributo no existe.
        """
        if name in self.attributes:
            return self.attributes[name]
        raise KeyError(f"Atributo '{name}' no encontrado en {self}.")
            
    def get_attributes(self) -> dict:
        """Obtiene todos los atributos del elemento.

        Returns:
            dict: Diccionario con todos los atributos del elemento
        """
        return self.attributes
        
     
            
class INDIGOProperty:
    """Representa una propiedad de un dispositivo INDIGO.
    
    Una propiedad agrupa elementos relacionados y define su comportamiento,
    tipo y restricciones. Los tipos de propiedades incluyen Text, Number,
    Switch, Light y BLOB.
    
    Attributes:
        name (str): Nombre de la propiedad
        device (INDIGODevice): Dispositivo al que pertenece la propiedad
        type (str): Tipo de propiedad (Text, Number, Switch, Light, BLOB)
        attributes (dict): Atributos específicos de la propiedad
        elements (dict): Diccionario de elementos (elementos de la clase INDIGOElement) que componen la propiedad
        last_pdate (float): Timestamp de la última actualización
        is_complete (bool): Indica si la propiedad ha sido completamente inicializada.
        _last_hash (int): Hash de los valores de los elementos para detectar cambios.
    """
    
    def __init__(self, xml_property: Element, device: "INDIGODevice"):
        """Constructor de la clase INDIGOProperty.

        Args:
            xml_property (xml.etree.ElementTree.Element): Elemento XML que representa la propiedad 
            device (INDIGODevice): Dispositivo INDIGO donde se incluye la propiedad
        """
        self.device = device
        self.name = xml_property.get("name")
        self.attributes = {}
        self.elements = {}
        self.last_update = 0
        self.type = None
        self.is_complete = False 
        self._last_hash = 0

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
        return (f"\nINDIGOProperty("
                f"\n  name={self.name}"
                f"\n  type={self.type}"
                f"\n  attributes={self.attributes}"
                f"\n  elements=[\n    {elements_str}\n  ]"
                f"\n  lastUpdate={self.last_update}"
                f")")

    def __repr__(self) -> str:        
        """Representación o descripción actualizada de la propiedad.
        
        Returns:
            str: Listado con los elementos de la propiedad
        """
        self.device.get_server().refresh(device_name=self.device.get_name(), property_name=self.name)
        return self.__str__()
    
    def parse_properties(self, xml_properties: Element):
        """Actualiza la propiedad y sus elementos con el XML.

        Args:
            xml_properties (xml.etree.ElementTree.Element): Elemento XML con los datos de la propiedad
        """
        
        self.last_update = time.time()
        self.attributes = {**self.attributes,**xml_properties.attrib} #Unimos los atributos de la propiedad junto con los elementos xml
        
        for elem in xml_properties.findall("./"):
            name_elem = elem.get('name')
            if name_elem not in self.elements:
                self.elements[name_elem] = INDIGOElement(elem, self)
            self.elements[name_elem].parse_elements(elem)
        # Solo marcamos como completa si el XML es un cierre de vector y hay elementos
        if xml_properties.tag in ("defTextVector", "defNumberVector", "defSwitchVector", "defLightVector", "defBLOBVector") and len(self.elements) > 0:
            self.is_complete = True
        else:
            self.is_complete = False
        
        
    def get_name(self) -> str | None:
        """Obtiene el nombre de la propiedad.

        Returns:
            Returns:
            str or None: Nombre de la propiedad
        """
        return self.name
    
    def get_element(self, name: str) -> INDIGOElement:
        """Obtiene un elemento específico por su nombre.

        Args:
            name (str): Nombre del elemento a buscar

        Returns:
            INDIGOElement: Instancia del elemento solicitado
        
        Raises:
            KeyError: Si el elemento no existe.
        """
        if name in self.elements:
            return self.elements[name]
        raise KeyError(f"Elemento '{name}' no encontrado en la propiedad '{self.get_name()}'.")    
    
    def get_elements(self) -> dict:
        """Obtiene todos los elementso de la propiedad.

        Returns:
            dict: Diccionario con todos los elementos de la propiedad
        """
        return self.elements
    
    def get_type(self) -> str | None:
        """Obtiene el tipo de la propiedad.

        Returns:
            str orNone: Tipo de la propiedad (Text, Number, Switch, Light, BLOB)
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
        
        Raises:
            KeyError: Si el atributo no existe.
        """
        if name in self.attributes:
            return self.attributes[name]
        raise KeyError(f"Atributo '{name}' no encontrado en {self}.")
            
    def get_attributes(self) -> dict:
        """Obtiene todos los atributos de la propiedad.

        Returns:
            dict: Diccionario con todos los atributos de la propiedad
        """
        return self.attributes 
    
    def get_device(self) -> "INDIGODevice":
        """Obtiene el dispositivo que contiene esta propiedad.

        Returns:
            INDIGODevice: Dispositivo INDIGO que contiene esta propiedad
        """
        return self.device
    
    def send_values_to_server(self, values: dict):
        """Envía nuevos valores de los elementos al servidor INDIGO.

        Args:
            values (dict): Diccionario con nombres de elementos como claves 
                          y sus nuevos valores como valores
        """
        server: INDIGOServer = self.device.get_server()
        send_message = True
        rule = self.attributes.get('rule', None)
        perm = self.attributes.get('perm', 'rw')  # Por defecto 'rw' si no está perm en los atributos
        
        message = f"<new{self.type}Vector device='{self.device.get_name()}' name='{self.name}'>\n"

        if self.type == "Switch":
            number_on = 0
            for name, value in values.items():
                if value == "On":
                    number_on += 1
                message += f"  <one{self.type} name='{name}' target='{value}'>{value}</one{self.type}>\n"
            if rule == "OneOfMany" and number_on != 1:
                print("\n\t\t***** ERROR: Debes seleccionar solo un elemento *****\n")
                send_message = False
            elif rule == "AtMostOne" and number_on > 1:
                print("\n\t\t***** ERROR: Debes seleccionar uno o ninguno *****\n")
                send_message = False

        elif self.type == "Text":
            if perm == "ro":
                print("\n\t\t***** ERROR: Solo lectura *****\n")
                send_message = False
            else:
                for name, value in values.items():
                    message += f"  <one{self.type} name='{name}' target='{value}'>{value}</one{self.type}>\n"

        elif self.type == "Number":
            for name, value in values.items():
                element = self.get_element(name)
                val_min = float(element.get_from_attributes("min"))
                val_max = float(element.get_from_attributes("max"))
                value = float(value)
                message += f"  <one{self.type} name='{name}' target='{value}'>{value}</one{self.type}>\n"
                if value < val_min or value > val_max:
                    print("\n\t\t***** ERROR: Valor fuera de rango *****\n")
                    send_message = False

        elif self.type == "BLOB":
            for name, value in values.items():
                server.download_image(value)

        message += f"</new{self.type}Vector>\n"

        if send_message:
            server.send_values(message)
    
class INDIGODevice:
    """Representa un dispositivo registrado en el servidor INDIGO.
    
    Un dispositivo INDIGO puede ser cualquier instrumento astronómico como
    monturas, cámaras, ruedas de filtros, enfocadores, etc. Cada dispositivo
    contiene múltiples propiedades que definen su estado y configuración.
    
    Attributes:
        name (str): Nombre único del dispositivo
        server (INDIGOServer): Referencia al servidor INDIGO donde está registrado
        properties (dict): Diccionario de propiedades del dispositivo
        is_initialized (bool): Indica si el dispositivo ha sido completamente inicializado.
    """
    
    def __init__(self, name: str, server: "INDIGOServer"):
        """Constructor de la clase INDIGODevice.

        Args:
            name (str): Nombre del dispositivo
            server (INDIGOServer): Instancia del servidor INDIGO
        """
        self.name=name
        self.server = server
        self.properties={}
        self.is_initialized = False
        
    def __str__(self) -> str:
        """Listado de los datos del dispositivo.
        
        Returns:
            str: Descripción de los elementos del dispositivo.
        """
        
        properties_str = "\n    ".join([str(prop) for prop in self.properties.values()])
        return (f"\nINDIGODevice("
            f"\n  name={self.name}"
            f"\n  server={self.get_server().get_name() if hasattr(self.server, 'get_name') else str(self.server)}"
            f"\n  properties=[\n    {properties_str}\n  ]"
            f")")

    def __repr__(self) -> str:
        """Representación o descripción actualizada del dispositivo.
        
        Returns:
            str: Listado con los elementos del dispositivo.
        """
        self.server.refresh(device_name=self.name)
        return self.__str__()
  
    def get_server(self) -> "INDIGOServer":
        """Obtiene el servidor INDIGO asociado al dispositivo.

        Returns:
            INDIGOServer: Instancia del servidor INDIGO
        """
        return self.server
    
    def get_properties(self) -> dict:
        """Obtiene todas las propiedades del dispositivo.

        Returns:
            dict: Diccionario de propiedades
        """
        return self.properties
    
    def get_property_by_name(self, property_name: str) -> "INDIGOProperty | None":
        """Obtiene una propiedad específica por su nombre.

        Args:
            property_name (str): Nombre de la propiedad

        Returns:
            INDIGOProperty or None: Propiedad solicitada o None si no existe
        """
        return self.properties.get(property_name)
    
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
        self.is_initialized = False
        name_prop = prop.get('name')
        
        if name_prop not in self.properties:
            self.properties[name_prop] = INDIGOProperty(prop, self)

        self.properties[name_prop].parse_properties(prop)
        self.is_initialized = True

    def delete_property(self, prop: Element):
        """Elimina unaa propiedad específica o todas las propiedades.

        Args:
            prop (ElementTree): Elemento XML con información de la propiedad a eliminar
        """
        prop_name = prop.get('name')
        if prop_name is not None and prop_name in self.properties:
            del self.properties[prop_name]
            # Elimina los listeners asociados a la propiedad
            if hasattr(self.server, 'property_listeners'):
                key = (self.name, prop_name)
                if key in self.server.property_listeners:
                    del self.server.property_listeners[key]
        else:
            # Elimina todos los listeners de todas las propiedades
            for prop_name in list(self.properties.keys()):
                key = (self.name, prop_name)
                if key in self.server.property_listeners:
                    del self.server.property_listeners[key]
            self.properties.clear()
            

class INDIGOServer:
    """"Gestiona la conexión y comunicación con un servidor INDIGO.
    
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
        serverListeners (dict): Listeners para eventos del servidor.
        logger (MessageLogger): Logger para registrar mensajes y errores.
        property_listeners (dict): Listeners para propiedades.
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
        self.server_listeners = {}

    def __str__(self) -> str:
        """Listado de los datos del servidor.
        
        Returns:
            str: Descripción de los elementos del servidor.
        """
        
        devices_str = "\n    ".join([str(device) for device in self.devices.values()])
        return (f"\nINDIGOServer("
                f"\n  name={self.name}"
                f"\n  host={self.host}"
                f"\n  port={self.port}"
                f"\n  blobMode={self.blob_mode}"
                f"\n  devices=[\n    {devices_str}\n  ]"
                f")")

    def __repr__(self) -> str:
        """Representación o descripción actualizada del servidor.
        
        Returns:
            str: Listado con los elementos del servidor.
        """
        self.refresh()
        return self.__str__()
    
    def refresh(self, device_name=None, property_name=None, timeout=2.0):
        """
        Refresca el estado del servidor, un dispositivo o una propiedad.
        Espera activamente hasta que cambie el timestamp/hash o se agote el timeout.
        """
        start = time.time()
        if device_name and property_name:
            prop = self.get_prop_of_device(device_name, property_name)
            if prop:
                last_update = getattr(prop, "last_update", 0)
                last_hash = hash(tuple((k, v.get_value()) for k, v in prop.get_elements().items()))
                self.send_values(f"<getProperties device='{device_name}' name='{property_name}' />")
                while time.time() - start < timeout:
                    new_update = getattr(prop, "last_update", 0)
                    new_hash = hash(tuple((k, v.get_value()) for k, v in prop.get_elements().items()))
                    if new_update != last_update or new_hash != last_hash:
                        break
                    time.sleep(0.05)
        elif device_name:
            dev = self.get_device_by_name(device_name)
            if dev:
                last_update = max((getattr(p, "last_update", 0) for p in dev.get_properties().values()), default=0)
                self.send_values(f"<getProperties device='{device_name}' />")
                while time.time() - start < timeout:
                    new_update = max((getattr(p, "last_update", 0) for p in dev.get_properties().values()), default=0)
                    if new_update != last_update:
                        break
                    time.sleep(0.05)
        else:
            last_update = max((getattr(p, "last_update", 0) for d in self.devices.values() for p in d.get_properties().values()), default=0)
            self.send_get_properties()
            while time.time() - start < timeout:
                new_update = max((getattr(p, "last_update", 0) for d in self.devices.values() for p in d.get_properties().values()), default=0)
                if new_update != last_update:
                    break
                time.sleep(0.05)
    
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
            self.blob_mode = "URL" #Para que se puedan recoger las propiedades BLOB
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

    def switch_blob_mode(self):
        """Función que alterna el valor del modo BLOB del servidor de 'Never' a 'URL' (de la imagen a descargar)."""
        self.blob_mode = "URL" if self.blob_mode == "NEVER" else "NEVER"    
    
    def send_blob_message(self, device: str, property: str):
        """Manda un mensaje al servidor para cambiar el BLOBMode de una propiedad en específico dentro de un dispositivo registrado.

        Args:
            device (str): Nombre del dispositivo donde se encuentra la propiedad 
            property (str): Nombre de la propiedad a cambiar el valor
        """
        #Manda un mensaje al servidor para cambiar el BLOBMode de una propiedad en específico dentro de un dispositivo registrado.
        if self.blob_mode == "URL":
            self.send_values(f"<enableBLOB device='{device}' name='{property}'>{self.blob_mode}</enableBLOB>")
        else:
            raise ConnectionError("Error: Se está intentando enviar un mensaje BLOB con BLOB del servidor general en NEVER")
    
    def read_messages(self):
        """Lee mensajes del servidor de forma continua en un hilo independiente del hilo principal.
        
        Utiliza un parser XML para procesar los mensajes entrantes y
        ejecuta los listeners correspondientes cuando se detectan cambios.
        """
        parser = XMLPullParser(['end'])
        parser.feed("<xml>\n")

        while not self.end_reading and self.is_connected():
            msg = ""
            try:
                if self.sock is not None:
                    msg = self.sock.recv(500000).decode("UTF-8")
            except Exception:
                pass

            if msg != "":
                parser.feed(msg)
                for event_data in parser.read_events():
                    if len(event_data) < 2:
                        continue
                    _, elem = event_data
                    if elem is None or not isinstance(elem, Element) or not hasattr(elem, "tag") or not hasattr(elem, "get"):
                        continue

                    # Procesa vectores de propiedades
                    if elem.tag in [
                        "defTextVector", "defNumberVector", "defSwitchVector",
                        "defLightVector", "defBLOBVector",
                        "setTextVector", "setNumberVector", "setSwitchVector",
                        "setLightVector", "setBLOBVector"
                    ]:
                        device_name = elem.get('device')
                        if device_name is not None:
                            dev = self.get_device_by_name(device_name)
                            dev.parse_property(elem)
                            prop_name = elem.get('name')
                            if dev and prop_name is not None:
                                prop = dev.get_property_by_name(prop_name)
                                if prop and prop.get_name() is not None:
                                    self.notify_property_listeners(device_name, prop_name)
                        # Descarga de la imagen al recibir setBLOBVector
                        if elem.tag == "setBLOBVector":
                            for one_blob in elem.findall("oneBLOB"):
                                path = one_blob.get("path")
                                if path and path.endswith(".fits"):
                                    
                                    self.download_image(path)
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
                self.devices[device_name] = INDIGODevice(device_name, device.get_server())
                self.devices[device_name].parse_property(xml_message)
        
    def get_device_by_name(self, device_name: str) -> INDIGODevice:
        """Obtiene un dispositivo buscando por su nombre,
            en caso de que no exista, lo crea.

        Args:
            device_name (str): Nombre del dispositivo

        Returns:
            INDIGODevice: Instancia del dispositivo
        """
        
        if device_name not in self.devices:
            try:
                self.devices[device_name] = INDIGODevice(device_name, self)
            except Exception as e:
                raise RuntimeError(f"No se ha podido crear el dispositivo {device_name}: {e}")
        device = self.devices.get(device_name)
        if device is None:
            raise RuntimeError(f"No se ha podido obtener el dispositivo {device_name}")
        return device

    def get_blob_mode(self) -> str:
        """Obtiene el modo BLOB actual.

        Returns:
            str: Modo BLOB actual (URL o NEVER)
        """
        return self.blob_mode
    
    def get_devices(self) -> dict:
        """Obtiene todos los dispositivos registrados en el servidor.

        Returns:
            dict: Diccionario de dispositivos
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
        encoded_message: bytes = message.encode("ASCII")
        if self.sock:
            try:
                self.sock.sendall(encoded_message)
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                self.disconnect()        
        
    def is_connected(self) -> bool:
        """Verifica si la conexión con el servidor está activa.

        Returns:
            bool: True si está conectado, False en caso contrario
        """
        return self.sock is not None and self.sock.fileno() != -1
        
        
    def get_prop_of_device(self, device_name: str, property_name: str) -> INDIGOProperty | None:
        """Obtiene una propiedad específica de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo
            property_name (str): Nombre de la propiedad

        Returns:
            INDIGOProperty or None: Propiedad solicitada o None si no existe
        """
        if(device_name in self.devices):
            dev : INDIGODevice = self.devices[device_name]
            prop = dev.get_property_by_name(property_name)
            if prop:
                return prop
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

                            
    def add_device_property_listener(self, device_name, prop_name, callback):
        """Registra un listener para una propiedad de un dispositivo."""
        if not hasattr(self, 'property_listeners'):
            self.property_listeners = {}
        key = (device_name, prop_name)
        if key not in self.property_listeners:
            self.property_listeners[key] = []
        if callback not in self.property_listeners[key]:
            self.property_listeners[key].append(callback)
            
    def notify_property_listeners(self, device_name, prop_name):
        if not hasattr(self, 'property_listeners'):
            return
        listeners = self.property_listeners.get((device_name, prop_name), [])
        device = self.get_device_by_name(device_name)
        prop = device.get_property_by_name(prop_name)
        if prop and getattr(prop, "is_complete", False):
            current_hash = hash(tuple((k, v.get_value()) for k, v in prop.get_elements().items()))
            if getattr(prop, "_last_hash", None) == current_hash:
                return  # No hay cambio real asi que no hacesos nada más
            prop._last_hash = current_hash
            for callback in listeners:
                callback(prop)
            
    def download_image(self, path: str):
        """Descarga una imagen FITS desde el servidor y la muestra.
        
        Construye la URL completa, descarga la imagen en la carpeta 'images'
        y la muestra usando matplotlib.

        Args:
            path (str): Ruta relativa de la imagen en el servidor
        """
        if not path:
            print("[ERROR] Ruta de imagen vacía.")
            return False

        # Construir la URL
        url = f"http://{self.get_host()}:{self.get_port()}{path}"
        print(f"[INFO] Intentando descargar imagen desde: {url}")

        # Carpeta de destino (que si no existe se crea)
        images_dir = os.path.join(os.getcwd(), "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            print(f"[INFO] Carpeta 'images' creada en: {images_dir}")

        # Nombre del archivo
        name_image = os.path.basename(path)
        download_path = os.path.join(images_dir, name_image)

        try:
            response = requests.get(url)
            if response.status_code == 200 and response.content:
                with open(download_path, "wb") as file:
                    file.write(response.content)
                print(f"[SUCCESS] Imagen descargada correctamente en: {download_path}")
                # Mostramos la imagen FITS descargada
                try:
                    img = fits.open(download_path)
                    img_data = img[0].data
                    pyplot.imshow(img_data, vmin=float(numpy.min(img_data)), vmax=float(numpy.mean(img_data)*2), origin="lower")
                    pyplot.title(name_image)
                    pyplot.colorbar()
                    pyplot.show()
                except Exception as e:
                    print(f"[ERROR] No se pudo mostrar la imagen FITS: {e}")
                return True
            else:
                print(f"[ERROR] Fallo al descargar la imagen. Código HTTP: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Excepción al descargar la imagen: {e}")
            return False
            
