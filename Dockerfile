FROM python:latest

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
# RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip install -r /requirements.txt
# RUN apk del .tmp

RUN mkdir /app
COPY ./app /app
COPY ./db/db.json /app
WORKDIR /app

COPY ./scripts /scripts
RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN mkdir -p /vol/socket

# RUN adduser user
# RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
# RUN chown user:user /app/db.sqlite3
# USER user

CMD ["entrypoint.sh"]
