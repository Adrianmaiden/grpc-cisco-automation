import grpc
import sys
import os
import threading
import time
from flask import Flask, jsonify

# Ajuste de path para importar módulos locales y protos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protos import network_manager_pb2, network_manager_pb2_grpc
from client.telemetry_collector import TelemetryCollector

# --- CONFIGURACIÓN ---
app = Flask(__name__)
collector = TelemetryCollector(buffer_size=50) # Guardamos los últimos 50 datos

# --- HILO DE GESTIÓN gRPC ---
def grpc_consumer_thread():
    """
    Se conecta al stream gRPC y alimenta al colector en segundo plano.
    """
    target = "localhost:50051"
    certs_path = "certs/"
    
    # Cargar credenciales mTLS
    with open(certs_path + "ca-cert.pem", 'rb') as f: ca_cert = f.read()
    with open(certs_path + "client-key.pem", 'rb') as f: client_key = f.read()
    with open(certs_path + "client-cert.pem", 'rb') as f: client_cert = f.read()
    
    creds = grpc.ssl_channel_credentials(ca_cert, client_key, client_cert)
    
    while True:
        try:
            print("🔄 [gRPC] Conectando al servidor de telemetría...")
            channel = grpc.secure_channel(target, creds)
            stub = network_manager_pb2_grpc.NetworkManagerStub(channel)
            request = network_manager_pb2.TelemetryRequest(sensor_path="sys/resources")
            
            # Iniciamos la suscripción
            stream = stub.GetTelemetry(request)
            
            for data in stream:
                # Decodificamos el valor 'oneof' del Protobuf
                valor = None
                if data.HasField("double_val"):
                    valor = round(data.double_val, 2)
                elif data.HasField("int_val"):
                    valor = data.int_val
                elif data.HasField("string_val"):
                    valor = data.string_val
                
                # Enviamos el dato limpio al Colector
                if valor is not None:
                    collector.process_data(data.key, valor)
                    
        except Exception as e:
            print(f"⚠️ Error gRPC: {e}. Reintentando en 5s...")
            time.sleep(5)

# --- API REST (FLASK) ---
@app.route('/api/telemetry')
def api_telemetry():
    """
    Endpoint que devuelve el contenido actual del buffer en JSON.
    """
    return jsonify(collector.get_recent_data())

@app.route('/')
def home():
    return "<h1>Colector de Telemetría Activo</h1><p>Visita <a href='/api/telemetry'>/api/telemetry</a> para ver los datos JSON.</p>"

if __name__ == '__main__':
    # Arrancar el hilo gRPC como daemon (se cierra al cerrar el script)
    t = threading.Thread(target=grpc_consumer_thread)
    t.daemon = True
    t.start()
    
    # Arrancar el servidor Web
    print("🚀 API del Colector iniciada en http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080)