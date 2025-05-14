FROM ubuntu:latest@sha256:6015f66923d7afbc53558d7ccffd325d43b4e249f41a6e93eef074c9505d2233


RUN apt-get update && apt-get install -y --no-install-recommends \
    cron wget make build-essential libreadline-dev libncursesw5-dev \
    libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
    libffi-dev zlib1g-dev python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tar.xz && \
    tar -xvf Python-3.13.3.tar.xz && \
    cd Python-3.13.3 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && rm -rf Python-3.13.3 Python-3.13.3.tar.xz

RUN python3 -m venv /venv


COPY cronconfig.txt .
COPY SpiderINMET__DOCKER.py .
COPY Logger.py .
COPY requirements.txt .

ENV WEBDRIVER_HOST='http://localhost:4444/wd/hub'
ENV DB_HOST='34.39.143.242'
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_DATABASE=postgres
ENV DB_PASSWORD=atmos2025
RUN set -e; \
    { \
      echo "WEBDRIVER_HOST=${WEBDRIVER_HOST}"; \
      echo "DB_HOST=${DB_HOST}"; \
      echo "DB_PORT=${DB_PORT}"; \
      echo "DB_USER=${DB_USER}"; \
      echo "DB_DATABASE=${DB_DATABASE}"; \
      echo "DB_PASSWORD=${DB_PASSWORD}\n"; \
      cat cronconfig.txt; \
    } > /etc/cron.d/cronconfig
RUN chmod 0644 /etc/cron.d/cronconfig && \
    crontab -u root /etc/cron.d/cronconfig && \
    touch /var/log/cron.log


RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]