FROM ubuntu:21.04
ARG DEBIAN_FRONTEND=noninteractive 
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip 
WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY * /app/
CMD ["flask", "run"]