# SIGEC – Sistema de Gestión y Seguimiento Contractual

SIGEC es un prototipo académico de un sistema web orientado a la gestión, seguimiento y control de información contractual. Permite administrar contratos, contratistas, pagos, documentos, novedades contractuales, alertas de vencimiento, usuarios y reportes desde una interfaz centralizada.

El proyecto fue desarrollado para la asignatura **Arquitectura de Software**, aplicando principios de modularidad, separación de responsabilidades, bajo acoplamiento, mantenibilidad y escalabilidad.

## Funcionalidades principales

- Autenticación de usuarios.
- Gestión de usuarios y roles.
- Gestión de contratistas.
- Registro, consulta, búsqueda, filtrado y actualización de contratos.
- Registro de pagos asociados a contratos.
- Carga y consulta de documentos contractuales.
- Registro y consulta de novedades contractuales.
- Generación automática de alertas por vencimiento de contratos.
- Panel principal con indicadores de seguimiento.
- Generación de reportes y exportación en formato CSV.
- Cola de tareas para procesamiento desacoplado de solicitudes de reportes.
- Control de acceso según los roles Administrador, Funcionario y Supervisor.

## Arquitectura

SIGEC utiliza una arquitectura web modular basada en Flask. La solución separa responsabilidades mediante controladores, modelos, repositorios, servicios, observadores, colas, plantillas y recursos estáticos.

La persistencia se gestiona mediante SQLAlchemy como ORM. En el entorno de desarrollo local se utiliza SQLite, mientras que el entorno desplegado en la nube utiliza PostgreSQL 18 para garantizar la persistencia de los datos entre despliegues.

El prototipo se encuentra desplegado en Render y utiliza Gunicorn como servidor WSGI. La conexión a PostgreSQL se configura mediante la variable de entorno `DATABASE_URL`.

## Patrones de diseño aplicados

### MVC (Model-View-Controller)

Se utiliza para separar la representación de los datos, la interfaz de usuario y el control de las solicitudes de la aplicación.

### Repository

Encapsula las operaciones de acceso a datos y reduce el acoplamiento entre la lógica de la aplicación y la persistencia.

### Observer

Se aplica al mecanismo de alertas contractuales. Cuando se evalúa un contrato próximo a vencer, el observador puede generar la información necesaria para registrar la alerta correspondiente.

### Queue-Based Load Leveling

El prototipo incluye una cola de tareas en memoria para desacoplar la solicitud de generación de reportes de su procesamiento.

Esta implementación tiene fines académicos y demostrativos. En un entorno productivo de mayor escala se utilizaría una cola persistente o administrada.

## Tecnologías utilizadas

- Python 3.9
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLAlchemy
- SQLite para desarrollo local
- PostgreSQL 18 para el entorno desplegado
- psycopg2-binary
- Gunicorn
- Render
- Bootstrap 5
- HTML y CSS
- Pytest

## Estructura principal

```text
SIGEC/
├── app/
│   ├── controllers/
│   ├── models/
│   ├── observers/
│   ├── queues/
│   ├── repositories/
│   ├── services/
│   ├── static/
│   └── templates/
├── instance/
├── tests/
├── .gitignore
├── inicializar_db.py
├── README.md
├── requirements.txt
└── run.py
```

## Instalación local

### 1. Crear un entorno virtual

```bash
python3 -m venv venv
```

### 2. Activar el entorno virtual

En macOS o Linux:

```bash
source venv/bin/activate
```

En Windows:

```bash
venv\Scripts\activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto y definir las siguientes variables:

```env
SECRET_KEY=una-clave-secreta
DATABASE_URL=URL-de-conexion-a-postgresql
```

El archivo `.env` no debe publicarse en el repositorio.

Para desarrollo local, si no se define `DATABASE_URL`, SIGEC utiliza SQLite automáticamente. En el entorno de Render, `DATABASE_URL` contiene la conexión a la base de datos PostgreSQL.

### 5. Inicializar la base de datos

```bash
python inicializar_db.py
```

Este proceso crea las tablas requeridas por SIGEC y los datos iniciales necesarios para el funcionamiento del prototipo.

### 6. Ejecutar SIGEC

```bash
python run.py
```

Luego acceder desde el navegador a la dirección indicada por Flask, normalmente:

```text
http://127.0.0.1:5000
```

## Pruebas automatizadas

Para ejecutar las pruebas:

```bash
python -m pytest tests/test_app.py -v
```

Actualmente el proyecto cuenta con **8 pruebas automatizadas estratégicas** relacionadas con:

- Creación de la aplicación.
- Protección de rutas mediante autenticación.
- Inicio de sesión con credenciales válidas.
- Rechazo de credenciales inválidas.
- Autorización y restricciones según roles.
- Funcionamiento del patrón Repository.
- Funcionamiento del patrón Observer.
- Funcionamiento de la cola de tareas.

Las **8 pruebas se ejecutan satisfactoriamente** en el entorno de desarrollo.

## Roles del sistema

- **Administrador:** acceso a la administración general del sistema, incluyendo usuarios y módulos operativos.
- **Funcionario:** gestión de contratistas, contratos, pagos, documentos, novedades, alertas y reportes según los permisos implementados.
- **Supervisor:** acceso de consulta a contratos, novedades y alertas, con restricciones sobre operaciones administrativas.

## Despliegue en la nube

SIGEC se encuentra desplegado en **Render**.

La arquitectura del entorno desplegado utiliza:

```text
Usuario
   ↓
Aplicación web SIGEC
   ↓
Gunicorn
   ↓
Flask
   ↓
SQLAlchemy
   ↓
PostgreSQL 18
```

La aplicación obtiene la cadena de conexión a PostgreSQL mediante la variable de entorno `DATABASE_URL`, evitando almacenar las credenciales de la base de datos directamente en el código fuente.

El proceso de despliegue ejecuta la inicialización de la base de datos y posteriormente inicia la aplicación mediante Gunicorn.

## Persistencia de datos

En desarrollo local, SIGEC puede utilizar SQLite.

En el entorno desplegado en Render se utiliza PostgreSQL 18 como sistema de gestión de base de datos persistente.

La persistencia fue verificada mediante una prueba de redeploy:

1. Se registró información de prueba en SIGEC.
2. Se realizó un nuevo despliegue del servicio.
3. Se volvió a acceder a la aplicación.
4. La información registrada permaneció almacenada correctamente.

Esta prueba permitió comprobar que los datos no dependen del sistema de archivos temporal de la instancia web.

## Estado del proyecto

SIGEC se encuentra en fase de **prototipo académico funcional desplegado en la nube**.

Actualmente dispone de:

- Arquitectura modular.
- Autenticación y autorización por roles.
- Gestión de información contractual.
- Persistencia mediante PostgreSQL.
- Alertas automáticas de vencimiento.
- Generación de reportes.
- Implementación de patrones de diseño.
- Pruebas automatizadas.
- Interfaz web responsive.
- Despliegue funcional en Render.

La cola de tareas utilizada por el patrón Queue-Based Load Leveling continúa siendo una implementación en memoria con fines académicos y demostrativos. En una implementación productiva de mayor escala podría reemplazarse por una solución de mensajería persistente o administrada.

## Autores

**Fabián Andrés Ariza**
**Diego Duran**  
**Ruth Duran**   
Ingeniería de Software  
Proyecto académico – Arquitectura de Software