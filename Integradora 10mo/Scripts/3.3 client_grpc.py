import grpc
import cisco_network_pb2
import cisco_network_pb2_grpc

def run():
    with open("certs/ca-cert.pem", "rb") as f:
        trusted_certs = f.read()
    with open("certs/client-cert.pem", "rb") as f:
        client_cert = f.read()
    with open("certs/client-key.pem", "rb") as f:
        client_key = f.read()

    creds = grpc.ssl_channel_credentials(
        root_certificates=trusted_certs,
        private_key=client_key,
        certificate_chain=client_cert
    )

    with grpc.secure_channel("localhost:50051", creds) as channel:
        stub = cisco_network_pb2_grpc.NetworkConfigStub(channel)
        response = stub.ConfigureInterface(
            cisco_network_pb2.InterfaceRequest(
                interface_name="GigabitEthernet1/0/1",
                ip_address="192.168.10.1/24",
                vlan_id=100
            )
        )
        print(f"🛰️ Respuesta del servidor: {response.message}")

if __name__ == "__main__":
    run()
