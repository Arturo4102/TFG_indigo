import os
import socket
import threading
import time
import xml.etree.ElementTree as ElementTree
import astropy.io.fits as fits
import matplotlib.pyplot as pyplot
import numpy as numpy
import requests
 
     
class INDIGO_Element:
    """Esta es una clase que representa un elemento de la propiedad del dispositivo registrado en el servidor INDIGO
    name: Nombre del elemento
    prop: Nombre de la propiedad donde está incluido el elemento
    attributes: Lista de todos los atributos que tiene actualmente el elemento
    value: Valor (numérico) que tiene el elemento
    """
    name: None
    prop: None
    attributes: None
    value: None
    
    def __init__(self, xml_property, prop):
        """Constructor de la clase Elemento

        Args:
            xml_property (xml.etree.ElementTree.Element): Elemento XML que representa el elemento
            prop (INDIGO_Property): Propiedad INDIGO donde se incluye el elemento
        """
        self.prop = prop
        self.name = xml_property.get("name")
        self.attributes = {}
        self.value = None
    
    def __str__(self):
        return f"\n\t\tINDIGO_Element(name={self.name}, value={self.value}, attributes={self.attributes})"
    
    def __repr__(self):
        return self.__str__()
    
    def parseElements(self, xml_property: ElementTree):
        """Creación o actualización de propiedades en el dispositivo INDIGO, esto se hace con una llamada recursiva a parseElements de la clase INDIGO_Element

        Args:
            properties_dict (xml.etree.ElementTree.Element): Diccionario de propiedades a crear o actualizar

        Returns:
            xml.etree.ElementTree.Element: Elemento XML que representa la propiedad
        """
        self.attributes = {**self.attributes, **xml_property.attrib}
        self.value = xml_property.text
    
    def getName(self) -> str:
        """Getter del nombre del elemento

        Returns:
            str: Nombre del elemento
        """
        return self.name
    def getValue(self) -> str:
        """Getter del valor (numérico) del elemento

        Returns:
            str: Valor del elemento
        """
        return self.value
        
    def getProp(self) -> str:
        """Getter del nombre de la propiedad a la que pertenece el elemento

        Returns:
            str: Nombre de la propiedad a la que pertenece el elemento
        """
        return self.prop
    
    def getFromAttributes(self, name: str) -> str:
        """Getter del valor de un atributo del elemento
        El elemento tiene algunos atributos como:
            - label: Etiqueta del elemento
            - format: Formato del elemento
            - min: Valor mínimo del elemento
            - max: Valor máximo del elemento
            - step: Valor de paso de un estado a otro del elemento
            - path: Ruta de la imagen que está guardada en el servidor (sólo funciona con las propiedades de tipo BLOB) 
            - target: Atributo objetivo del elemento
        Args:
            name (str): Nombre del elemento de buscar

        Returns:
            str: Valor del atributo
        """
        return self.attributes[name]
    
    def getAttributes(self) -> list:
        """Getter de todos los atributos del elemento

        Returns:
            list: Lista de atributos de los elementos
        """
        return self.attributes
        
     
            
