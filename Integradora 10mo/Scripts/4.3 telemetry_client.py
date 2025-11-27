from telemetry_collector import TelemetryCollector
import cisco_telemetry_pb2
import cisco_telemetry_pb2_grpc
import grpc

collector = TelemetryCollector(buffer_size=200)

def run():
    with open("certs/ca-cert.pem", "rb") as f:
        root_cert = f.read()
    with open("certs/client-cert.pem", "rb") as f:
        client_cert = f.read()
    with open("certs/client-key.pem", "rb") as f:
        client_key = f.read()

    credentials = grpc.ssl_channel_credentials(
        root_certificates=root_cert,
        private_key=client_key,
        certificate_chain=client_cert
    )

    with grpc.secure_channel("192.168.1.100:57000", credentials) as channel:
        stub = cisco_telemetry_pb2_grpc.TelemetryServiceStub(channel)
        request = cisco_telemetry_pb2.TelemetryRequest(xpath="/interfaces/interface/state/counters")

        print(" Escuchando flujo de telemetría...")

        for telemetry_data in stub.SubscribeTelemetry(request):
            metrics = dict(telemetry_data.metrics)
            collector.process_data(metrics)
