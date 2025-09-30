# grpc-cisco-automation
📖 Sobre el Proyecto
Este proyecto implementa un sistema de automatización para administrar la configuración y monitorear el estado de switches Cisco (NX-OS/IOS XE) mediante un canal de comunicación gRPC seguro. Utiliza un enfoque de Infraestructura como Código (IaC), donde el estado deseado de la red se define en archivos de configuración y se aplica de forma programática. 

El sistema se compone de un servidor de control Linux que ejecuta scripts en Python, se comunica de forma segura con los switches mediante 

TLS Mutuo (mTLS) y presenta la información en un dashboard web para visualización y pruebas. 

🏗️ Arquitectura
El siguiente diagrama ilustra el flujo de datos completo del sistema, desde la definición de la configuración hasta la visualización de la telemetría.

![Diagrama de Arquitectura](diagram.png)


🛡️ Seguridad
Este proyecto pone un fuerte énfasis en la seguridad. Para más detalles sobre nuestra política de seguridad, análisis de riesgos y cómo reportar vulnerabilidades, por favor, consulta nuestro archivo SECURITY.md.

📄 Licencia
Distribuido bajo la Licencia MIT. Ver LICENSE para más información.

Autores

Adrian Barroso Barrios

Diego Axel Estrada Ayala 

Oscar Kevin Martinez Acosta 
