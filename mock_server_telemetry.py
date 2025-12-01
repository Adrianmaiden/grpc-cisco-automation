import grpc
from concurrent import futures
import time
import sys
import os
import random
from datetime import datetime

# Ajuste de path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from protos import network_manager_pb2, network_manager_pb2_grpc

class NetworkManager(network_manager_pb2_grpc.NetworkManagerServicer):
    """
    Simula ser el Switch recibiendo configuración y enviando telemetría.
    """
    
    # --- FUNCIONALIDAD DE CONFIGURACIÓN (FASE 3) ---
    def ConfigureInterfaces(self, request, context):
        print(f"\n🔔 [CONFIG] ¡Petición recibida!")
        print(f"   -> Interfaces a configurar: {len(request.interfaces)}")
        for iface in request.interfaces:
            status = "HABILITADA" if iface.enabled else "DESHABILITADA"
            print(f"      - Configurando {iface.name} ({iface.ip_address}) -> Estado: {status}")
        
        return network_manager_pb2.ConfigResponse(
            success=True,
            message="Configuración aplicada exitosamente en el mock."
        )

    # --- FUNCIONALIDAD DE TELEMETRÍA (FASE 4) ---
    def GetTelemetry(self, request, context):
        sensor = request.sensor_path
        print(f"\n📊 [TELEMETRÍA] Cliente suscrito a: {sensor}")
        print("   -> Iniciando stream de datos...")

        try:
            # Simulamos un stream infinito
            while context.is_active():
                # Generamos datos aleatorios realistas
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Dato 1: Uso de CPU
                yield network_manager_pb2.TelemetryData(
                    sensor_path=sensor,
                    timestamp=timestamp,
                    key="cpu_usage",
                    double_val=random.uniform(10.5, 45.0) # Simula CPU entre 10% y 45%
                )

                # Dato 2: Memoria Libre (en MB)
                yield network_manager_pb2.TelemetryData(
                    sensor_path=sensor,
                    timestamp=timestamp,
                    key="memory_free",
                    int_val=random.randint(2048, 4096)
                )

                # Dato 3: Tráfico de Interfaz (Simulado)
                yield network_manager_pb2.TelemetryData(
                    sensor_path=sensor,
                    timestamp=timestamp,
                    key="eth1_1_traffic",
                    double_val=random.uniform(100.0, 500.0) # Kbps
                )

                # Esperamos 2 segundos antes del siguiente envío
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error en stream: {e}")
        finally:
            print("   -> Stream finalizado.")

def serve():
    server_key = open('certs/server-key.pem', 'rb').read()
    server_cert = open('certs/server-cert.pem', 'rb').read()
    ca_cert = open('certs/ca-cert.pem', 'rb').read()

    creds = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=True
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    network_manager_pb2_grpc.add_NetworkManagerServicer_to_server(NetworkManager(), server)
    
    server.add_secure_port('[::]:50051', creds)
    
    print("🚀 Servidor Mock v2.0 (con Telemetría) escuchando en 50051...")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()