#!/usr/bin/env python3
import grpc
from cisco_gnmi.proto import gnmi_pb2, gnmi_pb2_grpc

def main():
    """
    Cliente gNMI 'Hola Mundo' - Check de Capacidades.
    Esta es la prueba estándar para validar la conexión sin depender de rutas YANG específicas.
    """
    target = "192.168.56.10:50051"
    
    certs_path = "certs/"
    ca_cert_path = certs_path + "ca-cert.pem"
    client_key_path = certs_path + "client-key.pem"
    client_cert_path = certs_path + "client-cert.pem"

    print(f" Iniciando conexión gRPC Segura hacia {target}...")

    try:
        # 1. Cargar certificados
        with open(ca_cert_path, 'rb') as f: ca_cert = f.read()
        with open(client_key_path, 'rb') as f: client_key = f.read()
        with open(client_cert_path, 'rb') as f: client_cert = f.read()

        # 2. Credenciales SSL
        creds = grpc.ssl_channel_credentials(
            root_certificates=ca_cert,
            private_key=client_key,
            certificate_chain=client_cert
        )
        channel = grpc.secure_channel(target, creds)
        stub = gnmi_pb2_grpc.gNMIStub(channel)

        # 3. Autenticación (Usuario/Pass)
        auth_metadata = [
            ('username', 'admin'),
            ('password', 'Cisco123')
        ]

        # 4. EJECUTAR LA PRUEBA MAESTRA: Capabilities
        # Este método no requiere rutas ni namespaces, solo autenticación válida.
        print("  > Enviando saludo (Capabilities Request)...")
        request = gnmi_pb2.CapabilityRequest()
        response = stub.Capabilities(request, metadata=auth_metadata)

        # 5. Resultado
        print("\n" + "="*40)
        print("  ✅ ¡CONEXIÓN mTLS EXITOSA! ✅")
        print("="*40)
        print(f"  Datos del Switch:\n{response}")
        print("="*40 + "\n")

    except grpc.RpcError as e:
        print(f"\n❌ Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    main()