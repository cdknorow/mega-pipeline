FROM python:3.8-slim-buster

ENV PYENV_SHELL=/bin/bash
ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/mega-pipeline.json

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential ffmpeg && \
    mkdir -p /app && pip install pipenv

WORKDIR /app

ADD Pipfile Pipfile.lock /app/

RUN pipenv sync

ADD . /app

ENTRYPOINT ["/bin/bash"]

# Get into the pipenv shell
CMD ["-c", "pipenv shell"]