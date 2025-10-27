import time
from collections import deque
from datetime import datetime

class TelemetryCollector:
    """Colector de telemetría con almacenamiento temporal en memoria"""

    def __init__(self, buffer_size=100):
        # Usamos deque para mantener solo los últimos N registros
        self.buffer = deque(maxlen=buffer_size)

    def process_data(self, telemetry_packet):
        """
        Procesa un paquete de telemetría.
        telemetry_packet: dict con métricas del switch
        """
        processed = {
            "timestamp": datetime.now().isoformat(),
            "metrics": telemetry_packet
        }

        # Ejemplo de procesamiento: convertir strings a enteros si es posible
        for key, value in telemetry_packet.items():
            try:
                processed["metrics"][key] = int(value)
            except ValueError:
                processed["metrics"][key] = value

        self.buffer.append(processed)
        print(f" Datos procesados y almacenados (total: {len(self.buffer)})")

    def get_recent_data(self, limit=10):
        """Devuelve los últimos registros almacenados"""
        return list(self.buffer)[-limit:]
