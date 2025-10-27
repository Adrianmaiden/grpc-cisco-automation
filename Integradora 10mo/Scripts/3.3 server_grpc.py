import grpc
from concurrent import futures
import time
import cisco_network_pb2
import cisco_network_pb2_grpc

class NetworkConfigService(cisco_network_pb2_grpc.NetworkConfigServicer):
    """Implementación del servicio RPC"""

    def ConfigureInterface(self, request, context):
        print(f"🔧 Configurando interfaz {request.interface_name}")
        print(f"🧠 IP: {request.ip_address}, VLAN: {request.vlan_id}")

        # Simulación de comando en Cisco (en un entorno real se usaría SSH o API)
        try:
            # Ejemplo: enviar configuración vía subprocess o API
            print("Aplicando configuración en el dispositivo...")

            # Simulamos éxito
            return cisco_network_pb2.InterfaceResponse(
                success=True,
                message=f"Interfaz {request.interface_name} configurada correctamente con IP {request.ip_address}."
            )
        except Exception as e:
            return cisco_network_pb2.InterfaceResponse(
                success=False,
                message=f"Error al configurar interfaz: {str(e)}"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    cisco_network_pb2_grpc.add_NetworkConfigServicer_to_server(NetworkConfigService(), server)

    # Configurar TLS (usar certificados generados previamente)
    with open("certs/server-key.pem", "rb") as f:
        private_key = f.read()
    with open("certs/server-cert.pem", "rb") as f:
        certificate_chain = f.read()

    server_credentials = grpc.ssl_server_credentials(((private_key, certificate_chain,),))
    server.add_secure_port("[::]:50051", server_credentials)

    print("🚀 Servidor gRPC iniciado con TLS en el puerto 50051")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
