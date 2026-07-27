# IngeniumCode-FDM

Plataforma Web Integral de Gestión para la Escuela de Fútbol Comunitaria Infantil "Francisco de Miranda".

Este repositorio contiene el código fuente del sistema de gestión, desarrollado con **Django** para el backend y **Tailwind CSS** para el diseño de la interfaz de usuario, integrado con Alpine.js y esbuild para el frontend.

---

## 🛠️ Stack Tecnológico y Versiones Exactas

Para garantizar la compatibilidad entre todos los miembros del equipo, el proyecto utiliza estrictamente las siguientes versiones:

**Backend (Python):**
* **Django:** `5.2.9` (Framework principal)
* **psycopg2-binary:** `2.9.11` (Adaptador para la base de datos PostgreSQL)
* **Pillow:** `12.0.0` (Procesamiento de imágenes)
* **python-dotenv:** `1.2.1` (Gestión de variables de entorno)
* **weasyprint:** `68.1` (Generación de documentos PDF)
* **django-ratelimit:** `4.1.0` (Protección contra fuerza bruta en login)
* **requests:** `2.33.1` (Cliente HTTP)
* **asgiref:** `3.11.0`
* **sqlparse:** `0.5.4`
* **tzdata:** `2025.2`
* **pytest:** `9.0.3` (Framework de pruebas automatizadas)
* **pytest-django:** `4.12.0` (Integración de pytest con Django)

**Frontend (Node.js):**
* **tailwindcss:** `^3.4.19` (Framework CSS utility-first)
* **postcss:** `^8.5.6` (Herramienta de transformación CSS)
* **autoprefixer:** `^10.4.24` (Para compatibilidad de navegadores)
* **alpinejs:** `^3.15.8` (Framework JS ligero para interactividad)
* **esbuild:** `^0.27.3` (Bundler de JavaScript)

---

## 📂 Estructura y Módulos del Proyecto

El sistema está organizado de manera modular en las siguientes aplicaciones de Django:

* **[accounts](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/accounts):** Autenticación de usuarios, registro público de representantes, decoradores de control de acceso por roles (RBAC) y registro de eventos en `logs/security.log`.
* **[administracion](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/administracion):** Configuración de periodos académicos, canchas, categorías, delegados, coordinadores y entrenadores.
* **[filiacion](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/filiacion):** Expedientes de representantes y atletas (ficha médica, documentos digitales, foto) y generación de fichas técnicas en formato PDF.
* **[deportivo](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/deportivo):** Registro de partidos, asistencia, estadísticas individuales de atletas, evaluaciones técnicas de entrenadores y evaluaciones psicosociales de coordinadores.
* **[finanzas](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/finanzas):** Control de mensualidades y becas, reporte de pagos para representantes, bandeja de validación en bolívares/dólares para Tesorería, actualización automática de tasa BCV y alertas a representantes vía Telegram.
* **[core](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/core):** Layout base, paneles compartidos, páginas de error e inicio, y compilación de recursos frontend (CSS/JS).
* **[logistica](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/logistica):** Carpeta reservada para la futura gestión de logística e inventarios (actualmente estructura inicial sin instalar).

---

## 🔐 Sistema de Autenticación y Control de Acceso (RBAC)

