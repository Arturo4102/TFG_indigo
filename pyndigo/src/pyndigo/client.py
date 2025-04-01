'''
asdfasdf
'''

# Módulo para escribir código concurrente para manejar operaciones asíncronas, como conexiones de red
import asyncio
# Módulo para trabajar con datos JSON, permitiendo la serialización y deseralización de objetos JSON 
import json
# Módulo para trabajar con hilos, permitiendo la ejecución concurrente en diferentes hilos
import threading
import time

# Importa todo el módulo common que está en el mismo paquete
from .common import *


# Clase que maneja la comunicación con el servidor Pyndigo y que hereda de ayncio (para manejar las conexiones con el servidor web)
class PyndigoClient(asyncio.Protocol):

    # Constructor del objeto que permite escribir características del cliente: el nombre, dirección IP, puerto del servidor
    # diccionario que tiene los dispositivos clientes, mensajes, tiempo y el objeto asyncio transporte para manejar la conexión 
    def __init__(self, name, host, port):
        self._name = name
        self._host = host
        self._port = port
        self._client_devices = {}
        self._timestamp = 0
        self._message = 0
        self._transport = None
    # Los diccionarios no tienen orden específico y se almacenan asociando una clave (el nombre del dispositivo en este caso) con el propio dispositivo
    # para acceder se necesita acceder con la clave (el nombre del dispositivo) y para eliminarlo igual 

    # GETTERS
    # Retorna una copia de los dispositivos cliente (-> permite indicar que va tipo de dato devuelve, sólo para documentación)
    def get_client_devices(self) -> dict:
        return self._client_devices.copy()
    # Retorna el nombre del cliente, retorna un string
    def get_name(self) -> str:
        return self._name
    # Retorna un dispositivo específico por su nombre, retorna un dispositivo Pyndigo
    def get_client_device(self, device_name) -> PyndigoDevice:
        return self._client_devices.get(device_name)
    
    # ADDER / REMOVER
    # Agrega al diccionario del objeto self, el dispositivo device
    def _add_client_device(self, device: PyndigoDevice):
        self._client_devices[device.get_name()] = device
    # Elimina el dispositivo que tenga el nombre específico deviceName, el momento en el que se ha realizado (timestamp)
    # y el motivo de la eliminación (message)
    def _remove_client_device(self, deviceName: str, timestamp, message: str):
        if deviceName in self._client_devices:        
            self._client_devices.pop(deviceName)
            self._timestamp = timestamp
            self._message = message

            print("Removing device " + deviceName)               

    # MESSAGE HANDLING
    # Actualiza el momento (timestamp) y el mensaje (message)  
    def _update_message(self, timestamp, message):
        self._timestamp = timestamp
        self._message = message
    
    # Retorna el timestamp actual
    def get_timestamp(self):
        return self._timestamp
    
    # Retorna el mensaje actual
    def get_message(self):
        return self._message


    # CONNECTION
    # Inicia un nuevo hilo separado que establece una conexión mediante la libería threading, esto se hace para 
    # que el programa principal no se detenga cuando nos intentamos conectar, sino que lo hagamos mediante un otro hilo 
    def stablish_connection(self):
        x = threading.Thread(target=self._thread_stablish_connection)
        x.start()

    # Esta función crea y gestiona un bucle de eventos asíncronos (para la conexión) que manejará la conexión al servidor
    def _thread_stablish_connection(self):
        #loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Se crea la conexión
        coro = loop.create_connection(lambda: self, self._host, self._port)
        print("1")
        # Se ejecuta la rutina coro, hasta que la conexión se establezca o falle
        loop.run_until_complete(coro)
        print("2")
        # Una vez que la conexión está establecida, entra en modo de ejecución continua 
        loop.run_forever()
        print("3")
        # Cierra el bucle, pero como está en run_forever, se ejecuta esta línea solo si se interrumpe o se cierra el bucle  
        loop.close()
        print("4")


    # CONNECTION EVENTS
    # Método que se llama cuando se realiza la conexión de un objeto y se piden sus propiedades
    def connection_made(self, transport):
        # El objeto transport se guarda dentro del transport para gestionar luego la conexión con el servidor
        self._transport = transport
        # Además, envia el objeto message (un JSON) solicitando las propiedades del cliente
        message = { "getProperties": {"version": 512, "client": self._name} }
        # Esta función se usa para enviar el mensaje al servidor usando el objeto transport
        self._writeMsg(message)

        #self._transport.write(message.encode())
        # Se confirma que el mensaje ha sido enviado imprimiendo la información del mismo
        print('data sent: {}'.format(message))

    # Método que se ejecuta cuando el cliente recibe datos del servidor
    def data_received(self, data):
        # Se convierte a data de bits a cadena de texto y se reemplazan los '}{' por '},{' para que se traten como una lista JSON
        dataR = "[" + data.decode().replace("}{", "},{") + "]" #Los corchetes marcan el inicio y fin de la lista JSON
        #print('data received: {}'.format(dataR))
        
        # Convierte el JSON en una estructura de diccionario de Python
        y = json.loads(dataR)
        #print(yaml.dump(y, default_flow_style=False))
        
        # Llama a la función (creada a continuación) _parse_messages, para interpretar que quiere realizar el mensaje (get, set, message o deleteProperty)
        self._parse_messages(y)

    # Método auxiliar que interpreta los mensajes recibidos y verifica si se quiere registrar o modificar una propiedad del dispositivo está registrado en self
    # o si se quiere eliminar una propiedad o simplemente recibir un mensaje
    def _parse_messages(self, messages):
        # Imprime los mensajes y los recorre para ver de qué tipo son
        print(messages)
        for m in messages:
            for key, value in m.items():
                
                # Definir una nueva propiedad en un dispositivo
                if key.startswith("def"):
                    # Buscamos el dispositivo con la clave value en el campo device, si no existe lo crea
                    dev = self._get_device_or_create(value['device'])
                    
                    # Buscamos si la propiedad en el dispositivo encontrado/creado existe
                    prop = dev.get_property(value["name"])
                    # Si no existe, crea el tipo de propiedad que tiene la clave key
                    if prop == None:  # If the property does not exist. Avoid changing existing properties
                        if key == "defTextVector":
                            type = TYPE_TEXT
                        elif key == "defNumberVector":
                            type = TYPE_NUMBER
                        elif key == "defSwitchVector":
                            type = TYPE_SWITCH
                        elif key == "defLightVector":
                            type = TYPE_LIGHT
                        else:
                            type = TYPE_BLOB
                        # Creamos con el constructor una propiedad PyndigoProperty(definición en common.py)
                        # _decoded_json permite recibir el objeto value con todo el nombre, state, label... y añadirlo al objeto self 
                        prop = PyndigoProperty(dev, type, _decoded_json = value) # Also gets added to the device
                        # Se notifica que la propiedad ha cambiado
                        self.property_has_changed(prop)

                # Modificamos el valor de una propiedad del dispositivo
                elif key.startswith("set"):
                    # Obtenemos el dispositivo cliente con la clave value en el registro device
                    dev = self.get_client_device(value['device'])
                    # Si existe el dispositivo, se busca la propiedad, se cambia y se avisa de que se ha cambiado
                    if dev != None:
                        prop = dev.get_property(value['name'])

                        prop._update(_decoded_json = value)

                        self.property_has_changed(prop)
                
                # Mensaje de información, se cogen los datos de dispositivo, el mensaje y el tiempo
                elif key == "message":
                    devName = value.get('device')
                    message = value.get('message')
                    timestamp = value.get('timestamp')

                    # Si el mensaje está asociado a un dispositivo registrado, se actualiza el dispositivo y se añade un mensaje
                    if devName != None:
                        dev = self.get_client_device(devName)

                        if dev != None:
                            dev._update_message(timestamp, message)

                            self.device_message_arrived(dev)

                    # Sino el mensaje es generíco y se actualiza dentro de la propia conexión self
                    else:
                        self._update_message(timestamp, message)

                        self.client_message_arrived()

                # Borrar una propiedad o un dispositivo entero
                elif key == "deleteProperty":
                    # Recogemos los datos del mensaje
                    devName = value.get('device')
                    propertyName = value.get('name')
                    message = value.get('message')
                    timestamp = value.get('timestamp')
                    # Si hay nombre del dispositivo, se busca el dispositivo
                    if devName != None:
                        dev = self.get_client_device(devName)

                        # Si el dispositivo está registrado, se elimina ve si el nombre de la propiedad es una en específico o no
                        # Si está vacío el nombre de la propiedad, eliminamos todas las propiedades del dispositivo y el propio dispositivo  
                        if dev != None:
                            if propertyName == None:  # Remove entire device
                                properties = dev.get_properties()

                                for p in properties.values():
                                    dev.remove_property(p.get_name(), message, timestamp)

                                self._remove_client_device(devName, message, timestamp)
                            # Si tiene un nombre la propiedad, se elimina solo la propiedad
                            else:
                                dev.remove_property(propertyName, message, timestamp)
    
                # Si no es un get, set, message o deleteProperty, se imprime el mensaje ya que no es un tipo establecido
                else:
                    print(key)

                
    # Función auxiliar que encuentra o crea un dispositivo de la conexión self con el nombre device_name
    def _get_device_or_create(self, device_name):
        # Se busca el dispositivo
        dev = self.get_client_device(device_name)
        
        # Si no existe se crea
        if dev == None:
            dev = PyndigoDevice(device_name)
            self._add_client_device(dev)
    
        return dev
            
    # Función auxiliar de conexión perdida
    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()        


    def property_has_changed(self, prop: PyndigoProperty):
        pass

    def property_has_been_deleted(self, prop: PyndigoProperty ):
        pass

    def device_message_arrived(self, device: PyndigoDevice):
        pass

    def client_message_arrived(self):
        pass

    # Función auxiliar de actualizar propiedad
    def propertyUpdate(self, prop: PyndigoProperty, itemValues: dict):
        # Se comprueba si es un string el argumento prop, si lo es
        if isinstance(prop, str):
            # Separa la cadena aux cuando encuentre un @, la primera parte es el nombre del dispositivo y la segunda la propiedad 
            aux = prop.split("@", 1)
            devName = aux[0]         # Fallará, comprobarlo bien
            propName = aux[1]

            dev = self.get_client_device(devName)
            if dev is None:
                print(f"Error: El dispositivo '{devName}' no existe.")
                return
        
            # Se obtienen la propiedad que tenga de clave propName del dispositivo devName
            prop = self.get_client_device(devName).get_property(propName)

        # si la propiedad no es de sólo lectura (por ejemplo, CCD_COOLER_POWER o mensajes INFO, son de sólo lectura)
        if (not prop.is_read_only()):
            items = []
            # Se recorre el diccionario itemValues y cada par clave-valor se añade a una lista llamada items
            for name, value in itemValues.items():
                items.append({"name": name, "value": value})

            # Se crea el diccionario propVect, que representa dispositivo, la propiedad del dispositivo y los nuevos valores para los elementos de la propiedad
            propVect = {"device" : prop.get_device().get_name(), "name": prop.get_name(), "items": items}
            # Se construye el mensaje
            message = {"new" + prop.get_type() + "Vector": propVect}

            # Se envía el mensaje al servidor
            self._writeMsg(message)
    
    # Función auxiliar para mandar el mensaje al servidor
    def _writeMsg(self, msg):
        # Si se tiene una conexión activa con el servidor
        if self._transport != None:
            # Se convierte el msg a JSON
            msgStr = json.dumps(msg) + "\n\n"
            # Se escribe el mensaje codificado en bytes en el transporte para mandarlo al servidor
            self._transport.write(msgStr.encode())
            # Se imprime el mensaje enviado
            print(" -> " + msgStr)


