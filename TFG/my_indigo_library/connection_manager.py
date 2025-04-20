import os
import socket
import threading
import xml.etree.ElementTree as ElementTree
import astropy.io.fits as fits
import matplotlib.pyplot as pyplot
import numpy as numpy
import requests
from my_indigo_library.Cliente_INDIGO import INDIGO_Property, INDIGO_Device

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
            
