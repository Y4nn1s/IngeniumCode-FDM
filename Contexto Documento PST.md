# CONTEXTO DEL PROYECTO DE GRADO: SISTEMA DE GESTIÓN "FRANCISCO DE MIRANDA"

## 1. IDENTIFICACIÓN DEL PROYECTO
* [cite_start]**Institución:** Universidad Nacional Experimental de Telecomunicaciones e Informática (UNETI)[cite: 1].
* [cite_start]**Programa:** Programa Nacional de Formación en Informática[cite: 1].
* [cite_start]**Título del Trabajo:** Desarrollo de plataforma web integral, orientada a la gestión deportiva, administrativa y comunicacional de la Escuela Comunitaria de Fútbol Infantil "Francisco de Miranda"[cite: 1].
* [cite_start]**Propósito:** Trabajo Especial como Requisito para Optar al Certificado de Desarrollador de Software[cite: 1].
* [cite_start]**Docente Asesora:** María Herrera[cite: 1].
* **Equipo de Desarrollo (Participantes):**
    * [cite_start]**Albert Hernández** Rol: Product Owner y Desarrollador[cite: 1, 42, 45].
    * [cite_start]**Alcides Mata** Rol: Scrum Master y Desarrollador[cite: 1, 44, 45].
    * [cite_start]**Yannis Iturriago** Rol: Desarrollador[cite: 1, 45].

---

## 2. DESCRIPCIÓN DEL PROBLEMA (DIAGNÓSTICO)
* [cite_start]**Ubicación:** Escuela de Fútbol Infantil Comunitaria "Francisco de Miranda", Parroquia Raúl Leoni, Maracaibo (conocida como "Escuela Los Angelitos")[cite: 11].
* [cite_start]**Población Afectada:** Matrícula de 124 niños (edades 3-15 años) divididos en 6 categorías[cite: 11].
* **Situación Actual:**
    * [cite_start]La gestión depende de procesos manuales y de un servicio alquilado externo[cite: 12].
    * [cite_start]El servicio externo tiene limitaciones funcionales, poca flexibilidad y costos que impactan el presupuesto[cite: 12].
    * [cite_start]No existen estadísticas verificables (minutos jugados, goles, asistencias, evolución física)[cite: 12].
* [cite_start]**Consecuencias:** Imposibilidad de generar Fichas Técnicas profesionales, lo que cierra puertas a financiamientos, patrocinios y becas deportivas, limitando la participación a torneos locales de bajo impacto[cite: 12].
* [cite_start]**Necesidad Detectada:** Migración hacia una solución tecnológica soberana (Software Libre), eficiente y escalable[cite: 14].

---

## 3. JUSTIFICACIÓN DEL PROYECTO
### 3.1. Justificación Social
* [cite_start]Democratización del uso de tecnología en sectores comunitarios[cite: 14].
* [cite_start]Empoderamiento de la organización para funcionar con estándares de academia privada bajo un modelo social[cite: 14].
* [cite_start]Mejora la calidad de servicio para 134 niños y sus familias, otorgando respaldo digital de la carrera deportiva para movilidad social[cite: 14].

### 3.2. Justificación Tecnológica
* [cite_start]Implementación de Software Libre para garantizar soberanía tecnológica[cite: 15].
* [cite_start]Eliminación de costos por licenciamiento[cite: 15].
* [cite_start]Demostración de viabilidad de tecnologías de vanguardia (Python/Django) en problemas comunitarios[cite: 15].

### 3.3. Vinculación Legal (Marco Jurídico)
* [cite_start]**Plan de la Patria 2019-2025:** Objetivo Histórico N° 1 ("Independencia Nacional" y soberanía tecnológica)[cite: 16, 32].
* [cite_start]**Constitución (CRBV):** Artículo 110 (Interés público de la ciencia y tecnología)[cite: 16, 31].
* [cite_start]**Ley de Infogobierno:** Obligación de usar Tecnologías de Información Libres y estándares abiertos[cite: 16, 33].
* [cite_start]**LOCTI:** Democratización del conocimiento e innovación tecnológica desde las bases sociales[cite: 34].
* **LOPNNA (Protección del Niño):** Artículo 65 (Derecho al Honor, Reputación y Propia Imagen). [cite_start]El software debe tener estrictas medidas de seguridad dado el manejo de datos sensibles de menores[cite: 35].

