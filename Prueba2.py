import socket
import json
import time

host = "localhost"  # Dirección del servidor
port = 7624         # Puerto del servidor
response = b""      # Inicializa la variable de respuesta como un byte vacío

# Mensaje de conexión para "CCD Imager Simulator"
connection_message = {
    "type": "property",
    "device": "CCD Imager Simulator",
    "name": "CONNECTION",
    "state": "Idle",
    "items": [
        {"name": "CONNECTED", "value": True}
    ]
}

# Mensaje de consulta para "CCD Imager Simulator"
info_message = {
  "getProperties": {
    "device": "Server",
    "name": "BLOB_BUFFERING"
  }
}


# Mensaje para actualizar coordenadas en "Mount Agent"
coordinate_update_message = {
    "setSwitchVector": {
        "device": "Server",
        "name": "BLOB_BUFFERING",
        "items": [
            {"name": "DISABLED", "value": False},
            {"name": "ENABLED", "value": True},
            {"name": "COMPRESSION", "value": False}
        ]
    }
}

coordinate_update_message2 = {
  "setNumberVector": {
    "device": "Mount Agent",
    "name": "GEOGRAPHIC_COORDINATES",
    "state": "Ok",
    "items": [
      {"name": "LATITUDE", "value": 30},
      {"name": "LONGITUDE", "value": -10},
      {"name": "ELEVATION", "value": 0}
    ]
  }
}


# Comprobar las características para ver si se han actualizado
status_request_message = {
    "type": "getProperties",
    "device": "Mount Agent",
    "name": "GEOGRAPHIC_COORDINATES"
}

# Función para enviar un mensaje por el socket
def send_message(s, message):
    json_msg = json.dumps(message)
    s.sendall(json_msg.encode("utf-8"))

# Función para parsear una cadena de datos JSON y devolver los objetos encontrados
def parse_json_stream(data):
    decoder = json.JSONDecoder()
    idx = 0
    length = len(data)
    while idx < length:
        try:
            obj, idx_next = decoder.raw_decode(data, idx)
            yield obj
            idx = idx_next
        except json.JSONDecodeError:
            idx += 1

try:
    # Conectar al servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Conectado al servidor {host}:{port}")

        # Envía el comando de conexión
        send_message(s, connection_message)
        print("Comando de conexión enviado.")
        time.sleep(1)  # Espera para que el servidor procese el comando

        # Envía la consulta de estado
        #send_message(s, info_message)
        #print("Comando de consulta enviado.")
        #time.sleep(1)  # Espera para que el servidor procese la consulta

        # Envía el comando para actualizar las coordenadas del Mount Agent
        send_message(s, coordinate_update_message)
        print("Comando de actualización de coordenadas enviado.")
        time.sleep(1)  # Espera para que el servidor procese la actualización
        
        # Envía el comando para actualizar las coordenadas del Mount Agent
        send_message(s, coordinate_update_message2)
        print("Comando de actualización de parámetros enviado.")
        time.sleep(1)  # Espera para que el servidor procese la actualización
        
        send_message(s, status_request_message)
        print("Comando para ver la actualización enviado.")
        time.sleep(1)  # Espera para que el servidor procese la actualización
        
        # Configura un timeout para recibir la respuesta
        s.settimeout(5)
        
        # Recibe la respuesta del servidor
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break

    if response:
        response_str = response.decode("utf-8")
        for response_json in parse_json_stream(response_str):
            print("Respuesta del servidor (JSON):", response_json)
    else:
        print("No se recibió respuesta del servidor.")

except ConnectionRefusedError:
    print("No se pudo conectar al servidor. ¿Está ejecutándose en el puerto especificado?")
except Exception as e:
    print("Error al conectar con el servidor:", e)
