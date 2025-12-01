import grpc
from concurrent import futures
import time
import sys
import os
import random
from datetime import datetime

# Ajuste de path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- IMPORTAMOS LOS DOS PROTOCOLOS ---
# 1. NetworkManager (Para Telemetría - Lo que tú diseñaste)
from protos import network_manager_pb2, network_manager_pb2_grpc
# 2. Cisco GRPC (Para Configuración - Lo que el switch habla)
from protos import cisco_pb2, cisco_pb2_grpc

# --- SERVICIO 1: TELEMETRÍA (Tu diseño) ---
class NetworkManager(network_manager_pb2_grpc.NetworkManagerServicer):
    def GetTelemetry(self, request, context):
        sensor = request.sensor_path
        # print(f"📊 [MOCK] Cliente suscrito a telemetría: {sensor}")
        
        try:
            while context.is_active():
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Enviamos datos aleatorios simulando el switch
                yield network_manager_pb2.TelemetryData(
                    sensor_path=sensor, timestamp=timestamp, 
                    key="cpu_usage", double_val=random.uniform(10.5, 45.0))
                
                yield network_manager_pb2.TelemetryData(
                    sensor_path=sensor, timestamp=timestamp, 
                    key="memory_free", int_val=random.randint(2048, 4096))
                
                yield network_manager_pb2.TelemetryData(
                    sensor_path=sensor, timestamp=timestamp, 
                    key="eth1_1_traffic", double_val=random.uniform(100.0, 500.0))
                
                time.sleep(2)
        except Exception:
            pass

# --- SERVICIO 2: CONFIGURACIÓN CISCO (Simulación CLI) ---
class CiscoConfig(cisco_pb2_grpc.gRPCConfigOperServicer):
    def Config(self, request, context):
        print(f"\n🔧 [MOCK CISCO] ¡Comando de configuración recibido!")
        print(f"   📜 Payload:\n{request.cli}")
        
        # Simulamos la respuesta típica de un Switch Cisco
        fake_output = f"""
configure terminal
{request.cli}
Copy complete, now saving to disk (startup-config)
"""
        # Devolvemos éxito
        return cisco_pb2.ConfigReply(
            reqID=request.reqID,
            output=fake_output,
            errors=""
        )

def serve():
    # Cargar certificados
    server_key = open('certs/server-key.pem', 'rb').read()
    server_cert = open('certs/server-cert.pem', 'rb').read()
    ca_cert = open('certs/ca-cert.pem', 'rb').read()

    creds = grpc.ssl_server_credentials(
        [(server_key, server_cert)], 
        root_certificates=ca_cert, 
        require_client_auth=True
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # --- REGISTRAMOS AMBOS SERVICIOS ---
    network_manager_pb2_grpc.add_NetworkManagerServicer_to_server(NetworkManager(), server)
    cisco_pb2_grpc.add_gRPCConfigOperServicer_to_server(CiscoConfig(), server)
    # -----------------------------------
    
    server.add_secure_port('[::]:50051', creds)
    
    print("🚀 Mock Server Híbrido (Telemetría + CLI) escuchando en puerto 50051...")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