---

## 4. ANTECEDENTES DE LA INVESTIGACIÓN
### 4.1. Ámbito Nacional
* [cite_start]**Rodríguez y Bello (2004):** Resaltaron el valor de plataformas digitales para visibilidad institucional y procesos administrativos[cite: 17].
* [cite_start]**Universidad Monteávila (2015):** Proyectos educativos comunitarios con soluciones digitales[cite: 17].
* [cite_start]**UCAB - CEPYG (2018):** Iniciativas de intervención comunitaria con soporte web para comunicación y control administrativo[cite: 17].

### 4.2. Ámbito Internacional
* [cite_start]**FIFA / UNESCO (Football for Schools, 2020):** Integración de plataformas digitales para administración y estadísticas en escuelas[cite: 18].
* [cite_start]**PNUD (Valores a la Cancha, 2012):** Uso del deporte y recursos digitales para inclusión social[cite: 18].

---

## 5. OBJETIVOS
### 5.1. Objetivo General
[cite_start]Desarrollar una plataforma web integral orientada a la gestión deportiva, administrativa y comunicacional de la Escuela "Francisco de Miranda"[cite: 19].

### 5.2. Objetivos Específicos
1.  [cite_start]**Diagnosticar:** Situación actual de procesos y requisitos funcionales (Historias de Usuario)[cite: 19].
2.  [cite_start]**Diseñar:** Arquitectura web y modelo de base de datos relacional (atletas, representantes, estadísticas)[cite: 19].
3.  [cite_start]**Construir:** Plataforma web con módulos de expedientes, partidos y fichas técnicas usando Django[cite: 20].
4.  [cite_start]**Validar:** Pruebas de aceptación y capacitación al personal[cite: 21].

---

## 6. MARCO REFERENCIAL Y METODOLÓGICO
### 6.1. Metodología de Investigación
* [cite_start]**Tipo:** Investigación-Acción Participativa (IAP)[cite: 36].
* [cite_start]**Nivel:** Descriptiva y Proyectiva[cite: 36].
* [cite_start]**Población:** 134 atletas, 4 entrenadores, 1 coordinador, 1 presidenta, 6 delegados, 2 mantenimiento[cite: 37].
* [cite_start]**Muestra (Intencional):** 1 Coordinador, 2 Entrenadores, 6 Delegados, 15 Jugadores[cite: 38].
* [cite_start]**Técnicas:** Observación Directa, Entrevista Semiestructurada, Encuesta, Revisión Documental[cite: 39, 40].

### 6.2. Metodología de Desarrollo: SCRUM
* [cite_start]**Justificación:** Necesidad de entregas incrementales y validación constante[cite: 23, 41].
* **Roles:**
    * [cite_start]*Product Owner:* Albert Hernández (Define prioridades y valida)[cite: 42].
    * [cite_start]*Scrum Master:* Alcides Mata (Facilita y elimina obstáculos)[cite: 44].
    * [cite_start]*Equipo Dev:* Hernández, Mata, Iturriago (Arquitectura, BD, Programación)[cite: 45].
* [cite_start]**Artefactos:** Product Backlog (Inventario), Sprint Backlog (Tareas), Incremento[cite: 46].
* [cite_start]**Definition of Done (DoD):** Código bajo estándar PEP-8, funcionalidad probada sin errores, validación del Product Owner y aprobación comunitaria[cite: 47].

---