class INDIGO_Property:
    """
    Clase para gestionar propiedades de los dispositivos registrados en el servidor INDIGO
    
    name: Nombre de la propiedad
    device: Dispositivo al que pertenece la propiedad
    type: Tipo de propiedad (Text, Number, Switch, Light, BLOB)
    attributes: Lista de atributos particulares de la propiedad
    elements: Diccionario de elementos (con valores numéricos) de la propiedad actual
    lastUpdate: Última actualización de la propiedad
    """
    name = None 
    device = None
    type = None
    attributes = None
    elements = None
    lastUpdate = 0
    
    def __init__(self, xml_property: ElementTree, device):
        """Constructor de la clase propiedad

        Args:
            xml_property (xml.etree.ElementTree.Element): Elemento XML que representa la propiedad 
            device (INDIGO_Device): Dispositivo INDIGO donde se incluye la propiedad
        """
        self.device = device
        self.name = xml_property.get("name")    #ó xml_property.attrib['name'] 
        self.attributes = {}
        self.elements = {}
        
        list_names = {"Text", "Number", "Switch", "Light", "BLOB"}
        
        for name in list_names:
            if name in xml_property.tag:
                self.type = name
                break
    def __str__(self):
        elements_str = "\n    ".join([str(elem) for elem in self.elements.values()])
        return (f"\nINDIGO_Property("
                f"\n  name={self.name}"
                f"\n  type={self.type}"
                f"\n  attributes={self.attributes}"
                f"\n  elements=[\n    {elements_str}\n  ]"
                f"\n  lastUpdate={self.lastUpdate}"
                f")")

    def __repr__(self):
        return self.__str__()
    # def add_property_listener(self, device_name: str, property_name: str, callback):
    #     """
    #     Agrega un listener a una propiedad de un dispositivo
    #     Args:
    #         device_name: Nombre del dispositivo
    #         property_name: Nombre de la propiedad
    #         callback: Función a ejecutar cuando cambie la propiedad
    #     """
    #     if not self.server.is_connected():
    #         raise ConnectionError("El servidor no está conectado.")
    #     self.server.server.addPropertyListener(device_name, property_name, callback)

    def parseProperties(self, xml_properties: ElementTree):
        """Creación o actualización de propiedades en el dispositivo INDIGO, esto se hace con una llamada recursiva a parseElements de la clase INDIGO_Element

        Args:
            properties_dict (xml.etree.ElementTree.Element): Diccionario de propiedades a crear o actualizar

        Returns:
            xml.etree.ElementTree.Element: Elemento XML que representa la propiedad
        """
        self.lastUpdate = time.time()
        self.attributes = {**self.attributes,**xml_properties.attrib} #Unimos los elementos xml
        
        for elem in xml_properties.findall("./"):
            name_elem = elem.get('name')
            if (not name_elem in self.elements):
                self.elements[name_elem] = INDIGO_Element(elem, self)
            self.elements[name_elem].parseElements(elem)

    def getName(self) -> str:
        """Getter del nombre de la propiedad

        Returns:
            str: Nombre de la propiedad
        """
        return self.name
    
    def getElement(self, name: str) -> INDIGO_Element:
        """Getter de un elemento dentro de la propiedad actual por su nombre

        Args:
            name (str): Nombre del elemento a buscar

        Returns:
            INDIGO_Element: Instancia del elemento
        """
        return self.elements[name]
    
    def getElements(self) -> dict:
        """Getter de todos los elementos de la propiedad actual

        Returns:
            dict: Diccionario de todos los elementos de esta propiedad
        """
        return self.elements
    
    def getType(self) -> str:
        """Getter del tipo de la propiedad ("Text", "Number", "Switch", "Light", "BLOB")

        Returns:
            str: tipo de la propiedad
        """
        return self.type
    
    def getFromAttributes(self, name: str) -> str:
        """ Getter del valor de un atributo de la propiedad
        La propiedad tiene algunos atributos como:
            - group: Grupo al que pertenece la propiedad
            - label: Etiqueta de la propiedad
            - perm: Permiso (rw, ro) de la propiedad
            - state: Estado de la propiedad
            - rule: Regla de la propiedad 
            - timeout: Timeout de la propiedad
            - timestamp: Timestamp de la propiedad      
            - message: Mensaje de la propieddad
            - light: atributo light para saber si es una propiedad light      
            ... (COMPLETAR)
        
        Args:
            name (str): Nombre del atributo a obtener
        Returns:
            str: Valor del atributo
        """
        if (name.lower() in self.attributes):
            return self.attributes[name]
        
        return "No existe este atributo en esta propiedad."
    
    def getAttributes(self) -> dict:
        """Getter de todos los atributos particulares de la propiedad actual

        Returns:
            dict: Diccionario de atributos de la propiedad actual
        """
        return self.attributes 
    
    def getDevice(self):
        """Getter del device donde se incluye esta propiedad

        Returns:
            INDIGO_Device: Instancia del dispositivo INDIGO donde está registrada esta propiedad
        """
        return self.device
    
    def sendValuesToServer(self, values: dict):
        """Función que envía nuevos valores (o los actualiza) de los elementos que componen la propiedad al servidor 

        Args:
            values (dict): Diccionario de los nombres (key) y valores (value) de los elementos que forman la propiedad
        """
        server : INDIGO_Server = self.device.getServer()
        message = f"<new{self.type}Vector device={self.device.get('name')} name='{self.name}'>\n"
        
        match self.type:
            case "BLOB":
                for name, value in values.items():
                    server.downloadImage(value)
        
            case "Switch":
                switchesOn = 0
                for ele_name, ele_value in values.items():
                    if ele_value == "On":
                        switchesOn+=1
                    message += f"   <one{self.type} name='{ele_name}' target='{ele_value}'>{ele_value}</one{self.type}>\n"
            
                rule = self.get('rule')
                if rule == "OneOfMany":
                    if switchesOn != 1:
                        raise("\nError: Sólo se puede seleccionar un único elemento Switch\n")
                elif rule == "AtMostOne":
                    if switchesOn > 1:
                        raise("\nError: Sólo se puede seleccionar uno o ningún elemento Switch")
        
            case "Text":
                if self.getAttributes('perm') == "ro":
                    raise("Error: Este elemento sólo se puede leer, no se puede escribir")
                else:
                    for ele_name, ele_value in values.items():
                        message += f"   <one{self.type} name='{ele_name}' target='{ele_value}'>{ele_value}</one{self.type}>\n"
            
            case "Number":
                for ele_name, ele_value in values.items():
                    element = self.GetElement(ele_name)
                    
                    if(float(ele_value) < float(element.getAttribute("Min")) or float(ele_value) > float(element.getAttribute("Max"))):
                        raise("Error: El valor está fuera del rango permitido")    
                    message += f"   <one{self.type} name='{ele_name}' target='{ele_value}'>{ele_value}</one{self.type}>\n"

        message += f"</new{self.type}Vector>\n"
        
        server.send(message)
    
    
