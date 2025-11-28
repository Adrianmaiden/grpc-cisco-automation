import grpc
import sys
import os
import argparse

# Ajuste de path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protos import network_manager_pb2_grpc
from client.config_loader import ConfigManager

def run_client(config_file, target):
    # 1. Cargar la configuración desde JSON
    loader = ConfigManager()
    print(f"📖 Leyendo configuración de: {config_file}")
    request_msg = loader.load_config_from_file(config_file)
    proto_msg = loader.create_interface_request(request_msg)

    if not proto_msg:
        print("❌ No hay configuración para enviar.")
        return

    # 2. Cargar credenciales mTLS
    print("🔐 Cargando certificados...")
    certs_path = "certs/"
    with open(certs_path + "ca-cert.pem", 'rb') as f: ca_cert = f.read()
    with open(certs_path + "client-key.pem", 'rb') as f: client_key = f.read()
    with open(certs_path + "client-cert.pem", 'rb') as f: client_cert = f.read()

    creds = grpc.ssl_channel_credentials(
        root_certificates=ca_cert,
        private_key=client_key,
        certificate_chain=client_cert
    )

    # 3. Conectar al Servidor
    print(f"📡 Conectando a {target}...")
    # options=(('grpc.ssl_target_name_override', 'server'),) es vital para pruebas locales
    # porque el certificado dice "server" pero nos conectamos a "localhost"
    channel = grpc.secure_channel(target, creds)
    stub = network_manager_pb2_grpc.NetworkManagerStub(channel)

    # 4. Enviar RPC
    print("🚀 Enviando RPC 'ConfigureInterfaces'...")
    try:
        response = stub.ConfigureInterfaces(proto_msg)
        
        print("\n" + "="*40)
        if response.success:
            print("✅ ÉXITO DEL SERVIDOR:")
        else:
            print("❌ ERROR DEL SERVIDOR:")
        print(f"   Mensaje: {response.message}")
        print("="*40 + "\n")
        
    except grpc.RpcError as e:
        print(f"❌ Error gRPC: {e.code()} - {e.details()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/interfaces.json", help="Archivo JSON")
    parser.add_argument("--target", default="localhost:50051", help="IP:Puerto del servidor")
    args = parser.parse_args()

    run_client(args.config, args.target)