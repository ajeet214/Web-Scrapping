FROM python:3

EXPOSE 8000

#RUN apt-get -y update
#RUN apt-get install -y --fix-missing \
#    build-essential \
#    cmake \
#    && apt-get clean; rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/*
RUN mkdir /app
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD gunicorn -w 5 -t 120 -b 0.0.0.0 main:app