class INDIGO_Device:
    
    name = None
    server = None
    properties = None
        
    def __init__(self, name: str, server: str):
        """Constructor de la clase dispositivo en el servidor INDIGO

        Args:
            name (str): Nombre del dispositivo
            server (str): Instancia del servidor
            properties (dict): Diccionario de propiedades en el dispositivo actual. Tiene el nombre de la propiedad como clave y the INDIGO_Property como valor
        """
        self.name=name
        self.server = server
        self.properties={}
        
    def __str__(self):
        properties_str = "\n    ".join([str(prop) for prop in self.properties.values()])
        return (f"\nINDIGO_Device("
            f"\n  name={self.name}"
            f"\n  server={self.server.getName() if hasattr(self.server, 'getName') else str(self.server)}"
            f"\n  properties=[\n    {properties_str}\n  ]"
            f")")

    def __repr__(self):
        return self.__str__()
  
    def getServer(self):
        """Getter de server del dispositivo

        Returns:
            IndigoSerevr: Instancia del Servidor de INDIGO 
        """
        return self.server
    
    
    def getServer(self):
        """Getter de server del dispositivo

        Returns:
            IndigoSerevr: Instancia del Servidor de INDIGO 
        """
        return self.server
    
    def getServerStr(self) -> str:
        """Getter de server del dispositivo

        Returns:
            IndigoSerevr: Instancia del Servidor de INDIGO 
        """
        return str(self.server)
    
    def getProperties(self) -> dict:
        """Getter de property del dispositivo

        Returns:
            dict: Diccionario de propiedades registradas en el dispositivo
        """
        return self.properties
    
    def getPropertyByName(self, propertyName: str) -> INDIGO_Property:
        """Getter de property del dispositivo por su nombre

        Args:
            propertyName (str): Nombre dle dispositivo

        Returns:
            INDIGO_Property: Propiedad de DeviceManager
        """
        return self.properties[propertyName]
    
    def getName(self) -> str:
        """Getter del nombre del dispositivo 

        Returns:
            str: Nombre del dispositivo
        """
        return self.name
    
    def parseProperty(self, prop: ElementTree):
        """Función que añade o modifica el valor de una propiedad (y sus respectivos elementos llamando a la función parseElements)

        Args:
            prop (ElementTree): Propiedad a añadir o modificar
        """
        nameProp = prop.get('name')
        
        if nameProp not in self.properties:
            self.properties[nameProp] = INDIGO_Property(prop, self)

        self.properties[nameProp].parseProperties(prop)
        
    def deleteProperty(self, prop: INDIGO_Property):
        """Función que elimina una propiedad o todas las propiedades (según si la propiedad pasada tiene el atributo nombre o no)

        Args:
            prop (INDIGO_Property): Propiedad o propiedades a eliminar del dispositivo
        """
        if "name" in prop.getAttributes():
            nameProp = prop.getAttribute("name")
            if nameProp in self.properties[nameProp]:
                del self.properties[nameProp]
        
        else:
            self.properties.clear()
            

