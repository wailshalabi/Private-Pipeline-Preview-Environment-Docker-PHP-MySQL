FROM python:3.12-alpine

RUN apk add --no-cache docker-cli curl

WORKDIR /app
COPY app.py /app/app.py

EXPOSE 8081
CMD ["python", "/app/app.py"]
