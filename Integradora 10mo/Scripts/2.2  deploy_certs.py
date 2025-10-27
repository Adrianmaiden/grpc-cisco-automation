#!/usr/bin/env python3
import argparse
import getpass
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy

def deploy_certificates(host, username, password, certs_path="./certs"):
    """
    Se conecta a un dispositivo Cisco vía SSH y copia los certificados
    de la CA y del servidor al bootflash:.
    """
    certs_dir = Path(certs_path)
    files_to_deploy = {
        "ca-cert.pem": certs_dir / "ca-cert.pem",
        "server-cert.pem": certs_dir / "server-cert.pem",
        "server-key.pem": certs_dir / "server-key.pem"
    }

    print(f" Conectando a {host}...")
    try:
        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(hostname=host, username=username, password=password, port=22)

            print(" Conexión exitosa. Abriendo sesión SFTP...")
            with ssh.open_sftp() as sftp:
                for file_name, local_path in files_to_deploy.items():
                    if not local_path.exists():
                        print(f" Error: El archivo {local_path} no fue encontrado.")
                        continue

                    remote_path = f"/bootflash/{file_name}"
                    print(f"  > Copiando {local_path} a {remote_path}...")
                    sftp.put(str(local_path), remote_path)

            print("\n Despliegue de certificados completado exitosamente.")

    except Exception as e:
        print(f"\n Ocurrió un error durante el despliegue: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Despliega certificados en un switch Cisco NX-OS.")
    parser.add_argument("--host", required=True, help="Dirección IP del switch Cisco.")
    parser.add_argument("--user", default="admin", help="Nombre de usuario para la conexión SSH.")

    args = parser.parse_args()

    # Solicitar la contraseña de forma segura
    password = getpass.getpass(f"Ingrese la contraseña para {args.user}@{args.host}: ")

    deploy_certificates(args.host, args.user, password)
