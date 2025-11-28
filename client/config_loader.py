import json
import sys
import os
from typing import Dict, Any

# --- AJUSTE 1: Truco para encontrar la carpeta 'protos' ---
# Esto permite importar los archivos generados aunque estén en otra carpeta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ----------------------------------------------------------

# Importar los mensajes de Protocol Buffers generados desde el .proto
import protos.network_manager_pb2 as network_pb2

class ConfigManager:
    """
    Gestiona la carga y transformación de archivos de configuración JSON
    a mensajes de Protocol Buffers para gRPC.
    """

    def load_config_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Carga un archivo de configuración JSON desde la ruta especificada.
        """
        print(f"📂 Cargando configuración desde '{file_path}'...")
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: El archivo de configuración '{file_path}' no fue encontrado.")
            raise
        except json.JSONDecodeError:
            print(f"❌ Error: El archivo '{file_path}' no contiene un JSON válido.")
            raise

    def create_interface_request(self, config_data: Dict[str, Any]) -> network_pb2.InterfaceConfigRequest:
        """
        Transforma un diccionario de configuración a un mensaje gRPC InterfaceConfigRequest.
        """
        print("⚙️  Transformando datos de JSON a mensaje Protobuf...")

        # Crea el mensaje de petición principal
        request_proto = network_pb2.InterfaceConfigRequest()

        # Itera sobre la lista de interfaces en el JSON
        for if_config in config_data.get('interfaces', []):
            # Crea un mensaje InterfaceConfig para cada interfaz y lo añade a la lista
            interface_proto = request_proto.interfaces.add()
            interface_proto.name = if_config.get('name', '')
            interface_proto.description = if_config.get('description', '')
            interface_proto.ip_address = if_config.get('ip_address', '')
            # Nota: vlan_id y enabled deben coincidir con los tipos del .proto
            interface_proto.enabled = if_config.get('enabled', True)

        print(f"✅ Mensaje Protobuf creado con {len(request_proto.interfaces)} configuraciones de interfaz.")
        return request_proto

# --- AJUSTE 2: Bloque de prueba para ejecutarlo ahora mismo ---
if __name__ == "__main__":
    try:
        # Instanciamos la clase
        manager = ConfigManager()
        
        # Ruta al archivo JSON que creamos en el paso anterior
        test_file = "configs/interfaces.json"
        
        # Probamos los dos métodos
        data = manager.load_config_from_file(test_file)
        mensaje_proto = manager.create_interface_request(data)
        
        print("\n--- Resultado de la Conversión ---")
        print(mensaje_proto)
        print("----------------------------------")
        
    except Exception as e:
        print(f"Prueba fallida: {e}")