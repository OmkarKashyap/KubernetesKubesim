# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY distributedsystems.py /app/

RUN pip install flask

EXPOSE 5001

CMD ["python", "distributedsystems.py"]
