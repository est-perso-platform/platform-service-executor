FROM python:3.12-slim-trixie@sha256:dc9e92fcdc085ad86dda976f4cfc58856dba33a438a16db37ff00151b285c8ca

ENV TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 

RUN --mount=type=cache,target=/tmp/pip \
    --mount=type=bind,rw,source=./requirements.txt,target=/tmp/requirements.txt \
    PIP_CACHE_DIR=/tmp/pip \
    /usr/local/bin/python -m pip install \
        -r /tmp/requirements.txt

WORKDIR /app

COPY ./src /app

ENTRYPOINT [ "/bin/sh", "/app/docker-entrypoint.sh" ]