class MiCliente(PyndigoClient):
    def property_has_changed(self, prop: PyndigoProperty):
        print("%s has changed" % str(prop))

    def property_has_been_deleted(self, prop: PyndigoProperty ):
        print("%s has been deleted" % str(prop))

    def device_message_arrived(self, device: PyndigoDevice):
        print("%s has received a message" % str(device))

    def client_message_arrived(self):
        print("Client has received a message")

def main():
    # Se instancia un cliente, en localhost y el puerto de escucha de indigo
    client = MiCliente("Mi cliente", "127.0.0.1", 7624)
    # Se establece la conexión
    client.stablish_connection()

    time.sleep(5)
    # Se actualiza la propiedad del cliente 
    client.propertyUpdate("CCD Imager Simulator@CONNECTION", {"CONNECTED": True, "DISCONNECTED": False})

    time.sleep(10)

    print("Han pasado diez segundos")
    # Se buscan todos los dispositivos de la conexión MiCliente
    devs = client.get_devices()
    
    # Abre un archivo para escribir los dispositivos y sus propiedades
    with open("/home/Arturo4102/TFG/pyndigo/devices_info.txt", "w") as file:
        # Escribe y por cada uno se imprime el nombre, propiedades, items...
        for dn, d in devs.items():
            file.write(d.get_name() + "\n")

            props = d.get_properties()

            for pn, p in props.items():
                file.write("    " + str(p) + "\n")

                items = p.get_items()

                for inn, i in items.items():
                    file.write("        " + str(i) + "\n")

main()
