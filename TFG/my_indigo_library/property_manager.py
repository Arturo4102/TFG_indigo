import xml.etree.ElementTree as ElementTree
from my_indigo_library.Cliente_INDIGO import INDIGO_Server, INDIGO_Device, INDIGO_Element
import time

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
    
    def getValue(self) -> str:
        """Getter del value de la propiedad

        Returns:
            str: Valor de la propiedad
        """
        return self.value
    
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
    
