#

FROM python:3.11

COPY . /app

RUN pip install -r requirements.txt \
    && pip install -r requirements-dev.txt \

WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]