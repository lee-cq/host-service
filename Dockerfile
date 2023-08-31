#

ARG image_version=3.11-alpine

FROM python:${image_version}

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt \
    && pip install -r requirements-dev.txt

CMD  ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]