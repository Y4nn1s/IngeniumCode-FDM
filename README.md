# IngeniumCode-FDM
Plataforma Web Integral de Gestión para la Escuela de Fútbol Comunitaria Infantil "Francisco de Miranda".

Clonar este Repositorio:
git clone https://github.com/Y4nn1s/IngeniumCode-FDM

Archivo '.env.example'
Aquí se implementará la configuración local que cada quién debe colocar, dependiendo de su usuario de base de datos, el nombre de la misma, secret key local, etc.

Instalación de Requisitos (requirements.txt):
pip install -r requirements.txt

## Configuración de Frontend (Tailwind CSS)

Este proyecto utiliza [Tailwind CSS](https://tailwindcss.com/) para estilizar la interfaz de usuario. Tailwind CSS es un framework "utility-first" que genera un archivo CSS optimizado conteniendo solo las clases que realmente utilizas en tus plantillas HTML.

### Requisitos

Asegúrate de tener [Node.js](https://nodejs.org/) y [npm](https://www.npmjs.com/) instalados en tu sistema. Puedes verificarlo ejecutando `node -v` y `npm -v` en tu terminal.

### Instalación de Dependencias de Frontend

Antes de poder usar Tailwind CSS, necesitas instalar sus dependencias:

1.  Abre tu terminal en la raíz del proyecto.
2.  Ejecuta el siguiente comando para instalar las dependencias de Node.js:
    ```bash
    npm install
    ```

### Ejecutar Tailwind CSS en Modo Desarrollo

Para que los estilos de Tailwind CSS se apliquen en tu navegador, su compilador debe estar funcionando en segundo plano. Este proceso genera y actualiza automáticamente el archivo CSS final (`output.css`) cada vez que guardas cambios en tus plantillas HTML.

1.  Abre una nueva terminal en la raíz de tu proyecto (separada de la que usas para el servidor de Django).
2.  Ejecuta el siguiente comando:
    
    *npm run build:css*
    
    **¡Importante!** Deja esta terminal abierta y ejecutándose. Si la cierras, los estilos de Tailwind dejarán de actualizarse.

### Flujo de Trabajo de Desarrollo

Para ver los cambios de tu interfaz con Tailwind CSS:

1.  Abre una terminal y ejecuta el compilador de Tailwind CSS:
    
    *npm run build:css*
    
2.  En otra terminal **diferente**, activa tu entorno virtual e inicia el servidor de Django:
    
    # Activa tu entorno virtual (ej. en Windows)
    *.\venv\Scripts\activate*
    # Inicia el servidor de Django
    *python manage.py runserver*
    
3.  Abre tu navegador y navega a `http://127.0.0.1:8000/`. Refresca la página para ver los cambios.