## 7. ESPECIFICACIONES TÉCNICAS (STACK TECNOLÓGICO)
### 7.1. Software
* [cite_start]**Lenguaje:** Python (Seleccionado por legibilidad y potencia en datos)[cite: 54].
* [cite_start]**Framework Web:** Django (Arquitectura MVT, seguridad robusta, baterías incluidas, principio DRY)[cite: 25, 55].
* [cite_start]**Base de Datos:** PostgreSQL (Relacional, integridad referencial, código abierto)[cite: 30, 55].
* [cite_start]**Frontend:** HTML5, CSS3, Framework Tailwind (Diseño adaptativo/Responsive)[cite: 55].
* [cite_start]**Control de Versiones:** Git y GitHub[cite: 55].
* [cite_start]**IDE:** Antigravity de Google (Fork de Visual Studio Code)[cite: 55].
* [cite_start]**Generación de PDF:** Librería WeasyPrint[cite: 53].

### 7.2. Hardware de Desarrollo (Entorno Local requerido mínimo)
* [cite_start]**Equipo:** Computadora Portátil[cite: 56].
* [cite_start]**Procesador:** Intel Core i3 / AMD Ryzen 3 (o superior)[cite: 56].
* [cite_start]**RAM:** 8 GB[cite: 56].
* [cite_start]**Almacenamiento:** SSD 240 GB[cite: 56].
* [cite_start]**Sistema Operativo:** Windows 10 / Linux Ubuntu[cite: 56].

### 7.3. Arquitectura del Sistema (MVT)
* [cite_start]**Modelo (Datos):** Estructura lógica en BD gestionada por ORM de Django (seguridad ante inyecciones SQL)[cite: 25].
* [cite_start]**Vista (Lógica):** Procesa solicitudes y lógica de negocio[cite: 26].
* [cite_start]**Template (Interfaz):** Capa de presentación (HTML/CSS)[cite: 26].

---

## 8. REQUISITOS DEL SISTEMA
### 8.1. Funcionales (Historias de Usuario)
1.  [cite_start]**Gestión de Atletas:** Registrar, consultar, editar y deshabilitar (datos personales, fotos, peso, altura)[cite: 49].
2.  [cite_start]**Ficha Técnica:** Generación automática de PDF descargable con perfil para patrocinantes[cite: 50].
3.  [cite_start]**Gestión de Partidos:** Registrar encuentros y asociar estadísticas individuales (minutos, goles)[cite: 50].
4.  [cite_start]**Control de Categorías:** Validación automática según año de nacimiento (Sub-5 a Sub-15)[cite: 51].

### 8.2. No Funcionales
* [cite_start]**Usabilidad:** Responsive (adaptable a móviles para uso en cancha)[cite: 51].
* [cite_start]**Seguridad:** Control de acceso por roles (Admin/Entrenador) y encriptación PBKDF2[cite: 51].
* [cite_start]**Rendimiento:** Generación de reportes PDF < 3 segundos[cite: 51].

---

## 9. FASES DE EJECUCIÓN Y TRANSFERENCIA
1.  [cite_start]**Diagnóstico (Sprint 0):** Levantamiento de info y configuración de entorno[cite: 52].
2.  [cite_start]**Diseño (Sprint 1):** Diagrama Entidad-Relación (DER) y Wireframes[cite: 53]. Planificación e implementación del primer prototipo.
3.  [cite_start]**Construcción:** Backend Django (MVT) e integración de WeasyPrint[cite: 53]. Planificación e implementación del segundo prototipo.
4.  [cite_start]**Validación:** Pruebas UAT (Acceptance Testing) y Caja Negra[cite: 53].

### Protocolo de Capacitación (Transferencia Tecnológica)
* **Sesión 1 (Administrativa):** 2 horas. [cite_start]Temas: Registro de atletas y generación de fichas[cite: 56].
* **Sesión 2 (Deportiva):** 2 horas. [cite_start]Temas: Carga de partidos y estadísticas desde móviles[cite: 56].
* [cite_start]**Material de Apoyo:** Manual de Usuario Digital (PDF) y Guía de Preguntas Frecuentes[cite: 56].