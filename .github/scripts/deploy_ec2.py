import boto3
import os
import time

# --- Configuración Leída de los Secretos de GitHub ---
# NO pongas valores sensibles aquí. Se leen de las variables de entorno.
AWS_REGION = "us-east-1"
KEY_NAME = os.environ.get('EC2_KEY_NAME')
SECURITY_GROUP_ID = os.environ.get('EC2_SECURITY_GROUP_ID')

# --- Configuración del Proyecto ---
AMI_ID = "ami-0c398cb65a93047f2"  # Ubuntu 22.04 LTS en us-east-1
INSTANCE_TYPE = "t2.micro"       # Incluido en la capa gratuita de AWS
INSTANCE_TAG_KEY = "project"
INSTANCE_TAG_VALUE = "grpc-cisco-test" # Un tag único
REPO_URL = "https://github.com/Adrianmaiden/grpc-cisco-automation.git" # Tu repo

# --- ESTE ES EL SCRIPT QUE SE EJECUTA DENTRO DE LA EC2 ---
# Lo hemos simplificado al máximo.
USER_DATA_SCRIPT = f"""#!/bin/bash
set -ex
cd /home/ubuntu

# Actualizar e instalar git
apt-get update
apt-get install -y git

# Clonar tu repositorio
git clone {REPO_URL}

# Crear un archivo de prueba para verificar que funcionó
echo "¡Hola Profesor! El despliegue desde GitHub Actions fue exitoso." > /home/ubuntu/PRUEBA_EXITOSA.txt
"""

# --- Lógica Principal (No necesitas tocar esto) ---
def deploy():
    if not KEY_NAME or not SECURITY_GROUP_ID:
        print("Error: Faltan secretos. Asegúrate de definir EC2_KEY_NAME y EC2_SECURITY_GROUP_ID en GitHub.")
        exit(1)

    ec2 = boto3.client('ec2', region_name=AWS_REGION)
    ec2_resource = boto3.resource('ec2', region_name=AWS_REGION)

    print(f"Buscando instancias existentes con el Tag: {INSTANCE_TAG_KEY}={INSTANCE_TAG_VALUE}")

    # 1. Buscar y Terminar instancias existentes
    instances_to_terminate = []
    response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{INSTANCE_TAG_KEY}', 'Values': [INSTANCE_TAG_VALUE]},
            {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
        ]
    )
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances_to_terminate.append(instance['InstanceId'])

    if instances_to_terminate:
        print(f"Terminando {len(instances_to_terminate)} instancia(s) antigua(s): {instances_to_terminate}")
        ec2.terminate_instances(InstanceIds=instances_to_terminate)
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=instances_to_terminate)
        print("Instancias antiguas terminadas.")
    else:
        print("No se encontraron instancias existentes.")

    # 2. Crear nueva instancia
    print(f"Creando nueva instancia {INSTANCE_TYPE}...")
    instance = ec2_resource.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[SECURITY_GROUP_ID],
        UserData=USER_DATA_SCRIPT,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': INSTANCE_TAG_KEY, 'Value': INSTANCE_TAG_VALUE},
                    {'Key': 'Name', 'Value': 'gRPC-Test-Server'}
                ]
            }
        ]
    )[0]

    print(f"Instancia {instance.id} creada. Esperando a que esté 'running'...")
    instance.wait_until_running()
    instance.reload() # Recargar datos para obtener la IP pública

    print("\n--- ¡Despliegue Exitoso! ---")
    print(f"ID de Instancia: {instance.id}")
    print(f"IP Pública: {instance.public_ip_address}")
    print(f"Puedes conectarte con: ssh -i TULLAVE.pem ubuntu@{instance.public_ip_address}")

if __name__ == "__main__":
    deploy()