# PadelPlay App

**PadelPlay** es una aplicación web y móvil diseñada para gestionar reservas de canchas de pádel, torneos, partidos y más, con una experiencia fluida y adaptable tanto para jugadores como para clubes.

---

## Tecnologías

### Frontend
- **Quasar Framework** (Vue.js):
  - Componentes dinámicos y responsivos.
  - Diseño optimizado para dispositivos móviles y escritorio.
  - Estilo personalizado con un tema oscuro.

### Backend
- **FastAPI**:
  - Endpoints para gestionar usuarios, reservas, partidos y torneos.
  - Integración con Supabase para el manejo de la base de datos.
  - Autenticación segura con JWT.

### Base de Datos
- **Supabase (PostgreSQL)**:
  - Tablas para usuarios, clubes, canchas, reservas, torneos y partidos.
  - Relación entre las tablas para un acceso eficiente a los datos.

---

## Funcionalidades Implementadas

### 1. **Inicio de Sesión y Registro**
- Autenticación JWT para usuarios.
- Roles de usuario: jugador, club, administrador.
- Integración con Supabase para almacenar información de usuario.

### 2. **Gestión de Canchas**
- Los clubes pueden:
  - Añadir y gestionar canchas.
  - Definir horarios disponibles y precios.

### 3. **Reservas**
- Los jugadores pueden:
  - Reservar canchas disponibles.
  - Ver disponibilidad basada en día y hora.
- Función de bloqueo de canchas por mantenimiento o eventos privados.

### 4. **Partidos**
- Creación automática de un partido al realizar una reserva.
- Asignación de jugadores a equipos (Equipo 1 y Equipo 2).
- Visualización de la cancha con jugadores y botones de "Añadir".
- Registro de resultados de los partidos, limitado a puntajes de 0 a 7 por set.

### 5. **Eventos**
- Sección de "Mis Eventos" para jugadores:
  - Lista de próximos partidos en formato de tarjetas desplazables.
  - Indicador de tipo de evento: partido o torneo.

### 6. **Página de Error 404**
- Página personalizada con el tema de pádel.
- Animación de una pelota de pádel con mensaje divertido.

---

## Estructura del Proyecto

### Frontend
- **Componentes principales:**
  - `DashboardPlayer.vue`: Vista principal del jugador con opciones como "Reservar una cancha" y "Mis Eventos".
  - `MatchDetails.vue`: Detalles del partido, gestión de jugadores y resultados.
  - `PageNotFound.vue`: Página para rutas inexistentes.

### Backend
- **Endpoints clave:**
  - `/reservations`: Gestión de reservas y verificación de disponibilidad.
  - `/matches`: Información de partidos, incluyendo jugadores, resultados y detalles del club/cancha.
  - `/clubs`: Gestión de información de clubes, canchas y horarios.

### Base de Datos
- **Tablas principales:**
  - `users`: Información de los usuarios.
  - `clubs`: Información de los clubes.
  - `courts`: Canchas gestionadas por los clubes.
  - `reservations`: Reservas realizadas por los jugadores.
  - `matches`: Partidos generados automáticamente al reservar.

---

## Instrucciones de Instalación

### Requisitos Previos
1. Node.js (versión 20 o superior).
2. Python (versión 3.10 o superior).
3. Supabase configurado con las tablas mencionadas.
4. Docker (opcional para contenedores).

### Configuración
1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu_usuario/padelplay.git
   cd padelplay
   ```

2. **Instalar dependencias del frontend:**
   ```bash
   cd frontend
   npm install
   ```

3. **Configurar variables de entorno:**
   - Crear un archivo `.env` en el backend con las claves necesarias:
     ```env
     SUPABASE_URL=<url_supabase>
     SUPABASE_KEY=<clave_anonima>
     JWT_SECRET=<clave_secreta>
     ```

4. **Levantar el servidor del backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

5. **Iniciar el frontend:**
   ```bash
   cd frontend
   quasar dev
   ```

---

## Próximos Pasos
1. **Torneos:**
   - Creación y gestión de torneos.
   - Generación automática de cuadros de juego.

2. **Integración de Pago:**
   - Implementar pasarela de pago para reservas y torneos.

3. **Notificaciones:**
   - Alertas en tiempo real para eventos, partidos y cambios en reservas.

4. **Optimización del Diseño:**
   - Mejorar la experiencia de usuario en dispositivos móviles.

---

## Contribuciones
Si deseas contribuir al proyecto, ¡eres bienvenido! Abre un issue o envía un pull request con tu propuesta.

---

**Contacto:**
Para dudas o sugerencias, por favor envía un correo a: [contacto@padelplay.com](mailto:contacto@padelplay.com).

