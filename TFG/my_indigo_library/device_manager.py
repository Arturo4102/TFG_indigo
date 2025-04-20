from my_indigo_library.Cliente_INDIGO import INDIGO_Property
import xml.etree.ElementTree as ElementTree

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

    def getServer(self):
        """Getter de server del dispositivo

        Returns:
            IndigoSerevr: Instancia del Servidor de INDIGO 
        """
        return self.server
    
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
            
