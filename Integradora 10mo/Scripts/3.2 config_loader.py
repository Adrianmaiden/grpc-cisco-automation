# Archivo: client/config_loader.py
import json
from typing import Dict, Any

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

        Args:
            file_path: La ruta al archivo .json.

        Returns:
            Un diccionario de Python con los datos de configuración.

        Raises:
            FileNotFoundError: Si el archivo no se encuentra.
            json.JSONDecodeError: Si el archivo no es un JSON válido.
        """
        print(f" Cargando configuración desde '{file_path}'...")
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: El archivo de configuración '{file_path}' no fue encontrado.")
            raise
        except json.JSONDecodeError:
            print(f"Error: El archivo '{file_path}' no contiene un JSON válido.")
            raise

    def create_interface_request(self, config_data: Dict[str, Any]) -> network_pb2.InterfaceConfigRequest:
        """
        Transforma un diccionario de configuración a un mensaje gRPC InterfaceConfigRequest.

        Args:
            config_data: El diccionario cargado desde el archivo JSON.

        Returns:
            Un objeto InterfaceConfigRequest listo para ser enviado por gRPC.
        """
        print(" Transformando datos de JSON a mensaje Protobuf...")

        # Crea el mensaje de petición principal
        request_proto = network_pb2.InterfaceConfigRequest()

        # Itera sobre la lista de interfaces en el JSON
        for if_config in config_data.get('interfaces', []):
            # Crea un mensaje InterfaceConfig para cada interfaz y lo añade a la lista
            interface_proto = request_proto.interfaces.add()
            interface_proto.name = if_config.get('name', '')
            interface_proto.description = if_config.get('description', '')
            interface_proto.ip_address = if_config.get('ip_address', '')
            interface_proto.vlan_id = if_config.get('vlan_id', 1)
            interface_proto.enabled = if_config.get('enabled', True)

        print(f" Mensaje Protobuf creado con {len(request_proto.interfaces)} configuraciones de interfaz.")
        return request_proto
