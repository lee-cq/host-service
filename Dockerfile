#

ARG image_version=3.11-alpine

FROM python:${image_version}

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime  \
    && apt-get update --yes \
    && apt-get install --no-install-recommends --yes \
        iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD  ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]