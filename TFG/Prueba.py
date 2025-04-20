from my_indigo_library.Cliente_INDIGO import INDIGO_Device, INDIGO_Server, INDIGO_Property
import time
import sys
import datetime

# Función que se activa con el listener CONNECTED en cada device
def connected_callback(property: INDIGO_Property):
    print(f"El dispositivo {property.getDevice().getName()} está conectado")

def message_Action():
    print(f"Se ha realizado una acción en el servidor")

def main():
    host = "localhost"  # Dirección del servidor
    port = 7624         # Puerto del servidor
    # Configuramos una conexión con el servidor INDIGO con los parámetros anteriores
    server = INDIGO_Server("Server TFG", host, port)
    server.connect()
    # Esperar un momento para que se establezca la conexión
    time.sleep(.5)

    # Iniciamos la conexión con el servidor
    if server.isConnected():
        print(f"Se ha establecido conexión con el servidor {server.getName()}\n")
        server.addServerListener(message_Action)
        devices = server.getDevices()
        if devices:
            print("Los dispositivos son: ")
            for device_name in devices:
                print("     ", device_name)
                device: INDIGO_Device = server.getDeviceByName(device_name)

                # Les añadimos un Listener a cada dispositivo para el elemento CONNECTION
                if device.getName().lower() == "ccd guider simulator":
                    print(f"\tProbando DEVICE:\n\tEl nombre es: {device.getName()}")
                    print(f"\tEl servidor es: {device.getServerStr()}")
                    print(f"\tLas propiedades son: {device.getProperties()}")

                    # server.addDevicePropertyListener(device_name, "CONNECTION", connected_callback)
                    # simulation_prop: INDIGO_Property = server.getPropOfDevice(device_name, 'INFO') or None
                    # if simulation_prop is not None:
                    #     print(f"\tProbando PROPIEDADES:\n\tEl device es: {simulation_prop.getDevice().getName()}")
                    #     print(f"\tLos elementos son: {simulation_prop.getElements()}")
                    #     print(f"\tEl nombre es: {simulation_prop.getName()}")
                    #     print(f"\tLos atributos son: {simulation_prop.getAttributes()}")
                    #     print(f"\tEl tipo es: {simulation_prop.getType()}")
                    #     for elem in simulation_prop.getElements():
                    #         print(f"\tProbando ELEMENTOS:")
                    #         print(f"\tEl nombre es: {elem.getName()}")
                    #         print(f"\tEl valor es: {elem.getValue()}")
                    #         print(f"\tLos atributos son: {elem.getAttributes()}")

        else:
            print("No hay dispositivos en el servidor")
        # Esperar un momento para que se establezca la conexión
        time.sleep(.5)
        print("\n")

        properties = server.sendGetProperties()
        if properties:
            print("Las propiedades del servidor son: ")
            for prop_name in properties:
                print(prop_name)
        else:
            print("No hay propiedades en el servidor")

        # Esperar un momento para que se establezca la conexión
        time.sleep(.5)
        print("Hasta aqui hemos llegado\n")
        time.sleep(.5)
        return server.disconnect()

    else:
        print("Error al establecer la conexión con el servidor TFG\n")

if __name__ == "__main__":
    # Crear el nombre del archivo con la fecha y hora actual
    fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"log_indigo_{fecha_actual}.txt"

    # Guardar la referencia original de stdout
    stdout_original = sys.stdout

    try:
        # Abrir el archivo y redirigir stdout
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            sys.stdout = f
            main()
    finally:
        # Restaurar stdout a su valor original
        sys.stdout = stdout_original