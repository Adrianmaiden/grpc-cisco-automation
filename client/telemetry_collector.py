from collections import deque
from datetime import datetime

class TelemetryCollector:
    """
    Colector de telemetría con almacenamiento temporal en memoria (RAM).
    Implementa un buffer circular (deque) para mantener solo los últimos N registros.
    """

    def __init__(self, buffer_size=100):
        # deque elimina automáticamente los elementos viejos cuando se llena
        self.buffer = deque(maxlen=buffer_size)

    def process_data(self, key, value):
        """
        Recibe una métrica cruda, le agrega timestamp y la guarda.
        """
        # Normalizamos el dato para almacenamiento
        record = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "metric": key,
            "value": value
        }
        
        self.buffer.append(record)
        # Log ligero para depuración en consola
        # print(f"📥 [Colector] Guardado: {key} = {value}")

    def get_recent_data(self):
        """
        Devuelve una lista con todos los registros actuales del buffer.
        """
        return list(self.buffer)