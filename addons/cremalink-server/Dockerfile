ARG BUILD_ARCH
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base-python:3.13-alpine3.23


RUN apk add --no-cache --virtual .cremalink-build-deps git \
     && python -m venv /opt/venv \
     && /opt/venv/bin/pip install -U --no-cache-dir "cremalink @ git+https://github.com/Styx85/cremalink.git@a3dd2c5aeeacef5d0a907f515e03be2b4b1f17d7" \
     && apk del .cremalink-build-deps

WORKDIR /opt/cremalink

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
