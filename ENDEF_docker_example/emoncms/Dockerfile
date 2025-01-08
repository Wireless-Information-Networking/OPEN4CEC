FROM php:7.4-apache

RUN apt-get update && apt-get install -y git unzip \
    && docker-php-ext-install mysqli

WORKDIR /var/www/html

# Clonar el repositorio de emoncms
RUN git clone https://github.com/emoncms/emoncms.git .

EXPOSE 80
