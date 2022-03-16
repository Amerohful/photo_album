FROM python:3.9-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apk --update add libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl
RUN apk add jpeg-dev zlib-dev freetype-dev ffmpeg lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
COPY . /code/
CMD ./manage.py spectacular --file schema.yml