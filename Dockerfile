FROM public.ecr.aws/unocha/python:3.12-stable

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY app ./app

RUN apk add --no-cache \
    py3-pyarrow && \
    apk add --no-cache --virtual .build-deps \
    build-base \
    gdal-dev \
    geos-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm -r /root/.cache

CMD ["python", "-m", "app"]
