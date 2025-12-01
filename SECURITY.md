# Política de Seguridad

> **Nota:** Este proyecto sigue los principios de la norma internacional **ISO 27001** para establecer un Sistema de Gestión de Seguridad de la Información (SGSI) enfocado en la automatización de redes.

## 1. Objetivo de Seguridad
El objetivo principal es garantizar la **Tríada CIA** en toda la infraestructura gestionada por `grpc-cisco-automation`:

* **Confidencialidad:** Solo las partes autorizadas pueden acceder a los datos.
* **Integridad:** Los datos de configuración no son alterados en tránsito.
* **Autenticidad:** Confirmación absoluta de la identidad de switches y clientes.

---

## 2. Análisis de Riesgos y Mitigación
Hemos realizado un análisis de riesgos para identificar amenazas críticas y los controles técnicos implementados para neutralizarlas.

| Riesgo Identificado | Impacto Potencial | Control Implementado (Mitigación) |
| :--- | :--- | :--- |
| **Interceptación (Man-in-the-Middle)** | Robo de credenciales, visualización de `running-config`. | **Cifrado TLS:** Todo el canal gRPC está cifrado, haciendo ilegible el tráfico para terceros. |
| **Acceso no autorizado al API** | Cambios de configuración maliciosos, DoS. | **Autenticación mTLS:** El switch valida criptográficamente el certificado del cliente antes de aceptar comandos. |
| **Suplantación de Switch (Spoofing)** | El cliente envía configuraciones a un equipo falso/atacante. | **Validación de Servidor:** El cliente Python valida el certificado del switch contra la CA raíz. |

---

## 3. Controles de Seguridad Implementados (ISO 27001)

Para cumplir con los objetivos y mitigar los riesgos, se han desplegado los siguientes controles alineados con el **Anexo A** de la norma ISO 27001.

### 3.1. Controles Criptográficos (A.10)
Toda la comunicación entre el cliente (Python/gRPC) y el agente en el switch Cisco está protegida mediante **TLS Mutuo (mTLS)**.
* **Confidencialidad:** Cifrado robusto (AES/RSA/ECC según configuración) en tránsito.
* **Integridad:** Algoritmos de hash (SHA-256) garantizan que los payloads (JSON/XML) no sean modificados.

### 3.2. Controles de Acceso (A.9)
El acceso a la API de gestión (gRPC port 57400/etc) es de "Privilegio Mínimo":
* **Autenticación Fuerte:** Basada estrictamente en certificados **X.509**. No se permite autenticación de texto plano.
* **Autorización Bidireccional:** Tanto el cliente como el servidor deben presentar certificados firmados por la Autoridad Certificadora (CA) privada del proyecto.

### 3.3. Gestión de Activos y Secretos (A.8)
Los activos criptográficos son los componentes más críticos.
* **Protección de Secretos:** Las llaves privadas (`.key`, `.pem`) **NUNCA** se almacenan en el repositorio.
* **Git Ignore:** El archivo `.gitignore` está configurado para excluir extensiones de certificados y llaves.
* **Responsabilidad del Usuario:** Se instruye al usuario a generar sus propias PKI y resguardarlas en bóvedas seguras (ej. HashiCorp Vault) o directorios locales con permisos `chmod 600`.

---

## 4. Gestión y Reporte de Vulnerabilidades

Tomamos la seguridad muy en serio y agradecemos la divulgación responsable.

### Política de Reporte
Si descubres una vulnerabilidad, por favor **NO la divulgues públicamente** (GitHub Issues) hasta que haya sido analizada.

### Cómo Reportar
Envía un correo electrónico al mantenedor del proyecto:


**Asunto:** `Reporte de Vulnerabilidad: grpc-cisco-automation`

Por favor incluye:
1.  Descripción detallada del fallo.
2.  Pasos para reproducirlo (PoC).
3.  Impacto potencial en la red.
4.  Entorno de pruebas (Versión de IOS XE/NX-OS, versión de Python).

Nos comprometemos a investigar y responder en un plazo razonable para solucionar cualquier brecha de seguridad.
