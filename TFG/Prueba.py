
# import time
from my_indigo_library.INDIGO_Client_antiguo import INDIGODevice, INDIGOProperty, INDIGOServerConnection
# #Función que se activa con el listener CONNECTED en cada device
# def connected_callback(property: INDIGO_Property):
#     # if property.getElementByName('CONNECTED').getValue() == 'On':
#     print(f"El dispositivo {property.getDevice().getName()} está conectado")


# def main():
#     host = "localhost" # Dirección del servidor
#     port = 7624 # Puerto del servidor
#     # Configuramos una conexión con el servidor INDIGO con los parámetros anteriores
#     server = INDIGO_Server("Server TFG", host, port)


    
  
#     #Iniciamos la conexión con el servidor
#     if server.connect():
#         print("Se ha establecido conexión con el servidor TFG\n")
#         # Esperar un momento para que se establezca la conexión
#         time.sleep(1)

#         devices = server.getDevices()
#         if(devices):
#             print("Los dispositivos son: \t")
#             for device_name in devices:
#                 print(device_name,"\t")
#                 device: INDIGO_Device = server.getDeviceByName(device_name)
#                 # print("Las propiedades del dispositivo son: ",device.getProperties(), "\t")
#                 # Les añadimos un Listener a cada dispositivo para el elemento CONNECTION
#                 time.sleep(1)
#                 if(device.getName().lower() == "ccd guider simulator"):
#                     server.addDevicePropertyListener(device_name, "SIMULATION", connected_callback)
#                     # print(device.getName(), " las propiedades son: ", device.getProperties())

#                     # print("\nPropiedades: ", print_parsed_properties(parse_indigo_properties(device.getProperties())), "\n")
#                     # simulation_prop: INDIGOProperty = device.getPropertyByName('SIMULATION')
#                     simulation_prop: INDIGO_Property = device.getPropertyByName('SIMULATION')
#                     # print("Propiedad Simulation valor :", simulation_prop.getAttributes())
#                     # connection_prop.sendValues({"CONNECTED": "On"}) #Cambiar entre CONNECTED y DISCONNECTED
#                     # simulation_prop.sendValues({"SIMULATION": "On"}) #Cambiar entre CONNECTED y DISCONNECTED
#                     print("Los atributos son: ", simulation_prop.getAttributes())
#                 # print(f"\nCambiado a conectado el dispositivo: {device_name}")
    
#         else:
#             print("No hay dispositivos en el servidor")
#         # Esperar un momento para que se establezca la conexión
#         time.sleep(1)
#         print("\n")
        
#         properties: INDIGO_Property = server.sendGetProperties()
#         if(properties):
#             print("Las propiedades del servidor son: \t")
#             for prop_name in properties:
#                 print(prop_name,"\t")
#         else:
#             print("No hay propiedades en el servidor")

    
#         # Esperar un momento para que se establezca la conexión
#         time.sleep(1)
#         print("Hasta aqui hemos llegado\n")
#         time.sleep(1)
#         return server.disconnect()

#     else:
#         print("Error al establecer la conexión con el servidor TFG\n")

# main()
from my_indigo_library.Cliente_INDIGO import INDIGO_Device, INDIGO_Server,INDIGO_Property
import time
#Función que se activa con el listener CONNECTED en cada device
def connected_callback(property: INDIGO_Property):
    # if property.getElementByName('CONNECTED').getValue() == 'On':
    print(f"El dispositivo {property.getDevice().getName()} está conectado")


def main():
    host = "localhost" # Dirección del servidor
    port = 7624 # Puerto del servidor
    # Configuramos una conexión con el servidor INDIGO con los parámetros anteriores
    server = INDIGO_Server("Server TFG", host, port)


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
                device: INDIGO_Device = server.getDeviceByName(device_name)
                # print("Las propiedades del dispositivo son: ",device.getProperties(), "\t")
                # Les añadimos un Listener a cada dispositivo para el elemento CONNECTION
                time.sleep(.5)
                if(device.getName().lower() == "ccd guider simulator"):
                    server.addDevicePropertyListener(device_name, "SIMULATION", connected_callback)
                    # print(device.getName(), " las propiedades son: ", device.getProperties())

                    # print("\nPropiedades: ", print_parsed_properties(parse_indigo_properties(device.getProperties())), "\n")
                    # simulation_prop: INDIGOProperty = device.getPropertyByName('SIMULATION')
                    simulation_prop: INDIGO_Property = device.getPropertyByName('SIMULATION')
                    # print("Propiedad Simulation valor :", simulation_prop.getAttributes())
                    # connection_prop.sendValues({"CONNECTED": "On"}) #Cambiar entre CONNECTED y DISCONNECTED
                    # simulation_prop.sendValues({"SIMULATION": "On"}) #Cambiar entre CONNECTED y DISCONNECTED
                    print("Los atributos son: ", simulation_prop.getAttributes())
                # print(f"\nCambiado a conectado el dispositivo: {device_name}")
    
        else:
            print("No hay dispositivos en el servidor")
        # Esperar un momento para que se establezca la conexión
        time.sleep(.5)
        print("\n")
        
        properties: INDIGO_Property = server.sendGetProperties()
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