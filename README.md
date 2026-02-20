# IngeniumCode-FDM

Plataforma Web Integral de Gestión para la Escuela de Fútbol Comunitaria Infantil "Francisco de Miranda".

Este repositorio contiene el código fuente del sistema de gestión, desarrollado con **Django** para el backend y **Tailwind CSS** para el diseño de la interfaz de usuario. 

## 🛠️ Stack Tecnológico y Versiones Exactas

Para garantizar la compatibilidad entre todos los miembros del equipo, el proyecto utiliza estrictamente las siguientes versiones:

**Backend (Python):**
* **Django:** `5.2.9` (Framework principal)
* **psycopg2-binary:** `2.9.11` (Adaptador para la base de datos PostgreSQL)
* **Pillow:** `12.0.0` (Procesamiento de imágenes)
* **python-dotenv:** `1.2.1` (Gestión de variables de entorno)
* **weasyprint:** `68.1` (Generación de documentos PDF)
* **asgiref:** `3.11.0`
* **sqlparse:** `0.5.4`
* **tzdata:** `2025.2`

**Frontend (Node.js):**
* **tailwindcss:** `^3.4.19` (Framework CSS utility-first)
* **postcss:** `^8.5.6` (Herramienta de transformación CSS)
* **autoprefixer:** `^10.4.24` (Para compatibilidad de navegadores)

## 🚀 Guía de Instalación Paso a Paso

### 1. Clonar el Repositorio
Abre tu terminal y clona el proyecto en tu máquina local:
```bash
git clone [https://github.com/Y4nn1s/IngeniumCode-FDM](https://github.com/Y4nn1s/IngeniumCode-FDM)
cd IngeniumCode-FDM

```

### 2. Configurar Variables de Entorno

El proyecto requiere variables de configuración locales (credenciales de base de datos, claves secretas, etc.).

1. Localiza el archivo `.env.example` en la raíz del proyecto.
2. Crea una copia de este archivo y renómbrala a `.env`.
3. Rellena los datos dentro de `.env` con tu usuario de base de datos PostgreSQL, contraseña, nombre de la base de datos y la clave secreta (Secret Key) de Django.

### 3. Configuración del Entorno Backend (Python)

Es obligatorio usar un entorno virtual para no crear conflictos con otros proyectos en tu sistema.

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual (Windows)
.\venv\Scripts\activate

# Activar el entorno virtual (Linux/macOS)
source venv/bin/activate

# Instalar los requisitos exactos del proyecto
pip install -r requirements.txt

```

### 4. Configuración del Entorno Frontend (Node.js)

Asegúrate de tener Node.js instalado (`node -v` y `npm -v`). Luego, instala las dependencias de Tailwind CSS:

```bash
# En la raíz del proyecto, instala los paquetes definidos en package.json
npm install

```

### 5. Base de Datos y Migraciones

Una vez configurado tu archivo `.env` con las credenciales de PostgreSQL, aplica las migraciones para estructurar la base de datos:

```bash
python manage.py migrate

```

*(Opcional)* Crea tu usuario administrador para acceder al panel de Django:

```bash
python manage.py createsuperuser

```

---

## 💻 Flujo de Trabajo y Ejecución Local

Para visualizar los cambios correctamente, **debes tener dos terminales abiertas y ejecutándose simultáneamente**:

**Terminal 1: Compilador de Tailwind CSS**
Tailwind necesita estar observando (`--watch`) los cambios en los archivos HTML para generar el archivo CSS final (`output.css`).

```bash
# Ejecuta el script definido en package.json
npm run build:css

```

*Nota: Deja esta terminal abierta. Si la cierras, los estilos nuevos no se aplicarán.*

**Terminal 2: Servidor de Django**
En una terminal diferente, asegúrate de tener tu entorno virtual activado y levanta el servidor:

```bash
# Activar entorno (si no lo está)
.\venv\Scripts\activate

# Iniciar servidor
python manage.py runserver

```

Abre tu navegador en `http://127.0.0.1:8000/` para ver la plataforma funcionando.
