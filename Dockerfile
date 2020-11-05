FROM python:3.8-buster

RUN pip install pipenv

RUN useradd -ms /bin/bash flask
USER flask

WORKDIR /app
COPY Pipfile* /app/
RUN pipenv install

USER root
RUN mkdir -p /app/uploads \
    && mkdir -p /app/output_files \
    && mkdir -p /app/output_zip \
    && chown flask:flask /app/uploads /app/output_zip /app/output_files \
    && chmod 777 / /app
USER flask

COPY . /app

EXPOSE 5000

CMD ["pipenv", "run", "python", "app.py"]
