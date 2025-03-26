FROM public.ecr.aws/unocha/python:3.13-stable

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apk add --no-cache \
    gdal-driver-parquet \
    gdal-tools \
    apk add --no-cache --virtual .build-deps \
    apache-arrow-dev \
    build-base \
    cmake \
    gdal-dev \
    geos-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /root/.cache

COPY app ./app

CMD ["python", "-m", "app"]
