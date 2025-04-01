from INDIGO_Client import INDIGOServerConnection
import time
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
            for device in devices:
                print(device,"\t")
        else:
            print("No hay dispositivos en el servidor")
        # Esperar un momento para que se establezca la conexión
        time.sleep(1)
        print("\n")
        
        properties = server.sendGetProperties()
        if(properties):
            print("Las propiedades son: \t")
            for prop in properties:
                print(prop,"\t")
        else:
            print("No hay propiedades en el servidor")
        # Esperar un momento para que se establezca la conexión
        time.sleep(1)
        print("Hasta aqui hemos llegado\n")
        time.sleep(1)
        return server.disconnect()

    else:
        print("Error al establecer la conexión con el servidor TFG\n")

main()