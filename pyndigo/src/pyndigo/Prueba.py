from INDIGO_Client import INDIGOProperty, INDIGOServerConnection, INDIGODevice
import time

#Función que se activa con el listener CONNECTED en cada device
def connected_callback(property):
    # if property.getElementByName('CONNECTED').getValue() == 'On':
    print(f"El dispositivo {property.getDevice().getName()} está conectado")


#Función que parsear las propiedades
# def parse_indigo_properties(properties_dict):
#     """
#     Parsea un diccionario de propiedades INDIGO y devuelve una estructura más manejable.

#     Args:
#         properties_dict (dict): Diccionario con las propiedades INDIGO

#     Returns:
#         dict: Diccionario con información estructurada de las propiedades
#     """
    
#     parsed_properties = {}

#     # Agrupar propiedades por categorías
#     categories = {
#         'imaging': ['CCD_', 'GUIDER_'],
#         'system': ['INFO', 'SIMULATION', 'CONFIG'],
#         'connection': ['CONNECTION'],
#         'profile': ['PROFILE']
#     }

#     for prop_name, prop_obj in properties_dict.items():
#         # Determinar categoría
#         category = 'other'
#         for cat_name, prefixes in categories.items():
#             if any(prop_name.startswith(prefix) for prefix in prefixes):
#                 category = cat_name
#                 break

#         # Crear la categoría si no existe
#         if category not in parsed_properties:
#             parsed_properties[category] = {}

#         # Almacenar la propiedad con información relevante
#         parsed_properties[category][prop_name] = {
#             'name': prop_name,
#             # 'object': prop_obj,
#             # 'type': type(prop_obj).__name__
                        
#         }

#     return parsed_properties

# # Función para imprimir las propiedades parseadas
# def print_parsed_properties(parsed_props):
#     """
#     Imprime las propiedades parseadas de forma organizada.

#     Args:
#         parsed_props (dict): Diccionario con las propiedades parseadas
#     """
#     for category, properties in parsed_props.items():
#         print(f"\n=== {category.upper()} ===")
#         for prop_name in properties.items():
#             print(f"- {prop_name} \t")



def main():
    host = "localhost" # Dirección del servidor
    port = 7624 # Puerto del servidor
    # Configuramos una conexión con el servidor INDIGO con los parámetros anteriores
    server = INDIGOServerConnection("Server TFG", host, port)


    server.connect()
    # Esperar un momento para que se establezca la conexión
    time.sleep(0.5)

    #Iniciamos la conexión con el servidor
    if(server.isConnected() == True):
        print("Se ha establecido conexión con el servidor TFG\n")

        devices = server.getDevices()
        if(devices):
            print("Los dispositivos son: \t")
            for device_name in devices:
                print(device_name,"\t")
                device: INDIGODevice = server.getDeviceByName(device_name)
                # print("Las propiedades del dispositivo son: ",device.getProperties(), "\t")
                # Les añadimos un Listener a cada dispositivo para el elemento CONNECTION
                time.sleep(.5)
                if(device.getName().lower() == "ccd guider simulator"):
                    server.addPropertyListener(device_name, "SIMULATION", connected_callback)
                    print(device.getName(), " las propiedades son: ", device.getProperties())

                    # print("\nPropiedades: ", print_parsed_properties(parse_indigo_properties(device.getProperties())), "\n")
                    # simulation_prop: INDIGOProperty = device.getPropertyByName('SIMULATION')
                    simulation_prop: INDIGOProperty = device.getPropertyByName('SIMULATION')
                    print("Propiedad Simulation valor :", simulation_prop.getAttributes())
                    # connection_prop.sendValues({"CONNECTED": "On"}) #Cambiar entre CONNECTED y DISCONNECTED
                    simulation_prop.sendValues({"SIMULATION": "On"}) #Cambiar entre CONNECTED y DISCONNECTED
                        
                # print(f"\nCambiado a conectado el dispositivo: {device_name}")
    
        else:
            print("No hay dispositivos en el servidor")
        # Esperar un momento para que se establezca la conexión
        time.sleep(.5)
        print("\n")
        
        properties: INDIGOProperty = server.sendGetProperties()
        if(properties):
            print("Las propiedades del servidor son: \t")
            for prop_name in properties:
                print(prop_name,"\t")
        else:
            print("No hay propiedades en el servidor")

    
        # Esperar un momento para que se establezca la conexión
        time.sleep(.5)
        print("Hasta aqui hemos llegado\n")
        time.sleep(.5)
        return server.disconnect()

    else:
        print("Error al establecer la conexión con el servidor TFG\n")

main()