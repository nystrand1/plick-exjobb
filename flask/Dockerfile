FROM python:3.7-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY * /app/
CMD ["flask", "run"]