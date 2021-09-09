FROM python:3

ENV FLASK_APP buscamed.py
ENV FLASK_CONFIG docker

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /home/buscamed

COPY requirements requirements
RUN /venv/bin/pip install -r requirements/docker.txt

ENV TZ 'America/Sao_Paulo'
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY app app
COPY migrations migrations
COPY scraper scraper
COPY buscamed.py config.py boot.sh .env scrapy.cfg ./
RUN chmod +x boot.sh

ENTRYPOINT ["./boot.sh"]
