FROM php:7.4-cli

WORKDIR /var/www/html

# Añadir cualquier configuración personalizada
RUN apt-get update && apt-get install -y curl

CMD ["php", "-S", "0.0.0.0:8000"]
EXPOSE 8000