El control de accesos e interactividad se maneja a través de roles y grupos de Django mediante decoradores dedicados ([accounts/decorators.py](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/accounts/decorators.py)) y un procesador de contexto para templates ([accounts/context_processors.py](file:///c:/Users/yitur/Documents/UNETI/TRAYECTO%203/SEMESTRE%206%20%28Actual%29/Proyecto%20Sociotecnol%C3%B3gico%20III%20%28M2%29/IngeniumCode-FDM/accounts/context_processors.py)).

### Matriz de Roles y Accesos

| Rol / Grupo Django | Permisos Clave | Decorador Asociado |
|---|---|---|
| **Administrador / Superuser** | Acceso total a base de datos, Django Admin y configuraciones críticas. | *(Permitido por defecto)* |
| **Coordinador General** | Gestión completa de filiaciones (atletas y representantes), periodos, categorías y asignación de personal. | `@coord_general_required` |
| **Coordinador Deportivo** | Gestión de evaluaciones psicosociales, supervisión de categorías, asignación de entrenadores y partidos. | `@coord_deportivo_required` |
| **Tesorería** | Gestión contable, bandeja de validación de pagos e ingreso/actualización de la tasa cambiaria BCV. | `@tesoreria_required` |
| **Entrenador** | Control de asistencias de entrenamiento, evaluaciones técnicas y registro de estadísticas de partidos. | `@entrenador_required` |
| **Representante** | Portal de autogestión: Visualizar fichas y rendimiento de atletas asignados y reportar pagos de mensualidades. | `@representante_required` |

### Seguridad y Restricciones
* **Restricción de Acceso:** El formulario de login personalizado `StaffOnlyAuthenticationForm` bloquea a cualquier usuario que no pertenezca a un rol administrativo (`is_staff=True`) o que no tenga un perfil activo de `Representante` asociado.
* **Rate Limiting:** El endpoint `/login/` cuenta con rate-limiting mediante `django-ratelimit` configurado para un máximo de **5 intentos por minuto por IP** y **10 intentos por hora por username**.
* **Sesión:** Expiración de cookies de sesión establecida a las **8 horas** (`SESSION_COOKIE_AGE`).
* **Seguridad Inmutable:** Los eventos de logins, logouts e intentos fallidos se registran con IP en `logs/security.log`.

---

## 🚀 Guía de Instalación Paso a Paso

### 1. Clonar el Repositorio
Abre tu terminal y clona el proyecto en tu máquina local:
```bash
git clone https://github.com/Y4nn1s/IngeniumCode-FDM
cd IngeniumCode-FDM
```

### 2. Configurar Variables de Entorno
1. Localiza el archivo `.env.example` en la raíz del proyecto.
2. Crea una copia de este archivo y renómbrala a `.env`.
3. Rellena los datos dentro de `.env` con tu usuario de base de datos PostgreSQL, contraseña, nombre de la base de datos, clave secreta (Secret Key) de Django y el bot token de Telegram si es necesario.

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
Instala las dependencias necesarias de Tailwind CSS y esbuild:
```bash
# En la raíz del proyecto
npm install
```

### 5. Base de Datos y Migraciones
Aplica las migraciones para estructurar la base de datos en tu servidor local PostgreSQL:
```bash
python manage.py migrate
```

### 6. Crear Usuarios de Prueba
Crea el usuario administrador principal (Directiva):
```bash
python manage.py createsuperuser
# user: admin_fdm | password: <segura>
```

*(Opcional)* Para crear usuarios de prueba con perfiles y grupos de permisos correctos:

**Crear Entrenador de Prueba:**
```bash
# Abre la shell de Django
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('entrenador1', password='Entrena2026!', is_staff=True, first_name='Carlos', last_name='Coach')
grupo, _ = Group.objects.get_or_create(name='Entrenador')
user.groups.add(grupo)
print('Entrenador creado exitosamente')
"
```

**Crear Representante de Prueba (con perfil asociado):**
```bash
# Abre la shell de Django
python manage.py shell -c "
from django.contrib.auth.models import User
from filiacion.models import Representante
user = User.objects.create_user('22222222', email='rep1@test.com', password='Rep2026!', first_name='Juan', last_name='Perez')
Representante.objects.create(
    cedula_identidad='22222222',
    nombres='Juan',
    apellidos='Perez',
    telefono_principal='04121234567',
    direccion_habitacion='Direccion de prueba',
    correo_electronico='rep1@test.com',
    usuario=user
)
print('Representante y perfil creados exitosamente')
"
```

### 7. Compilar Assets Frontend
```bash
# Generar bundle de Alpine.js
npm run build:js

# Compilar Tailwind CSS (dejar corriendo en terminal aparte)
npm run build:css
```

---

## 💻 Flujo de Trabajo y Ejecución Local

Para visualizar los cambios correctamente, **debes tener dos terminales abiertas y ejecutándose simultáneamente**:

**Terminal 1: Compilador de Tailwind CSS**
Tailwind necesita estar observando (`--watch`) los cambios en los archivos HTML para generar el archivo CSS final (`output.css`).
```bash
npm run build:css
```

**Terminal 2: Servidor de Django**
En una terminal diferente, con el entorno virtual activado, levanta el servidor:
```bash
# Iniciar servidor
python manage.py runserver
```
Abre tu navegador en `http://127.0.0.1:8000/`.

---

## 🧪 Pruebas y QA (Quality Assurance)

El proyecto cuenta con una suite completa de pruebas automatizadas utilizando `pytest` para verificar el correcto funcionamiento del control de accesos, flujos deportivos y el módulo de finanzas.

### Ejecutar las Pruebas

```bash
# Ejecutar todas las pruebas del proyecto
pytest

# Ejecutar las pruebas reutilizando la base de datos (más rápido)
pytest --reuse-db

# Ejecutar únicamente las pruebas de integración
pytest -m integration

# Ejecutar únicamente las pruebas unitarias
pytest -m "not integration"
```

### Distribución de las Pruebas
* **Pruebas Unitarias (`**/tests.py`):** Validan el comportamiento aislado de validadores, modelos y formularios en cada aplicación de Django.
* **Pruebas de Integración (`tests_integration/`):**
  * `test_filtering_por_rol.py`: Verifica que las restricciones de seguridad (RBAC) y accesos prohibidos (403/429) funcionen según el rol del usuario logueado.
  * `test_flujo_evaluaciones.py`: Comprueba el registro de evaluaciones técnicas por entrenadores y psicosociales por coordinadores.
  * `test_flujo_pago_aprobacion.py` y `test_flujo_pago_rechazo.py`: Valida el flujo contable del reporte de mensualidades por representantes y su posterior validación en la bandeja de Tesorería.
  * `test_flujo_partido.py`: Verifica el registro de encuentros y actualización de estadísticas individuales del atleta.
  * `test_telegram_y_pdf.py`: Comprueba la integración con el API del Bot de Telegram y la generación correcta de reportes en formato PDF con `WeasyPrint`.

---

## 💰 Módulo de Pagos y Notificaciones de Finanzas

El sistema automatiza el cálculo de mensualidades de atletas y su equivalencia en bolívares según la tasa del Banco Central de Venezuela (BCV).

### Variables de entorno requeridas
- `TELEGRAM_BOT_TOKEN` — Token generado a través de @BotFather en Telegram.

### Comandos de Administración de Finanzas
```bash
# Generar mensualidades del mes actual para todos los atletas activos (idempotente)
python manage.py generar_mensualidades

# Generar mensualidades para un mes y año específicos
python manage.py generar_mensualidades --mes 4 --anio 2026

# Generar mensualidades con un monto específico base (ej. $20)
python manage.py generar_mensualidades --monto 20.00

# Actualizar tasa oficial BCV del día desde DolarAPI
python manage.py refrescar_tasa_bcv
# Se recomienda configurar una tarea cron/programada en producción (ej. todos los días a las 9:00 AM)
# Cron de producción: 0 9 * * * python manage.py refrescar_tasa_bcv
```

### Asociación de representante a Telegram
* **Opción manual:** El administrador puede ingresar el `chat_id` de Telegram directamente desde Django Admin → Representantes.
* **Opción webhook:** Permite configurar un webhook HTTPS público para recibir el comando `/start CEDULA` enviado por el representante al bot y asociar automáticamente su cuenta.

### Flujo Contable de Pagos
1. **Reporte:** El representante ingresa a `/finanzas/reportar/`, selecciona las mensualidades pendientes, detalla la referencia del pago móvil o transferencia y sube el comprobante.
2. **Revisión:** Un miembro del rol `Tesoreria` (o admin) inspecciona los reportes en `/finanzas/admin/bandeja/`. El sistema valida que el comprobante no sea un duplicado mediante hash SHA-256 e impide el doble uso de una referencia activa.
3. **Aprobación:** Al ingresar la tasa oficial y presionar aprobar, las mensualidades marcadas se guardan como pagadas, se calcula el monto equivalente en USD y se envía una notificación instantánea al representante vía Telegram.
4. **Rechazo:** Si el pago es inconsistente, se libera la mensualidad para nuevos reportes y se notifica la razón del rechazo al representante por Telegram.
