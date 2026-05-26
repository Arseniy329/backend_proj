# Educational Center Management System (Backend)

## Overview
This project is a Django-based backend for managing educational centers, supporting branches, subjects, students, groups, lessons, subscriptions, and attendance. It is fully containerized and ready for production deployment.

---

## Quick Start (Docker Compose)

1. **Clone the repository:**
   ```sh
   git clone <https://github.com/Arseniy329/backend_proj>
   cd backend_proj
   ```

2. **Copy and configure environment variables:**
   - Create a `.env` file in `education_plat/` with the following variables:
     ```env
     DJANGO_SECRET_KEY= "django-insecure-etam6^fc@f!f_i+8m9ss0tu4(vp04#-4gkyge0$1gml)l)yy5^"
     DJANGO_DEBUG=False
     POSTGRES_DB=education_db
     POSTGRES_USER=education_user
     POSTGRES_PASSWORD=education_pass
     POSTGRES_HOST=db
     POSTGRES_PORT=5432
     ALLOWED_HOSTS=*
     ```

3. **Start all services (backend, frontend, db):**
   ```sh
   docker-compose up --build
   ```
   - The backend will be available at `http://localhost:8000/`
   - The frontend will be available at `http://localhost:3000/`

4. **Apply migrations:**
   ```sh
   docker-compose exec backend python manage.py migrate
   ```

5. **Create a superuser:**
   ```sh
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Run tests:**
   ```sh
   docker-compose exec backend python manage.py test
   ```

---

## API Documentation
- Swagger/OpenAPI: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- Raw schema: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

## Required Environment Variables
- `DJANGO_SECRET_KEY` — Django secret key
- `DJANGO_DEBUG` — Set to `False` in production
- `POSTGRES_DB` — PostgreSQL database name
- `POSTGRES_USER` — PostgreSQL user
- `POSTGRES_PASSWORD` — PostgreSQL password
- `POSTGRES_HOST` — Database host (should be `db` for Docker Compose)
- `POSTGRES_PORT` — Database port (default: 5432)
- `ALLOWED_HOSTS` — Allowed hosts for Django (e.g., `*` for local dev)

---

## Useful Commands
- **Migrate DB:**
  ```sh
  docker-compose exec backend python manage.py migrate
  ```
- **Create superuser:**
  ```sh
  docker-compose exec backend python manage.py createsuperuser
  ```
- **Run tests:**
  ```sh
  docker-compose exec backend python manage.py test
  ```
- **Collect static files:**
  ```sh
  docker-compose exec backend python manage.py collectstatic
  ```

---

## Notes
- After any model changes, always run migrations:
  ```sh
  docker-compose exec backend python manage.py makemigrations
  docker-compose exec backend python manage.py migrate
  ```
- For production, set strong values for all secrets and restrict `ALLOWED_HOSTS`.
- The frontend and backend containers are decoupled for flexibility.

---

## License
MIT
