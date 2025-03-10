# import socket
# import json
# import time

# host = "localhost" # Dirección del servidor
# port = 7624 # Puerto del servidor
# response = b"" # Inicializa la variable de respuesta como un byte vacío

# # Mensaje de conexión
# connection_message = {
#     "type": "property",
#     "device": "CCD Imager Simulator",
#     "name": "CONNECTION",
#     "state": "Idle",
#     "items": [
#         {"name": "CONNECTED", "value": True}
#     ]
# }

# # Mensaje de consulta
# info_message = {
#     "type": "property",
#     "device": "CCD Imager Simulator",
#     "name": "INFO",
#     "state": "Ok"
# }

# # Envía un mensaje al socket
# def send_message(s, message):
#     # Convierte el mensaje a JSON y lo envía al socket
#     json_msg = json.dumps(message)
#     # Envía el mensaje JSON al socket
#     s.sendall(json_msg.encode("utf-8"))

# #Toma una cadena de datos JSON y devuelve un generador que produce objetos JSON uno por uno
# def parse_json_stream(data):
#     decoder = json.JSONDecoder() # Crea un decodificador JSON
#     idx = 0 # Indice para rastrear la posición actual
#     length = len(data) # Longitud de la cadena de datos
    
#     while idx < length: # Mientras no se haya alcanzado el final de la cadena
#         # Intenta decodificar un objeto JSON
#         try:
#             obj, idx_next = decoder.raw_decode(data, idx) # Decodifica el objeto JSON
#             yield obj # Devuelve el objeto decodificado
#             idx = idx_next # Actualiza el índice a la posición siguiente
#         except json.JSONDecodeError:
#             idx += 1  # Si hay un error de decodificación, avanza un carácter

# try: 
#     # Conexión al servidor
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((host, port)) 
#         print(f"Conectado al servidor {host}:{port}")

#         # Envía el comando de conexión
#         send_message(s, connection_message)
#         print("Comando de conexión enviado.")

#         # Esperar un momento para que el servidor procese el cambio
#         time.sleep(1)

#         # Envía una consulta de estado
#         send_message(s, info_message)
#         print("Comando de consulta enviado.")

#         # Configura un timeout para recibir la respuesta
#         s.settimeout(5)

#         # Recibe la respuesta del servidor
#         while True:
#             try:
#                 # Recibe datos en bloques
#                 chunk = s.recv(4096)
#                 if not chunk: # Si no hay más datos, salir del bucle
#                     break
#                 response += chunk # Agrega el bloque recibido a la respuesta

#             except socket.timeout: # Si se alcanza el tiempo de espera, salir del bucle
#                 break

#     if response:
#         # Decodifica la respuesta en UTF-8
#         response_str = response.decode("utf-8")
#         for response_json in parse_json_stream(response_str): # Analiza la respuesta JSON
#             print("Respuesta del servidor (JSON):", response_json, "\t")
#     else:
#         print("No se recibió respuesta del servidor.")

# except ConnectionRefusedError: # Error de conexión
#     print("No se pudo conectar al servidor. ¿Está ejecutándose en el puerto especificado?")
# except Exception as e: # Manejo de excepciones
#     print("Error al conectar con el servidor:", e)

from pyindi.client import IndiClient

# Crear una instancia del cliente INDI
client = IndiClient()

# Conectar al servidor INDI en localhost:7624
server_host = "localhost"
server_port = 7624

try:
    client.connect(server_host, server_port)
    print(f"Conectado al servidor INDI en {server_host}:{server_port}")

    # Listar los dispositivos disponibles
    devices = client.get_devices()
    print("Dispositivos disponibles:")
    for device in devices:
        print(f"- {device}")

    # Seleccionar el simulador de cámara CCD
    ccd_device = "CCD Simulator"
    if ccd_device in devices:
        print(f"Conectando al dispositivo: {ccd_device}")
        client.set_device(ccd_device)

        # Obtener propiedades del dispositivo
        properties = client.get_properties(ccd_device)
        print(f"Propiedades del dispositivo {ccd_device}:")
        for prop in properties:
            print(f"- {prop}")

        # Ejemplo: Configurar una exposición de 5 segundos
        exposure_property = "CCD_EXPOSURE"
        if exposure_property in properties:
            print(f"Configurando exposición a 5 segundos en {ccd_device}")
            client.set_property(ccd_device, exposure_property, {"EXPOSURE": 5.0})
        else:
            print(f"Propiedad {exposure_property} no encontrada en {ccd_device}")
    else:
        print(f"Dispositivo {ccd_device} no encontrado.")
except Exception as e:
    print(f"Error al conectar al servidor INDI: {e}")
finally:
    # Desconectar del servidor
    client.disconnect()
    print("Desconectado del servidor INDI.")