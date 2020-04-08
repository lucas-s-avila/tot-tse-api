FROM python:3.6-alpine

COPY . /app

WORKDIR /app

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["main.py"]