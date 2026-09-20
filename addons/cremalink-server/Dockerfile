ARG BUILD_ARCH
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base-python:3.13-alpine3.23


RUN apk add --no-cache --virtual .cremalink-build-deps git \
     && python -m venv /opt/venv \
     && /opt/venv/bin/pip install -U --no-cache-dir "cremalink @ git+https://github.com/Styx85/cremalink.git@71c68faf8df8a17c7516661480b9326160057abd" \
     && apk del .cremalink-build-deps

WORKDIR /opt/cremalink

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
