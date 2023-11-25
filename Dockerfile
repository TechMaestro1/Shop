FROM python:3.11

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

RUN chmod +x ./start.sh
CMD ["/bin/bash", "/app/start.sh"]