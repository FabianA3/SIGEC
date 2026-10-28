# SIGEC – Sistema de Gestión y Seguimiento Contractual

SIGEC es un prototipo académico de un sistema web orientado a la gestión, seguimiento y control de información contractual. Permite administrar contratos, contratistas, pagos, documentos, novedades contractuales, alertas de vencimiento, usuarios y reportes desde una interfaz centralizada.

El proyecto fue desarrollado para la asignatura **Arquitectura de Software**, aplicando principios de modularidad, separación de responsabilidades, bajo acoplamiento y mantenibilidad.

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

La persistencia local del prototipo se realiza mediante SQLite y SQLAlchemy como ORM.

## Patrones de diseño aplicados

### MVC (Model-View-Controller)

Se utiliza para separar la representación de los datos, la interfaz de usuario y el control de las solicitudes de la aplicación.

### Repository

Encapsula operaciones de acceso a datos y reduce el acoplamiento entre la lógica de la aplicación y la persistencia.

### Observer

Se aplica al mecanismo de alertas contractuales. Cuando se evalúa un contrato próximo a vencer, el observador puede generar la información necesaria para registrar la alerta correspondiente.

### Queue-Based Load Leveling

El prototipo incluye una cola de tareas en memoria para desacoplar la solicitud de generación de reportes de su procesamiento. Esta implementación tiene fines académicos y demostrativos; en un entorno productivo se utilizaría una cola persistente o administrada.

## Tecnologías utilizadas

- Python 3.9
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLAlchemy
- SQLite
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

Crear un archivo `.env` en la raíz del proyecto y definir una clave secreta:

```env
SECRET_KEY=una-clave-secreta
```

El archivo `.env` no debe publicarse en el repositorio.

### 5. Ejecutar SIGEC

```bash
python run.py
```

Luego acceder desde el navegador a la dirección indicada por Flask, normalmente `http://127.0.0.1:5000`.

## Pruebas automatizadas

Para ejecutar las pruebas:

```bash
python -m pytest tests/test_app.py -v
```

Actualmente el proyecto cuenta con pruebas estratégicas sobre creación de la aplicación, autenticación, autorización por roles, Repository, Observer y cola de tareas.

## Roles del sistema

- **Administrador:** acceso a la administración general del sistema, incluyendo usuarios y módulos operativos.
- **Funcionario:** gestión de contratistas, contratos, pagos, documentos, novedades, alertas y reportes según los permisos implementados.
- **Supervisor:** acceso de consulta a contratos, novedades y alertas, con restricciones sobre operaciones administrativas.

## Estado del proyecto

SIGEC se encuentra en fase de prototipo académico funcional. La versión actual utiliza SQLite y una cola de tareas en memoria para ejecución local. La arquitectura está preparada para continuar su adaptación a un entorno de despliegue en la nube.

## Autor

**Fabián Andrés Ariza**  
Ingeniería de Software  
Proyecto académico – Arquitectura de Software