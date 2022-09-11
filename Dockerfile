FROM python:3.10
ADD . /code
COPY .env /code
WORKDIR /code
RUN pip install -r requirements.txt