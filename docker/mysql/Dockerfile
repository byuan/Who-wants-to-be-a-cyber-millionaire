FROM mysql:5.7

ADD static_import.sql /docker-entrypoint-initdb.d
ADD dynamic_import.sql /docker-entrypoint-initdb.d
ADD user_import.sql /docker-entrypoint-initdb.d

EXPOSE 3306
