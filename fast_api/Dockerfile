# Dockerfile that builds the image that will be used to run the FastyAPI built
# to serve the trained model

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim AS base

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["python", "api.py"]