Política de Seguridad (SECURITY.md)

Este documento describe la política de seguridad para el proyecto grpc-cisco-automation. El proyecto sigue los principios de la norma internacional ISO 27001 para establecer un Sistema de Gestión de Seguridad de la Información (SGSI) que garantice la protección de la infraestructura de red gestionada.

1. Objetivo de Seguridad
El principal objetivo de seguridad es asegurar la Confidencialidad, Integridad y Autenticidad (la tríada CIA) de toda la comunicación y configuración gestionada a través de este sistema.


2. Análisis de Riesgos
Se ha realizado un análisis de los principales riesgos de seguridad para el sistema, junto con los controles implementados para mitigarlos:

  Riesgo Identificado: Interceptación del tráfico de red (Man-in-the-Middle)
  Impacto Potencial: Robo de credenciales, visualización de configuración.
  Control Implementado (Mitigación): Cifrado con mTLS: Garantiza la confidencialidad del canal.
  
  Riesgo Identificado: Acceso no autorizado al API del switch
  Impacto Potencial: Cambios de configuración maliciosos, denegación de servicio.
  Control Implementado (Mitigación): Autenticación mTLS: El switch valida la identidad del cliente.
  
  Riesgo Identificado: Suplantación de identidad del switch
  Impacto Potencial: El cliente envía configuraciones a un equipo falso.


3. Controles de Seguridad Implementados
Para cumplir con los objetivos de seguridad y mitigar los riesgos identificados, se han implementado los siguientes controles, alineados con el Anexo A de la norma ISO 27001.

3.1. Controles Criptográficos (Anexo A.10)
Toda la comunicación entre el cliente Python y el agente gRPC en el switch Cisco está protegida mediante TLS Mutuo (mTLS). Este control criptográfico asegura:

Confidencialidad: El tráfico se cifra, impidiendo que sea leído por terceros no autorizados.

Integridad: Se aplican mecanismos para detectar cualquier modificación no autorizada de los datos en tránsito.

3.2. Controles de Acceso (Anexo A.9)
El acceso a la API de gestión del switch está estrictamente controlado.

Autenticación Fuerte: Se utiliza un modelo de autenticación basado en certificados X.509. Solo los clientes que posean un certificado válido, firmado por la Autoridad Certificadora (CA) del proyecto, pueden establecer una conexión.

Autorización Bidireccional: Gracias a mTLS, tanto el servidor (switch) como el cliente validan sus identidades mutuamente, previniendo ataques de suplantación de identidad en ambas direcciones.

3.3. Gestión de Activos y Secretos (Anexo A.8)
Los activos criptográficos, como las llaves privadas de la CA, el servidor y el cliente, son los componentes más sensibles del sistema.

Protección de Secretos: Todas las llaves privadas y certificados no deben ser almacenados en el repositorio de Git. El archivo .gitignore está configurado para excluir estos archivos.

Guía de Generación Segura: La documentación del proyecto instruye a los usuarios para que generen sus propios certificados y los almacenen en un lugar seguro con permisos de acceso restringidos.


4. Gestión y Reporte de Vulnerabilidades
Tomamos la seguridad de este proyecto muy en serio. Agradecemos a la comunidad por sus esfuerzos en la divulgación responsable de vulnerabilidades.

Política de Reporte
Si descubres una vulnerabilidad de seguridad, por favor, ayúdanos reportándola de manera privada. Te pedimos que no divulgues la vulnerabilidad públicamente hasta que hayamos tenido la oportunidad de analizarla y solucionarla.

Cómo Reportar una Vulnerabilidad
Envía un correo electrónico a [Correo del Líder de Proyecto] con el asunto "Reporte de Vulnerabilidad: grpc-cisco-automation".

En el cuerpo del correo, por favor, incluye la siguiente información:

Una descripción detallada de la vulnerabilidad.

Los pasos necesarios para reproducirla.

El impacto potencial de la vulnerabilidad.

Cualquier prueba de concepto o script que hayas utilizado.

Nos comprometemos a investigar todos los reportes de manera oportuna y a trabajar para solucionar cualquier problema de seguridad encontrado.
