# Creze - Caso técnico

## Tabla de contenido

1. [Descripción del proyecto](#descripción-del-proyecto)
2. [Autenticación Multi-Factor](#autenticación-multi-factor)
3. [Tecnologías y herramientas utilizadas](#tecnologías-y-herramientas-utilizadas)
4. [Instrucciones de instalación](#instrucciones-de-instalación)
5. [Pruebas](#pruebas)
6. [Documentación](#documentación)

---

## Descripción del proyecto

Este proyecto tiene como objetivo desarrollar un módulo de autenticación multi-factor (MFA). El desarrollo del sistema MFA tiene como fin añadir una capa adicional de seguridad, permitiendo a los usuarios proteger mejor sus cuentas y datos financieros.

## Autenticación Multi-Factor

- Añadir un segundo factor de autenticación utilizando **Time-Based One-Time Passwords (TOTP)**, compatible con aplicaciones como **Google Authenticator** o **Authy**.
- Almacenar de forma segura las claves secretas asociadas a cada usuario en la base de datos.

## Tecnologías y herramientas utilizadas

- **Lenguaje de programación Backend:** Python 3.x
- **Framework Web Backend:** Django 4.x
- **Base de Datos:** PostgreSQL 13.x
- **Servidor Web:** Nginx
- **Contenedores:** Docker y Docker Compose
- **Herramientas AWS:** EC2, Lambda, RDS, Secrets Manager
- **Control de versiones:** Git

## Instrucciones de Instalación

1. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/naranjochuy/creze_api.git
    cd creze_api
    ```

2. **Entornos de Producción y Desarrollo:**

    Las instrucciones de instalación son las mismas tanto para el entorno de producción como para el de desarrollo. La única diferencia radica en el valor de la variable de entorno `DJANGO_ENV`:

   - **Producción**: Establece `DJANGO_ENV` en `prod`.
   - **Desarrollo**: Establece `DJANGO_ENV` en `dev`.

   Asegúrate de darle el valor correcto, la variable se encuentra en el archivo `docker-compose.yml`, modifica esta variable antes de iniciar los contenedores según el entorno en el que estés trabajando.

3. **Levantar los contenedores de Docker:**

    Asegúrate de tener **Docker** y **Docker Compose** instalados. Luego, ejecuta:

    ```bash
    docker compose up --build --detach
    ```
   
    Si ya tienes **Make** instalado y prefieres utilizarlo, puedes iniciar los contenedores con:

    ```bash
    make up
    ```
   **Nota:** En ambos casos, es necesario tener **Docker** y **Docker Compose** instalados para que el comando funcione correctamente.

## Pruebas

1. **Levantar los contenedores de Docker:**

    Primero, necesitas asegurarte de que los contenedores estén en funcionamiento.


2. **Ejecutar comando dentro del contenedor:**

    Puedes ejecutar comandos dentro del contenedor usando el siguiente comando:

    ```bash
    docker compose exec creze-api python manage.py test
    ```
   
    o

    ```bash
    make test
    ```
   **Nota:** El **throttling** estará desactivado en el entorno de desarrollo.
   






## Documentación

   - **Base URL producción**: `http://ec2-54-80-48-166.compute-1.amazonaws.com/api/`
   - **Authentication**: Esta API utiliza JWT (JSON Web Tokens) para autenticación. Incluye el token JWT en el encabezado `Authorization` con el formato: `Bearer <tu_token>`.

### Autenticación

**Endpoint: POST /login/**

**Description:**
Este endpoint permite a los usuarios autenticarse proporcionando sus credenciales (correo electrónico y contraseña). Si las credenciales son correctas, el endpoint devuelve un token JWT que debe ser utilizado en las solicitudes futuras para acceder a recursos protegidos.

**Request:**
- Headers:
  - `N/A`

- Body:
```json
{
	"email": "correo@gmail.com",
	"password": "password"
}
```

**Response:**
- Status: `200 OK`
- Body:
```json
{
	"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI3MTM4MTQ2LCJpYXQiOjE3MjcxMzgwODYsImp0aSI6IjYwOWZkN2I2NDkwMDQwZWI4MWQ4OTQxZWRhN2ZkMGY3IiwidXNlcl9pZCI6MX0.9sGACwC9KMm1iHUUXbvVtQnMskNy_H7cbU2Q3Y0S70k",
	"otp_activated": true,
	"otp_verified": false
}
```

- Status: `401 Unauthorized`
- Body:
```json
{
	"detail": "Credenciales inválidas"
}
```

- Status: `400 Bad Request`
- Body:
```json
{
	"password": [
		"Este campo no puede estar en blanco."
	],
	"email": [
		"Este campo no puede estar en blanco."
	]
}
```

___
### Registro

**Endpoint: POST /signup/**

**Description:**
Este endpoint permite a los nuevos usuarios registrarse en la aplicación. Los usuarios deben proporcionar correo electrónico y contraseña. Al completarse el registro, se crea una nueva cuenta de usuario y se devuelve una respuesta de éxito.

**Request:**
- Headers:
  - `N/A`

- Body:
```json
{
	"email": "correo@gmail.com",
	"password": "password"
}
```

**Response:**
- Status: `201 Created`
- Body:
```
    N/A
```

- Status: `400 Bad Request`
- Body:
```json
{
	"password": [
		"Este campo no puede estar en blanco."
	],
	"email": [
		"Este campo no puede estar en blanco."
	]
}
```

___
### Configuración de MFA

**Endpoint: GET /mfa-setup/**

**Description:**
Este endpoint genera una URI para configurar la Autenticación Multifactor (MFA) para un usuario. La URI generada se puede utilizar para escanear un código QR en aplicaciones de autenticación como Google Authenticator o Authy, lo que habilita el uso de códigos temporales para asegurar la cuenta del usuario.

**Request:**
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`

**Response:**
- Status: `200 OK`
- Body:
```json
{
	"otp_uri": "otpauth://totp/CrezeApp:a%40a.com?secret=None&issuer=CrezeApp"
}
```

### Validación de MFA

**Endpoint: POST /validate/**

**Description:**
Este endpoint permite validar un código de autenticación multifactor (MFA). El usuario debe enviar el código generado por su aplicación de autenticación (como Google Authenticator o Authy). Si el código es correcto, el MFA se marcará como validado para el usuario, mejorando la seguridad de su cuenta.

**Request:**
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`

- Body:
```json
{
	"code": "183753"
}
```

**Response:**
- Status: `200 OK`
- Body:
```json
{
  "recovery_codes": [
    "X9FJ3W84NV",
    "B7KLMZ0PQR",
    "V5TYH3D8WL",
    "N2HQ6J4S8Z",
    "P8X0RQ1W7M",
    "F4ZK9T6B3C",
    "L9W1J2Y5FR",
    "G7T8VK3Q4N",
    "H5R2LP9X6B",
    "D3Z8KV0Y1Q"
  ]
}
```
- Status: `200 OK`
- Body:
```
    N/A
```
**Nota:** Este método de validación de MFA puede devolver dos tipos de respuestas para `200 OK`dependiendo de la situación.
Cuando el usuario valida el código MFA por primera vez, la respuesta incluirá un conjunto de códigos de recuperación.
En las validaciones posteriores no incluirá un cuerpo de respuesta.

- Status: `400 Bad Request`
- Body:
```json
{
	"code": [
		"Código inválido"
	]
}
```
- Status: `400 Unauthorized`
- Body:
```json
{
	"detail": "Error en la petición"
}
```

### Desactivación de MFA

**Endpoint: POST /disable/**

**Description:**
Este método desactiva la autenticación de múltiples factores (MFA) para el usuario autenticado.

**Request:**
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`

- Body:
```json
{
	"code": "G7T8VK3Q4N"
}
```

**Response:**
- Status: `400 Bad Request`
- Body:
```json
{
	"code": [
		"Código inválido"
	]
}
```
- Status: `400 Bad Request`
- Body:
```json
{
	"detail": "Error en la petición"
}
```

### Activación de MFA

**Endpoint: POST /activate/**

**Descripción:**
Este endpoint activa la autenticación de múltiples factores (MFA) para un usuario que ha sido desactivada previamente.

**Request:**
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`

- Body:
```json
{
	"password": "password"
}
```

**Response:**
- Status: `400 Bad Request`
- Body:
```json
{
	"password": [
		"Contraseña inválida"
	]
}
```
- Status: `400 Bad Request`
- Body:
```json
{
	"detail": "Error en la petición"
}
```