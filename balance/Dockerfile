FROM tiangolo/uwsgi-nginx:python3.8

ENV UWSGI_INI /application/uwsgi.ini
ENV LISTEN_PORT 8000

COPY . /application
RUN pip install -r /application/requirements.txt

EXPOSE 8000

WORKDIR /application
