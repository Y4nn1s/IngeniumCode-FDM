# Imagen base oficial de Python 3.13 slim (Debian bookworm)
FROM python:3.13-slim-bookworm

# Variables de entorno para Python en producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# Instalar dependencias del sistema necesarias para WeasyPrint
# y para psycopg2-binary (libpq) en una sola capa para optimizar tamaño
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Crear carpetas necesarias y asegurar permisos
RUN mkdir -p logs staticfiles media && \
    chmod -R 755 logs staticfiles media

# Ejecutar collectstatic durante el build
RUN python manage.py collectstatic --no-input

# Exponer el puerto que Render espera
EXPOSE 8000

# Comando de arranque: migraciones + gunicorn
# Las migraciones se ejecutan en runtime, no en build, porque DATABASE_URL
# solo está disponible en runtime cuando Render conecta la base de datos
CMD python manage.py migrate --no-input && \
    gunicorn project_gestion.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
