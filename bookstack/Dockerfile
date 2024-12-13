FROM lscr.io/linuxserver/bookstack:latest

RUN apk update && apk add --no-cache python3 py3-pip python3-dev mariadb-connector-c-dev build-base pkgconfig
RUN pip3 install sqlalchemy bcrypt beautifulsoup4 markdown mysql-connector-python redis rq requests pydantic --break-system-packages
COPY ./override /app/www/
ENTRYPOINT [ "/init" ]