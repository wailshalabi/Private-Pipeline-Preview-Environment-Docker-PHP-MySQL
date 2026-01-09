FROM php:8.2-apache

# Enable PDO MySQL
RUN docker-php-ext-install pdo pdo_mysql

# Apache: enable rewrite if you later need it
RUN a2enmod rewrite

WORKDIR /var/www/html
COPY app/ /var/www/html/

# Simple health endpoint could be added later
