from INDIGO_Client import INDIGOServerConnection
import time

def connected_callback(property):
    if property.getElementByName('CONNECTED').getValue() == 'On':
        print(f"El dispositivo {property.getDevice().getName()} está conectado")

def main():
    # Crear la conexión al servidor
    host = "localhost"  # o tu IP específica
    port = 7624
    
    # Crear la conexión
    server = INDIGOServerConnection("Server", host, port)
    
    # Conectar al servidor
    print("Conectando al servidor...")
    server.connect()
    
    # Esperar un momento para que se establezca la conexión
    time.sleep(1)
    
    # Obtener los dispositivos
    devices = server.getDevices()
    
    if not devices:
        print("No se encontraron dispositivos")
        server.disconnect()
        return
    
    # Imprimir los dispositivos encontrados
    print("\nDispositivos encontrados:")
    for device_name in devices:
        print(f"- {device_name}")
        
        # Agregar listener para la propiedad CONNECTION
        server.addPropertyListener(device_name, 'CONNECTION', connected_callback)
    
    # Intentar conectar el primer dispositivo
    first_device = list(devices.values())[0]
    print(f"\nIntentando conectar el dispositivo: {first_device.getName()}")
    
    # Buscar y activar la propiedad CONNECTION si existe
    if 'CONNECTION' in first_device.getProperties():
        connection_prop = first_device.getPropertyByName('CONNECTION')
        connection_prop.sendValues({"CONNECTED": "On"})
        print(f"\nCambiado a conectado el dispositivo: {first_device.getName()}")
    
    # Esperar un momento para ver los resultados
    time.sleep(2)
    
    # Desconectar
    print("\nDesconectando del servidor...")
    server.disconnect()

if __name__ == "__main__":
    main()
    
    # import INDIGO_Client
# from INDIGO_Client import INDIGOServerConnection
# import time

# def connected(property):
#     if property.getElementByName('CONNECTED').getValue() == 'On':
#         print("The device " + str(property.getDevice().getName()) + " is connected")

# host = "172.30.124.160"  # Dirección IP del servidor
# port = 7624  # Puerto del servidor INDIGO

# serverConnection = INDIGOServerConnection("Server", host, port)
# serverConnection.connect()

# time.sleep(0.5)

# devices = []
# for deviceName, device in serverConnection.getDevices().items():
#     serverConnection.addPropertyListener(deviceName, 'CONNECTION', connected)
#     devices.append(device)
# <
# if 'CONNECTION' in devices[0].getProperties():
#     devices[0].getPropertyByName('CONNECTION').sendValues({"CONNECTED": "On"})
# elif len(devices) > 1 and 'CONNECTION' in devices[1].getProperties():
#     devices[1].getPropertyByName('CONNECTION').sendValues({"CONNECTED": "On"})

# time.sleep(0.5)
# serverConnection.enableBLOB()

# if 'CCD_IMAGE' in devices[0].getProperties():
#     serverConnection.sendBLOBMessage(devices[0].name, 'CCD_IMAGE')
# else:
#     print("Warning: Property 'CCD_IMAGE' not found for the first device.")

# if 'CCD_EXPOSURE' in devices[0].getProperties():
#     devices[0].getPropertyByName('CCD_EXPOSURE').sendValues({"EXPOSURE": "2"})
#     time.sleep(2.5)
# else:
#     print("Warning: Property 'CCD_EXPOSURE' not found for the first device.")

# if 'CCD_IMAGE' in devices[0].getProperties():
#     devices[0].getPropertyByName('CCD_IMAGE').sendValues({
#         "IMAGE": str(devices[0].getPropertyByName('CCD_IMAGE').getElementByName('IMAGE').getPath())
#     })
# else:
#     print("Warning: Property 'CCD_IMAGE' not found for the first device.")

# devices[0].getPropertyByName('CONNECTION').sendValues({"DISCONNECTED": "On"})
# serverConnection.disconnect()