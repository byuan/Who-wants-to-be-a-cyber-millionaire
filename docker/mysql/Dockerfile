FROM mariadb:11.4

COPY static_import.sql /docker-entrypoint-initdb.d/01-static.sql
COPY user_import.sql /docker-entrypoint-initdb.d/02-users.sql

EXPOSE 3306
