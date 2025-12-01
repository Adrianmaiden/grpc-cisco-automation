import sys
import os
import io
import time
import threading
import contextlib
import grpc
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# --- AJUSTE DE PATHS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

# Importamos módulos
from client.real_switch_cli import apply_config_via_cli
from protos import network_manager_pb2, network_manager_pb2_grpc

app = Flask(__name__)

# --- BLOQUE ANTI-CACHÉ (Agrégalo aquí) ---
@app.after_request
def add_header(response):
    # Le dice al navegador: "Nunca guardes nada en caché"
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response
# -----------------------------------------

# --- CONFIGURACIÓN ---
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Estado global para Telemetría
telemetry_state = {
    "cpu": 0.0,
    "memory": 0,
    "traffic": 0.0,
    "last_update": "Esperando..."
}

# ==============================================================================
# 1. HILO DE TELEMETRÍA (Background Worker)
# ==============================================================================
def telemetry_worker():
    """
    Consume el stream gRPC desde el Mock Server local.
    """
    # --- CAMBIO: Apuntamos a localhost porque usamos el Mock ---
    target = "localhost:50051" 
    # ---------------------------------------------------------
    
    certs_path = os.path.join(parent_dir, "certs/")
    
    print(f"🔄 [Backend] Iniciando monitor de telemetría hacia {target}...")
    
    try:
        with open(certs_path + "ca-cert.pem", 'rb') as f: ca = f.read()
        with open(certs_path + "client-key.pem", 'rb') as f: ck = f.read()
        with open(certs_path + "client-cert.pem", 'rb') as f: cc = f.read()
        creds = grpc.ssl_channel_credentials(ca, ck, cc)
    except Exception as e:
        print(f"❌ [Backend] Error cargando certificados: {e}")
        return

    while True:
        try:
            # Conexión Segura a Localhost
            channel = grpc.secure_channel(target, creds)
            
            stub = network_manager_pb2_grpc.NetworkManagerStub(channel)
            request = network_manager_pb2.TelemetryRequest(sensor_path="sys/resources")
            
            stream = stub.GetTelemetry(request)
            
            for data in stream:
                if data.key == "cpu_usage":
                    telemetry_state["cpu"] = round(data.double_val, 2)
                elif data.key == "memory_free":
                    telemetry_state["memory"] = data.int_val
                elif data.key == "eth1_1_traffic":
                    telemetry_state["traffic"] = round(data.double_val, 2)
                
                telemetry_state["last_update"] = data.timestamp
                
        except Exception as e:
            # Reintento silencioso para no ensuciar la consola si el mock se apaga
            time.sleep(5)

# ==============================================================================
# 2. RUTAS WEB
# ==============================================================================
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/configure')
def configure_page():
    return render_template('configure.html')

# Vistas Demo
@app.route('/editor')
def editor_page(): return render_template('editor.html')
@app.route('/library')
def library_page(): return render_template('library.html')
@app.route('/quick')
def quick_page(): return render_template('quick_cfg.html')

# ==============================================================================
# 3. API ENDPOINTS
# ==============================================================================

@app.route('/api/telemetry')
def get_telemetry():
    return jsonify(telemetry_state)

@app.route('/api/deploy', methods=['POST'])
def deploy_config():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Captura de Logs
        log_capture = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(log_capture):
                print(f"🔵 [WEB] Iniciando despliegue de: {filename}")
                
                # --- CAMBIO: Apuntamos a localhost ---
                target_switch = "localhost:50051"
                print(f"🔵 [WEB] Objetivo: {target_switch}")
                
                # Ejecutamos el script de configuración contra el Mock local
                apply_config_via_cli(filepath, target_switch)
                # -------------------------------------
                
                print("🏁 [WEB] Proceso finalizado.")
            
            logs = log_capture.getvalue()
            success = True
            
        except Exception as e:
            logs = f"❌ Error crítico en backend:\n{str(e)}"
            success = False
            
        return jsonify({
            "success": success,
            "logs": logs
        })

# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == '__main__':
    t = threading.Thread(target=telemetry_worker)
    t.daemon = True
    t.start()
    
    print("🚀 Servidor Network Manager iniciado en http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
