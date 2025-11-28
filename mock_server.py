import grpc
from concurrent import futures
import time
import sys
import os

# Ajuste de path para encontrar los protos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from protos import network_manager_pb2, network_manager_pb2_grpc

class NetworkManager(network_manager_pb2_grpc.NetworkManagerServicer):
    """
    Simula ser el Switch recibiendo la configuración.
    """
    def ConfigureInterfaces(self, request, context):
        print(f"\n🔔 [SERVIDOR] ¡Petición recibida!")
        print(f"   -> Interfaces a configurar: {len(request.interfaces)}")
        
        # Simulamos procesar cada interfaz
        for iface in request.interfaces:
            status = "HABILITADA" if iface.enabled else "DESHABILITADA"
            print(f"      - Configurando {iface.name} ({iface.ip_address}) -> Estado: {status}")
        
        print("   ✅ Configuración aplicada exitosamente en el Mock.\n")
        
        # Respondemos al cliente
        return network_manager_pb2.ConfigResponse(
            success=True,
            message="Configuración aplicada exitosamente en el mock."
        )

def serve():
    # Usamos las mismas credenciales del servidor que generamos para el switch
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
    
    # Escuchamos en el puerto 50051 de la máquina local
    server.add_secure_port('[::]:50051', creds)
    
    print("🚀 Servidor Mock NetworkManager escuchando en puerto 50051...")
    print("   (Presiona Ctrl+C para detener)")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()