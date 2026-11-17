# Sistema de seguimiento de equipos

## Construir la imagen

Desde `api/`:

```bash
docker build -t equipment-api:1.0 .
```

Para el despliegue en AWS, etiquetar esa imagen con la URI del repositorio `equipment-api` y publicarla en ECR desde el equipo de desarrollo. En EC2, definir `API_IMAGE` en `.env` con la URI ECR completa y descargarla con `docker compose pull`; el Compose usa `image:` y no construye el código fuente en EC2.

## Ejecutar localmente

Desde `cloud-equipment/`, copiar `.env.example` a `.env`, usar una contraseña local y ejecutar:

```bash
docker compose up -d
docker compose ps
curl http://localhost/health
curl http://localhost/empleados
```

Para Compose local, conservar `API_IMAGE=equipment-api:1.0` después de construir la imagen. PostgreSQL inicializa el esquema y los empleados de ejemplo en el volumen vacío. Los endpoints de escritura permiten probar empleados, equipos, asignación, mantenimiento e historial. Las cargas de documentos requieren `S3_BUCKET`, región y credenciales IAM disponibles para el proceso.

## API incluida

- `GET/POST /empleados`, `GET /empleados/{id}`
- `GET/POST /equipos`, `GET/PUT /equipos/{id}`
- `POST /equipos/{id}/asignar`
- `POST /equipos/{id}/mantenimientos`
- `GET /equipos/{id}/historial`
- `POST /equipos/{id}/documentos` con `multipart/form-data`, campo `file`
- `GET /health`

El Security Group de EC2 debe exponer HTTP/80 y SSH/22 solo a la red administrativa. PostgreSQL no publica puerto al host. No guardar credenciales reales en Git; en AWS, asignar un IAM Role con acceso mínimo a ECR y al bucket S3.
