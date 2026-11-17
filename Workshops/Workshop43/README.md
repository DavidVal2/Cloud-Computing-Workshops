# Workshop 3 — Despliegue

El Compose publica únicamente Nginx en el puerto 80; Flask queda accesible en la red interna de Compose. `/` informa el hostname del contenedor, el valor `EC2_HOSTNAME` configurado para el host y hora UTC. En EC2, establecer `EC2_HOSTNAME` con el resultado de `hostname`, instalar Docker y Compose según la distribución y permitir TCP/80 en el Security Group. Para probar localmente:

```bash
docker compose up -d --build
docker compose ps
curl http://localhost/health
curl http://localhost/
docker compose down
```

Flujo: Internet → Security Group (80) → EC2 → Docker → Nginx → Flask. El puerto del contenedor es 5000; el único puerto publicado del host en esta configuración es 80.
