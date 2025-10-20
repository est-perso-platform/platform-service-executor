FROM --platform=linux/amd64 python:3.12-slim-trixie@sha256:dc9e92fcdc085ad86dda976f4cfc58856dba33a438a16db37ff00151b285c8ca

ENV TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 

RUN --mount=type=cache,target=/tmp/pip \
    PIP_CACHE_DIR=/tmp/pip \
    /usr/local/bin/python -m pip install \
        "fastapi[standard]==0.119.0" \
        "httpx[http2]==0.28.1" \
        "uvicorn[standard]==0.37.0" 

WORKDIR /app

COPY ./src /app

ENTRYPOINT [ "/bin/sh", "/app/docker-entrypoint.sh" ]
