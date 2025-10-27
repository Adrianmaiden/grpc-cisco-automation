import grpc
import time
import cisco_telemetry_pb2
import cisco_telemetry_pb2_grpc

class CiscoTelemetryClient:
    """Cliente gRPC para recibir datos de telemetría en streaming"""

    def __init__(self, host="192.168.1.100", port=57000):
        self.host = host
        self.port = port

        # Cargar certificados TLS
        with open("certs/ca-cert.pem", "rb") as f:
            self.root_cert = f.read()
        with open("certs/client-cert.pem", "rb") as f:
            self.client_cert = f.read()
        with open("certs/client-key.pem", "rb") as f:
            self.client_key = f.read()

        # Configurar credenciales seguras TLS
        self.credentials = grpc.ssl_channel_credentials(
            root_certificates=self.root_cert,
            private_key=self.client_key,
            certificate_chain=self.client_cert
        )

    def subscribe_to_stream(self, xpath_filter="/interfaces/interface/state/counters"):
        """Suscribirse al stream de telemetría"""
        try:
            with grpc.secure_channel(f"{self.host}:{self.port}", self.credentials) as channel:
                stub = cisco_telemetry_pb2_grpc.TelemetryServiceStub(channel)
                request = cisco_telemetry_pb2.TelemetryRequest(xpath=xpath_filter)

                print(f"📡 Suscrito a {xpath_filter}, escuchando métricas en tiempo real...\n")

                for telemetry_data in stub.SubscribeTelemetry(request):
                    timestamp = telemetry_data.timestamp
                    metrics = dict(telemetry_data.metrics)
                    print(f"[{timestamp}] Datos recibidos:")
                    for key, value in metrics.items():
                        print(f"  🔹 {key}: {value}")
                    print("-" * 40)
                    time.sleep(1)
        except grpc.RpcError as e:
            print(f" Error gRPC: {e.code()} - {e.details()}")

if __name__ == "__main__":
    client = CiscoTelemetryClient()
    client.subscribe_to_stream()
