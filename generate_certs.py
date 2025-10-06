#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

class CertificateManager:
    def __init__(self, base_path="./certs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def run_command(self, command: list):
        subprocess.run(command, check=True)
    
    def generate_ca(self):
        print("🛠️ Generando CA...")
        self.run_command([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-days", "365", "-nodes",
            "-keyout", f"{self.base_path}/ca-key.pem",
            "-out", f"{self.base_path}/ca-cert.pem",
            "-subj", "/C=MX/ST=Morelos/L=Cuernavaca/O=NetworkOrg/OU=IT/CN=RootCA"
        ])
        print(" CA generada correctamente.\n")

    def generate_cert(self, name: str, san_list: list):
        print(f" Generando certificado para {name}...")
        san_config = f"{self.base_path}/{name}-ext.cnf"
        with open(san_config, "w") as f:
            f.write(f"subjectAltName={','.join(['DNS:' + s for s in san_list])}\n")

        self.run_command([
            "openssl", "req", "-newkey", "rsa:4096", "-nodes",
            "-keyout", f"{self.base_path}/{name}-key.pem",
            "-out", f"{self.base_path}/{name}-req.pem",
            "-subj", f"/C=MX/ST=Morelos/L=Cuernavaca/O=NetworkOrg/OU=Devices/CN={name}"
        ])

        # Firmar con la CA
        self.run_command([
            "openssl", "x509", "-req", "-in", f"{self.base_path}/{name}-req.pem",
            "-days", "180",
            "-CA", f"{self.base_path}/ca-cert.pem",
            "-CAkey", f"{self.base_path}/ca-key.pem",
            "-CAcreateserial",
            "-out", f"{self.base_path}/{name}-cert.pem",
            "-extfile", san_config
        ])
        print(f" Certificado de {name} generado correctamente.\n")

if __name__ == "__main__":
    cm = CertificateManager()
    cm.generate_ca()
    cm.generate_cert("server", ["localhost", "192.168.1.100"])
    cm.generate_cert("client", ["localhost"])
