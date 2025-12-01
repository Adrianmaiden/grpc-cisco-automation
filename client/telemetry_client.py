import grpc
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from protos import network_manager_pb2, network_manager_pb2_grpc

def run_telemetry_client(target):
    # 1. Credenciales
    certs_path = "certs/"
    with open(certs_path + "ca-cert.pem", 'rb') as f: ca_cert = f.read()
    with open(certs_path + "client-key.pem", 'rb') as f: client_key = f.read()
    with open(certs_path + "client-cert.pem", 'rb') as f: client_cert = f.read()

    creds = grpc.ssl_channel_credentials(ca_cert, client_key, client_cert)
    
    # 2. Conexión
    print(f"📡 Conectando a {target} para recibir telemetría...")
    channel = grpc.secure_channel(target, creds)
    stub = network_manager_pb2_grpc.NetworkManagerStub(channel)

    # 3. Solicitud de Streaming
    request = network_manager_pb2.TelemetryRequest(sensor_path="sys/resources")
    
    try:
        # Esto devuelve un iterador (un stream)
        stream = stub.GetTelemetry(request)
        
        print("📊 Esperando datos en tiempo real (Ctrl+C para salir)...\n")
        print(f"{'TIMESTAMP':<10} | {'METRIC':<15} | {'VALUE'}")
        print("-" * 40)

        # 4. Bucle infinito recibiendo datos
        for data in stream:
            # Determinamos cuál de los valores 'oneof' viene lleno
            valor = "N/A"
            if data.HasField("double_val"):
                valor = f"{data.double_val:.2f}"
            elif data.HasField("int_val"):
                valor = f"{data.int_val}"
            elif data.HasField("string_val"):
                valor = data.string_val
            
            print(f"{data.timestamp:<10} | {data.key:<15} | {valor}")

    except grpc.RpcError as e:
        print(f"❌ Error gRPC: {e.code()}")
    except KeyboardInterrupt:
        print("\n👋 Deteniendo cliente.")

if __name__ == "__main__":
    run_telemetry_client("localhost:50051")