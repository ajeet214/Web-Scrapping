FROM python:3

EXPOSE 8000

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD gunicorn -w 5 -b 0.0.0.0 main:app