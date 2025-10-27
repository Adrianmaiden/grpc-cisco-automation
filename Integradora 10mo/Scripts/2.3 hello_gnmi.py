#!/usr/bin/env python3
import grpc
from cisco_gnmi import ClientBuilder

def main():
    """
    Cliente gNMI 'Hola Mundo' para verificar la conexión mTLS con un switch Cisco NX-OS.
    Solicita el hostname del dispositivo.
    """
    target_address = "192.168.56.10:50051"

    # Rutas a los certificados generados en la fase 2.1
    certs_path = "certs/"
    ca_cert_path = certs_path + "ca-cert.pem"
    client_key_path = certs_path + "client-key.pem"
    client_cert_path = certs_path + "client-cert.pem"

    print(f" Iniciando conexión gNMI 'Hola Mundo' hacia {target_address}...")

    try:
        # 1. Cargar los certificados desde los archivos .pem
        print("  > Cargando credenciales mTLS...")
        with open(ca_cert_path, 'rb') as f:
            ca_cert = f.read()
        with open(client_key_path, 'rb') as f:
            client_key = f.read()
        with open(client_cert_path, 'rb') as f:
            client_cert = f.read()

        # 2. Construir el cliente gNMI con las credenciales mTLS
        builder = ClientBuilder(target_address)
        builder.with_secure_target(
            root_certificates=ca_cert,
            private_key=client_key,
            certificate_chain=client_cert
        )
        client = builder.construct()

        # 3. Realizar una petición gNMI Get para el hostname
        # La ruta YANG para el hostname en NX-OS es "sys/sys-info/ch_id"
        gnmi_path = "sys/sys-info/ch_id"
        print(f"  > Solicitando hostname con la ruta YANG: '{gnmi_path}'...")

        response = client.get_xpaths(gnmi_path)

        # 4. Procesar y mostrar la respuesta
        hostname = response.notification[0].update[0].val.string_val
        print("\n" + "="*40)
        print("  CONEXIÓN mTLS EXITOSA ")
        print("="*40)
        print(f"  Hostname recibido del switch: {hostname}")
        print("="*40 + "\n")

    except grpc.RpcError as e:
        print("\n" + "!"*40)
        print("  ERROR: No se pudo establecer la conexión gRPC.")
        print("!"*40)
        print(f"  Código de error: {e.code()}")
        print(f"  Detalles: {e.details()}")
        print("\n  Posibles causas:")
        print("  - El agente gRPC no está habilitado en el switch.")
        print("  - Hay un problema de red (firewall, IP incorrecta).")
        print("  - Los certificados no están configurados correctamente en el switch.")
        print("  - La CA no es de confianza en el switch (revisar el trustpoint).")
        print("!"*40 + "\n")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()
