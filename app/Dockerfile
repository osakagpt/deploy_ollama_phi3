FROM python:3.12.3-bullseye

RUN apt-get update \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 467B942D3A79BD29 \
    && apt-get -y install lsb-release \
    && apt-get clean

COPY . /app
WORKDIR /app

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--reload"]
