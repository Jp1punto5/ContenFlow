# ContentFlow – API REST y MongoDB Atlas

## 1. Descripción del proyecto

ContentFlow es un proyecto desarrollado para la evaluación de Bases de Datos No Relacionales. Su objetivo es implementar una solución de almacenamiento y gestión de información utilizando MongoDB Atlas y una API REST desarrollada con Python y Flask.

El sistema permite consultar, registrar, actualizar y eliminar usuarios y publicaciones, incorporando validaciones de datos, control de integridad referencial y registro de actividad.

## 2. Tecnologías utilizadas

- **Base de datos:** MongoDB Atlas (M0).
- **Lenguaje:** Python.
- **Framework:** Flask.
- **Conector MongoDB:** PyMongo.
- **Variables de entorno:** python-dotenv.
- **Pruebas de API:** Postman.
- **Gestión de solicitudes entre orígenes (CORS):** Flask-CORS.

## 3. Estructura del proyecto

```text
ContentFlow/
├── app/
│   ├── database/
│   │   └── connection.py
│   ├── routes/
│   │   ├── publicaciones.py
│   │   └── usuarios.py
│   └── __init__.py
├── docs/
│   └── evidencias/
│       ├── 01_atlas/
│       ├── 02_importacion/
│       └── 03_validaciones/
|       └── 04_api_postman/
|   └── evidencia_logging_crud.png/
├── Postman/
│   └── API - ContentFlow.postman_collection.json
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## 4. Base de datos

La solución utiliza MongoDB Atlas con una base de datos denominada `contentflow`.

Se implementaron las siguientes colecciones:

- `usuarios`
- `publicaciones`
- `reacciones`
- `comentarios`
- `campanas`

Los datos fueron importados desde archivos JSON y posteriormente se realizaron transformaciones para convertir los campos de fecha a tipo Date.

También se realizaron validaciones de consistencia de datos y referencias entre colecciones.

## 5. Configuración del entorno

### Requisitos previos

- Python 3.10 o superior.
- Una cuenta de MongoDB Atlas.
- MongoDB Atlas con acceso de red y usuario de base de datos configurados.
- Postman para ejecutar las solicitudes de prueba.

### Clonar el repositorio

```bash
git https://github.com/Jp1punto5/ContenFlow
cd ContentFlow
```

### Crear entorno virtual

En Windows PowerShell:

```powershell
python -m venv venv
```

Activar el entorno:

```powershell
.\venv\Scripts\Activate.ps1
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## 6. Configuración de MongoDB Atlas

Crear un archivo `.env` en la raíz del proyecto utilizando como referencia `.env.example`.

Configurar las siguientes variables:

```env
MONGO_URI=mongodb+srv://USUARIO:CONTRASENA@CLUSTER/
MONGO_DB=contentflow
```

Reemplazar los valores de conexión por las credenciales correspondientes a la instancia de MongoDB Atlas.

**Importante:** el archivo `.env` contiene credenciales privadas y no debe compartirse ni subirse al repositorio.

## 7. Ejecución de la API

Con el entorno virtual activado y las variables de entorno configuradas, ejecutar:

```bash
python run.py
```

La API estará disponible en:

```text
http://127.0.0.1:5000
```

Para comprobar su funcionamiento, acceder a la ruta principal:

```text
GET http://127.0.0.1:5000/
```

## 8. Endpoints disponibles

### Usuarios

| Método | Endpoint                     | Descripción        |
|--------|------------------------------|--------------------|
| GET    | `/api/usuarios/`             | Listar usuarios    |
| GET    | `/api/usuarios/{usuario_id}` | Consultar usuario  |
| POST   | `/api/usuarios/`             | Crear usuario      |
| PUT    | `/api/usuarios/{usuario_id}` | Actualizar usuario |
| DELETE | `/api/usuarios/{usuario_id}` | Eliminar usuario   |

### Publicaciones

| Método | Endpoint                                  | Descripción            |
|--------|-------------------------------------------|------------------------|
| GET    | `/api/publicaciones/`                     | Listar publicaciones   |
| GET    | `/api/publicaciones/{publicacion_id}`     | Consultar publicación  |
| POST   | `/api/publicaciones/`                     | Crear publicación      |
| PUT    | `/api/publicaciones/{publicacion_id}`     | Actualizar publicación |
| DELETE | `/api/publicaciones/{publicacion_id}`     | Eliminar publicación   |

## 9. Validaciones y manejo de errores

La API incorpora validaciones para:

- Campos obligatorios.
- Formato ISO 8601 para fechas.
- Tipos de datos esperados.
- Existencia de usuarios asociados a publicaciones.
- Correos electrónicos duplicados.
- Restricciones de integridad referencial al eliminar registros.
- Estructura de listas de hashtags.

Se utilizan códigos HTTP para identificar los resultados de las operaciones, entre ellos:

- `200`: operación realizada correctamente.
- `201`: registro creado.
- `400`: solicitud o datos inválidos.
- `404`: recurso no encontrado.
- `409`: conflicto con los datos o relaciones existentes.
- `500`: error interno del servidor.

## 10. Registro de actividad

La aplicación implementa un sistema de logging que registra eventos y operaciones realizadas mediante la API.

El archivo `contentflow.log` almacena información sobre solicitudes HTTP, operaciones de creación y actualización, validaciones y errores.

Este registro permite realizar seguimiento y diagnóstico del comportamiento de la aplicación.

## 11. Pruebas con Postman

La carpeta `Postman/` contiene la colección exportada de solicitudes utilizadas para verificar el funcionamiento de los endpoints.

La colección incluye operaciones GET, POST, PUT y DELETE para las colecciones de usuarios y publicaciones, además de pruebas de validación y manejo de errores.

Para ejecutar las pruebas, iniciar primero la API y luego importar la colección en Postman.

## 12. Evidencias y documentación

La carpeta `docs/evidencias/` contiene capturas de pantalla y respaldos del proceso de implementación, configuración de MongoDB Atlas, importación de datos, validaciones y pruebas de funcionamiento.

---

**Proyecto académico – ContentFlow**  
Asignatura: Bases de Datos No Relacionales.