class INDIGO_Server:
    """Clase que representa la conexión con el servidor INDIGO

    name: Nombre del servidor
    host: Dirección IP del servidor  
    port: Puerto del listerner para escuchar al servidor INDIGO (por defecto es 7624)
    sock: Variable que contiene el socket de conexión con el servidor
    endReading: Chequea si el socket ha terminado de leer todos los datos del servidor
    thread: Esto es una variable que contiene una hebra que ejecuta en bucle readMessages independientemente del main
    devices: Un diccionario de los dispositivos del servidor (key: nombre, value: INDIGO_Device)
    wait: Coloca un tiempo de espera para ejecutar las funciones
    blobMode: Se indica si el modo del Blob es 'Never' o 'URL'
    devicePropertyListeners: Lista de los listeners para las propiedades
    messageListeners: Lista de los listeners para los mensajes
    serverListeners: Lista de listeners para el servidor
    """
    name = None
    host = None
    port = -1
    sock = None
    endReading = False
    thread = None
    devices = None
    wait = 1
    blobMode = None
    
    devicePropertyListeners = None
    # messageListeners = None
    serverListeners = None
        
    def __init__(self, name: str, host: str, port: int):
        """
        Initicializa la conexión con el servidor INDIGO.
        Args:
            name (str): Nombre de la instancia del servidor INDIGO
            host (str): Dirección del servidor INDIGO
            port (int): Puerto del servidor INDIGO
        """
        self.name = name
        self.host = host
        self.port = port
        self.sock = None
        self.blobMode = "NEVER"
        self.devices={}
        self.devicePropertyListeners = {}
        # self.messageListeners = {}
        self.serverListeners = {}
    
    def __str__(self):
        devices_str = "\n    ".join([str(device) for device in self.devices.values()])
        return (f"\nINDIGO_Server("
            f"\n  name={self.name}"
            f"\n  host={self.host}"
            f"\n  port={self.port}"
            f"\n  blobMode={self.blobMode}"
            f"\n  devices=[\n    {devices_str}\n  ]"
            f")")

    def __repr__(self):
        return self.__str__()
                
    def connect(self):
        """Crea una conexión con el servidor usando un socket. Lanzamos una hebra que lea en bucle los mensajes del servidor
        y finalmente manda un getProperties para conseguir todos los dispositivos y propiedades que hay
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(.01)
            if self.sock != None:
                self.thread = threading.Thread(target=self.readMessages, daemon = True)
                self.thread.start()
            else:
                raise("Error: No Connection")
            
            self.sendGetProperties()
        
        except Exception as e:
            raise(f"Error connecting to server: {str(e)}")
        
    def addServerListener(self, listener_function):
        """Función que permite añadir Listeners al propio servidor 

        Args:
            listener_function (): Variable con una función que se ejecutará cuando el listener se active
        """
        name = self.name
        if not(name in self.serverListeners):
            self.serverListeners[name]=[]
            
        self.serverListeners[name].append(listener_function)
    
    
    def addDevicePropertyListener(self, deviceName: str, propertyName:str, listener_function):
        """Función que permite añadir Listeners a alguna propiedad de un dispositivo

        Args:
            listener_function (): Variable con una función que se ejecutará cuando el listener se active
        """
        name = deviceName + '@' + propertyName
         
        if not(name in self.devicePropertyListeners):
            self.devicePropertyListeners[name]=[]
            
        self.devicePropertyListeners[name].append(listener_function)
    
    
    # def addMessageListener(self, deviceName: str, listener_function: ):
    #     """Función que permite añadir Listeners a los mensajes que llegan del servidor INDIGO

    #     Args:
    #         listener_function (function): Variable con una función que se ejecutará cuando el listener se active
    #     """
    #     name = deviceName
         
    #     if not(name in self.messageListeners):
    #         self.messageListeners[name]=[]
            
    #     self.messageListeners[name].append(listener_function)
    

    def SwitchBLOB(self):
        """
        Función que cambia el valor de BLOB del servidor en general de 'Never' a 'URL' de la imagen a descargar
        """
        self.blobMode != self.blobMode
    
    def sendBLOBMessage(self, device: str, property: str):
        """Manda un mensaje al servidor para cambiar el BLOBMode de una propiedad en específico dentro de un dispositivo en específico

        Args:
            device (str): Nombre del dispositivo donde se encuentra la propiedad 
            property (str): Nombre de la propiedad a cambiar el valor
        """
        if self.blobMode == "URL":
            prop: INDIGO_Property = self.getPropOfDevice(device, property)
            
            if prop != None and prop.getType() == "BLOB":
                self.sendValues(f"<enableBLOB device='{device}' name='{property}'>{self.blobMode}</enableBLOB>")
            else:
                raise("Error: Esta propiedad no es de tipo BLOB")
        else:
            raise("Error: Se está intentando enviar un mensaje BLOB con BLOB del servidor general en NEVER")
        
    
    def readMessages(self):
        """Función que permite leer en un bucle continuamente los mensajes recibidos desde el servidor.
        Para ello, se utiliza un parser XML(esto se usa para parsear al mismo estilo que vienen los mensajes que llegan desde el servidor)
        para leer los mensajes y se ejecutan los listeners correspondientes
        """
        parser= ElementTree.XMLPullParser(['end'])

        parser.feed("<xml>\n")

        while not self.endReading and self.isConnected():
            msg= ""

            try:
                msg= self.sock.recv(500000).decode("UTF-8")
            except Exception as e:
                pass

            if(msg != ""):
                parser.feed(msg)
                for event, elem in parser.read_events():
                    if elem.tag == "defLightVector":
                        print("This a light")
                    if (elem.tag == "defTextVector") or (elem.tag == "defNumberVector") or (elem.tag == "defSwitchVector") or (elem.tag == "defLightVector") or (elem.tag == "defBLOBVector") or (elem.tag == "setTextVector") or (elem.tag == "setNumberVector") or (elem.tag == "setSwitchVector") or (elem.tag == "setLightVector") or (elem.tag == "setBLOBVector"):
                        dev = self.getDeviceByName(elem.get('device'))     
                        dev.parseProperty(elem)
                        prop = dev.getPropertyByName(elem.get('name'))
                        name= dev.getName() + "@" + prop.getName()

                        if name in self.devicePropertyListeners:
                            for listener in self.devicePropertyListeners[name]:
                                listener(prop)
                                
                    elif(elem.tag == "delProperty"):
                        self.getDeviceByName(elem.get('device')).deleteProperty(elem)
                    
                    elif(elem.tag == "message"):
                        self.parseMessage(elem)
                        
        
        if self.isConnected():
            # Call a function with the execute of server's listener  
            if(self.name in self.serverListeners):
                for listener in self.serverListeners[self.name]:
                    listener()                
                
    def parseMessage(self, xml_message: ElementTree):
        """Función que parsea un mensaje entero (con dispositivos y propiedades) y añade los dispositivos y propiedades al diccionario de dispositivos

        Args:
            xml_message (ElementTree): Mensaje XML del servidor
        """
        deviceName = xml_message.get('device')
        if not deviceName in self.devices:
            self.devices[deviceName] = INDIGO_Device(deviceName,self)
        
        self.devices[deviceName].parseProperty(xml_message)
        
    def getDeviceByName(self, deviceName: str) -> INDIGO_Device:
        """Función que permite conseguir un objeto dispositivo a partir de su nombre

        Args:
            deviceName (str): Nombre del dispositivo a buscar

        Returns:
            INDIGO_Device: Objeto dispositivo
        """
        if not deviceName in self.devices:
            self.devices[deviceName] = INDIGO_Device(deviceName,self)
            
        return self.devices[deviceName]

    def getBLOBMode(self) -> str:
        """Función para coneguir el valor de BLOBMode

        Returns:
            str : Valor del BLOBMode (URL o Never)
        """
        return self.blobMode
    
    def getDevices(self) -> dict:
        """Función que devuelve el diccionario de dispositivos registrados en el servidor

        Returns:
            dict: Diccionario de dispositivos (key: nombre del dispositivo, value: INDIGO_Device)
        """
        return self.devices
    
    def getName(self) -> str:
        """Getter del nombre del servidor INDIGO

        Returns:
            str: Nombre del servidor
        """
        return self.name
    
    def getHost(self) -> str:
        """Getter de la dirección IP del servidor INDIGO

        Returns:
            str: Dirección IP del servidor
        """
        return self.host

    def getPort(self) -> str:
        """Getter del puerto del servidor INDIGO

        Returns:
            str: Puerto del servidor
        """
        return self.port 
    
    def sendGetProperties(self):
        """Función que manda un mensaje al servidor para conseguir todos los dispositivos y propiedades que hay (mensaje de descubrimiento de propiedades)
        """
        self.sendValues("<getProperties version='2.0' />")
        
        
    def sendValues(self, message:str):
        """Función que envía valores (a través de mensajes) al servidor INDIGO 

        Args:
            message (str): Mensaje a enviar al servidor
        """
        message = message.encode("ASCII")
        if self.sock:
            self.sock.sendall(message)
        
        
    def isConnected(self) -> bool:
        if self.sock is None:
            return False
        try:
            data = self.sock.recv(16, socket.MSG_PEEK)
            return len(data) != 0
        except (socket.timeout, BlockingIOError):
            return True  # No hay datos, pero el socket está abierto
        except (ConnectionResetError, OSError):
            return False  # El socket está cerrado o la conexión se perdió
        
        
    def getPropOfDevice(self, deviceName:str, property:str) -> INDIGO_Property:
        """ Función que permite conseguir una propiedad de un dispositivo a partir del nombre del dispositivo y el nombre de la propiedad

        Args:
            deviceName (str): Nombre del dispositivo
            property (str): Nombre de la propiedad

        Returns:
            INDIGO_Property: Propiedad del dispositivo
        """
        if(deviceName in self.devices):
            dev :INDIGO_Device = self.devices[deviceName]
            return dev.getPropertyByName(property)
        return None
        
    def disconnect(self):
        """
        Cierra la conexión con el servidor INDIGO de manera limpia.
        """
        if not(self.sock != None):
            self.endReading = True
            if self.sock:
                self.sock.close()
                self.sock = None
            if self.thread:
                self.thread.join(timeout=2.0)

    def downloadImage(self, path:str):
        """ Función que descarga una imagen a partir de la url que se le pasa como parámetro.
        La url se construye a partir de la dirección IP y el puerto del servidor INDIGO, y la url que se le pasa como parámetro.
        La imagen se guarda en la carpeta images del directorio actual, y se le pone el mismo nombre que la imagen original.
        La imagen se muestra en una ventana de matplotlib.
        Args:
            path (str): URL de la imagen a descargar
        """
        if path:
            url = "http://" + self.getHost() + ":" + self.getPort() + path
            print("La url construida es: ", url)
            nameImage = path.split("/")[-1]            
            downloadPath = os.getcwd() + "/images"
            
            if not (os.path.exists(downloadPath)):
                os.mkdir(downloadPath)
            
            #Descargamos la imagen en la carpeta images
            downloadPath += "/" + nameImage
            #Descargamos la información que haya en la url
            request = requests.get(url) 
            with open(downloadPath, "wb") as file:
                file.write(request.content)
            
            #Pintamos la imagen descargada
            img = fits.open(downloadPath)
            imgData = img[0].data
            
            pyplot.imshow(imgData, vmin= numpy.min(imgData), vmax=numpy.mean(imgData)*2, origin="lower")            
            pyplot.show()
            
