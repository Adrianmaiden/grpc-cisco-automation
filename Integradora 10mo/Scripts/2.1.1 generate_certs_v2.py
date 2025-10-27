#!/usr/bin/env python3
import os
import subprocess
import argparse
import configparser
from pathlib import Path

class CertificateManager:
    """Gestiona la creación de una CA y la firma de certificados."""

    def __init__(self, base_path="./certs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def run_command(self, command: list):
        """Ejecuta un comando de subprocess y verifica si hay errores."""
        subprocess.run(command, check=True, capture_output=True, text=True)

    def generate_ca(self):
        """Genera la Autoridad Certificadora (CA) usando la configuración de config.ini."""
        print("  Generando Autoridad Certificadora (CA)...")
        ca_config = self.config['ca']
        self.run_command([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-days", ca_config['days'],
            "-nodes",
            "-keyout", f"{self.base_path}/ca-key.pem",
            "-out", f"{self.base_path}/ca-cert.pem",
            "-subj", ca_config['subj']
        ])
        print(" CA generada correctamente.\n")

    def generate_cert(self, name: str):
        """Genera un certificado para un nombre dado (ej. 'server', 'client')."""
        print(f" Generando certificado para '{name}'...")
        if name not in self.config:
            raise ValueError(f"No se encontró la sección '{name}' en config.ini")

        cert_config = self.config[name]
        san_list = cert_config['san'].split(',')
        san_config_file = self.base_path / f"{name}-ext.cnf"
        req_file = self.base_path / f"{name}-req.pem"

        # Crear archivo de configuración SAN
        with open(san_config_file, "w") as f:
            f.write(f"subjectAltName={','.join(['DNS:' + s.strip() for s in san_list])}\n")

        # Generar solicitud de firma (CSR)
        self.run_command([
            "openssl", "req", "-newkey", "rsa:4096", "-nodes",
            "-keyout", f"{self.base_path}/{name}-key.pem",
            "-out", str(req_file),
            "-subj", cert_config['subj']
        ])

        # Firmar el certificado con la CA
        self.run_command([
            "openssl", "x509", "-req", "-in", str(req_file),
            "-days", cert_config['days'],
            "-CA", f"{self.base_path}/ca-cert.pem",
            "-CAkey", f"{self.base_path}/ca-key.pem",
            "-CAcreateserial",
            "-out", f"{self.base_path}/{name}-cert.pem",
            "-extfile", str(san_config_file)
        ])

        # Limpieza de archivos temporales
        os.remove(req_file)
        os.remove(san_config_file)

        print(f" Certificado de '{name}' generado correctamente.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestor de Certificados para gRPC Lab")
    parser.add_argument('action', choices=['generate-ca', 'generate-cert', 'all'], help="Acción a realizar.")
    parser.add_argument('--name', type=str, help="Nombre del certificado a generar (ej. 'server' o 'client'). Requerido para 'generate-cert'.")

    args = parser.parse_args()
    cm = CertificateManager()

    if args.action == 'generate-ca':
        cm.generate_ca()
    elif args.action == 'generate-cert':
        if not args.name:
            parser.error("--name es requerido para la acción 'generate-cert'.")
        cm.generate_cert(args.name)
    elif args.action == 'all':
        cm.generate_ca()
        cm.generate_cert('server')
        cm.generate_cert('client')
