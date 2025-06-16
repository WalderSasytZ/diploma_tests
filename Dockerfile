FROM python:3.13-alpine as algorithm_1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash
SHELL ["/bin/bash", "-c"]
COPY services/algorithm_1 /app/algorithm_1
COPY services/common /app/common
ENV PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python", "algorithm_1/main.py"]


FROM python:3.13-alpine as message_generator
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash
SHELL ["/bin/bash", "-c"]
COPY services/message_generator /app/message_generator
COPY services/common /app/common
ENV PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python", "message_generator/main.py"]


FROM python:3.13-alpine as query_consumer
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash
SHELL ["/bin/bash", "-c"]
COPY services/algorithm_2/query_consumer /app/algorithm_2/query_consumer
COPY services/common /app/common
ENV PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python", "algorithm_2/query_consumer/main.py"]


FROM python:3.13-alpine as query_producer
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash
SHELL ["/bin/bash", "-c"]
COPY services/algorithm_2/query_producer /app/algorithm_2/query_producer
COPY services/common /app/common
ENV PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python", "algorithm_2/query_producer/main.py"]