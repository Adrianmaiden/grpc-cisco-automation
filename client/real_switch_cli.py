#!/usr/bin/env python3
import grpc
import sys
import os
import json

# Ajuste de path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importamos los protos de Cisco y tu ConfigManager
from protos import cisco_pb2, cisco_pb2_grpc
from client.config_loader import ConfigManager

def apply_config_via_cli(config_file, target):
    print(f"\n🚀 Iniciando configuración (Modo CLI) en {target}")
    
    loader = ConfigManager()
    config_dict = loader.load_config_from_file(config_file)
    
    print("🔨 Generando comandos CLI...")
    commands = ["conf t"]
    
    for iface in config_dict.get("interfaces", []):
        name = iface["name"]
        desc = iface["description"]
        enabled = iface["enabled"]
        
        commands.append(f"interface {name}")
        commands.append(f"  description {desc}")
        if enabled:
            commands.append("  no shutdown")
        else:
            commands.append("  shutdown")
        commands.append("  exit")

    cli_payload = " ; ".join(commands)
    
    # Conexión mTLS
    certs_path = "certs/"
    with open(certs_path + "ca-cert.pem", 'rb') as f: ca = f.read()
    with open(certs_path + "client-key.pem", 'rb') as f: ck = f.read()
    with open(certs_path + "client-cert.pem", 'rb') as f: cc = f.read()

    creds = grpc.ssl_channel_credentials(ca, ck, cc)
    
    # IMPORTANTE: Si usas el Mock local, descomenta esta opción para evitar error SSL de nombre
    # options = (('grpc.ssl_target_name_override', 'server'),)
    # channel = grpc.secure_channel(target, creds, options=options)
    
    # Para Mock/Switch en localhost sin validación estricta de hostname:
    channel = grpc.secure_channel(target, creds)
    
    stub = cisco_pb2_grpc.gRPCConfigOperStub(channel)
    auth_metadata = [('username', 'admin'), ('password', 'Cisco123')]

    print("📡 Enviando payload...")
    try:
        request = cisco_pb2.ConfigArgs(reqID="1", cli=cli_payload)
        response = stub.Config(request, metadata=auth_metadata)
        
        if response.errors:
            print(f"\n❌ Error del Switch: {response.errors}")
        else:
            print("\n✅ ¡CONFIGURACIÓN APLICADA!")
            print(f"   Output: {response.output}")
            
    except grpc.RpcError as e:
        print(f"\n❌ Error gRPC: {e.code()} - {e.details()}")
