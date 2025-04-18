import xml.etree.ElementTree as ElementTree

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
    
    def parseElements(self, xml_property: ElementTree):
        """Creación o actualización de propiedades en el dispositivo INDIGO, esto se hace con una llamada recursiva a ParseElement de la clase INDIGO_Element

        Args:
            properties_dict (xml.etree.ElementTree.Element): Diccionario de propiedades a crear o actualizar

        Returns:
            xml.etree.ElementTree.Element: Elemento XML que representa la propiedad
        """
        self.attributes = {**self.attributes, **xml_property.get()}
        self.value = xml_property.getText()
    
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
    